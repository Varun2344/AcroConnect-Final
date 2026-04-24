import os
import logging
import importlib

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

# module logger
logger = logging.getLogger(__name__)

from .models import (
    CustomUser,
    StudentProfile,
    Skill,
    JobPosting,
    Roadmap,
    StudentSkillSet,
)
from .serializers import (
    CustomUserSerializer,
    CustomTokenObtainPairSerializer,
    StudentProfileSerializer,
    SkillSerializer,
    JobPostingSerializer,
    RoadmapSerializer,
    StudentSkillSetSerializer,
)


def build_fallback_roadmap(profile, skills_list, career_goal):
    """
    Deterministic fallback roadmap used when Gemini is unavailable.
    """
    skills_text = ", ".join(skills_list) if skills_list else "No skills added yet"
    semester = getattr(profile, "semester", 1) or 1
    tech_stack = (getattr(profile, "tech_stack", "") or "").strip() or "General software stack"
    target_role = career_goal if career_goal and career_goal.strip() else "Placement-ready Software Engineer"

    return f"""# Personalized Learning Roadmap (Fallback Mode)

**Student:** {profile.full_name}  
**Current Semester:** {semester}  
**CGPA:** {profile.cgpa}  
**Career Goal:** {target_role}  
**Current Skills:** {skills_text}  
**Preferred Tech Stack:** {tech_stack}

## Phase 1 (Weeks 1-4): Foundation
- Audit your profile, resume, and project portfolio.
- Practice coding fundamentals and DSA daily.
- Create a weekly schedule with revision checkpoints.

## Phase 2 (Weeks 5-8): Core Development
- Deepen one backend and one frontend stack.
- Build a mini project and deploy it.
- Strengthen interview theory: DBMS, OS, OOP, CN.

## Phase 3 (Weeks 9-12): Portfolio & Achievements
- Build one major project aligned to your target role.
- Add measurable outcomes in project documentation.
- Participate in hackathons/certifications and record achievements.

## Phase 4 (Weeks 13-16): Placement Readiness
- Prepare role-specific resume variants.
- Take weekly mock interviews (technical + HR).
- Track job applications and improve based on feedback.

## Weekly Checklist
- [ ] 10-15 coding questions
- [ ] 1 project/module update
- [ ] 1 mock interview
- [ ] Resume + LinkedIn refresh

_Generated in fallback mode because Gemini was unavailable or request failed in the current environment._
"""


def get_configured_gemini_client():
    """
    Resolve and configure Gemini client at request-time.
    Returns: (client_module_or_none, reason_or_none)
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None, "GEMINI_API_KEY is missing."

    try:
        genai = importlib.import_module("google.generativeai")
    except ImportError:
        return None, "google-generativeai package is not installed."

    try:
        genai.configure(api_key=api_key)
    except Exception as exc:
        return None, f"Gemini client configuration failed: {exc}"

    return genai, None


def get_gemini_runtime_config():
    """
    Runtime tuning for Gemini calls to avoid long request hangs.
    """
    timeout_sec = int(os.getenv("GEMINI_REQUEST_TIMEOUT_SEC", "15"))
    models_raw = os.getenv(
        "GEMINI_MODELS",
        "models/gemini-2.5-flash,models/gemini-flash-latest,models/gemini-2.0-flash,models/gemini-pro-latest",
    )
    raw_models = [m.strip() for m in models_raw.split(",") if m.strip()]
    if not raw_models:
        raw_models = ["models/gemini-2.5-flash"]

    # Accept both "gemini-*" and "models/gemini-*" forms.
    models_to_try = []
    for name in raw_models:
        if name.startswith("models/"):
            models_to_try.append(name)
            models_to_try.append(name.replace("models/", "", 1))
        else:
            models_to_try.append(name)
            models_to_try.append(f"models/{name}")

    # Preserve order while removing duplicates.
    deduped = []
    seen = set()
    for m in models_to_try:
        if m not in seen:
            seen.add(m)
            deduped.append(m)

    return timeout_sec, deduped


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # Restrict user listing to TPOs; regular users can only see themselves.
        if self.request.user.is_tpo:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=self.request.user.id)

    def perform_create(self, serializer):
        # Public registration should never create privileged users.
        serializer.save(is_tpo=False)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Get the current authenticated user's data.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]


class StudentSkillSetViewSet(viewsets.ModelViewSet):
    queryset = StudentSkillSet.objects.select_related("student_profile", "skill")
    serializer_class = StudentSkillSetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = StudentSkillSet.objects.select_related("student_profile", "skill")
        if self.request.user.is_tpo:
            return queryset
        return queryset.filter(student_profile__user=self.request.user)

    def perform_create(self, serializer):
        # Students can only create skill assignments for their own profile.
        if self.request.user.is_tpo:
            serializer.save()
            return
        profile, _ = StudentProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                "full_name": self.request.user.get_full_name() or self.request.user.username,
                "phone": "",
                "cgpa": 0.0,
            },
        )
        serializer.save(student_profile=profile)


class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.select_related("user").prefetch_related("student_skill_set__skill")
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = StudentProfile.objects.select_related("user").prefetch_related("student_skill_set__skill")
        if self.request.user.is_tpo:
            return queryset
        return queryset.filter(user=self.request.user)

    @action(detail=False, methods=["get", "patch"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Retrieve or update the authenticated student's profile.
        Automatically creates a profile if one is missing.
        """
        profile, _ = StudentProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "full_name": request.user.get_full_name() or request.user.username,
                "phone": "",
                "cgpa": 0.0,
            },
        )

        if request.method.lower() == "patch":
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.select_related("tpo_user").prefetch_related("required_skills_details__skill")
    serializer_class = JobPostingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = JobPosting.objects.select_related("tpo_user").prefetch_related("required_skills_details__skill")
        if self.request.user.is_tpo:
            return queryset
        return queryset.all()

    def perform_create(self, serializer):
        if not self.request.user.is_tpo:
            raise PermissionDenied("Only TPO users can create job postings.")
        serializer.save(tpo_user=self.request.user)

    def perform_update(self, serializer):
        if not self.request.user.is_tpo:
            raise PermissionDenied("Only TPO users can update job postings.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_tpo:
            raise PermissionDenied("Only TPO users can delete job postings.")
        instance.delete()


class RoadmapViewSet(viewsets.ModelViewSet):
    queryset = Roadmap.objects.select_related("profile", "profile__user")
    serializer_class = RoadmapSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Roadmap.objects.select_related("profile", "profile__user")
        if self.request.user.is_tpo:
            return queryset
        return queryset.filter(profile__user=self.request.user)


class GenerateRoadmapView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            profile = request.user.student_profile
        except StudentProfile.DoesNotExist:
            return Response(
                {"detail": "Student profile not found for the current user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Fetch student's skills from StudentSkillSet
        skill_assignments = profile.student_skill_set.select_related("skill").all()
        skills_list = []
        for assignment in skill_assignments:
            skill_name = assignment.skill.skill_name
            skill_level = assignment.skill_level
            skills_list.append(f"{skill_name}: {skill_level}/5")

        skills_text = ", ".join(skills_list) if skills_list else "No skills specified yet."

        # Fetch career goal from profile
        career_goal = profile.career_goal or "Not specified"

        # Keep prompt concise to reduce model timeout risk in free-tier environments.
        prompt = f"""Create a concise, practical student career roadmap in markdown.

Student profile:
- Name: {profile.full_name}
- CGPA: {profile.cgpa}
- Career goal: {career_goal}
- Skills: {skills_text}

Output format:
1) 16-week plan split into 4 phases (weeks 1-4, 5-8, 9-12, 13-16)
2) Weekly checklist (4 bullets)
3) Interview preparation plan
4) 5 immediate next actions

Keep it specific, action-oriented, and realistic."""

        genai, gemini_unavailable_reason = get_configured_gemini_client()
        if genai is None:
            logger.warning("Gemini unavailable, using fallback roadmap. Reason: %s", gemini_unavailable_reason)
            roadmap_text = build_fallback_roadmap(profile, skills_list, career_goal)
            roadmap = Roadmap.objects.create(profile=profile, roadmap_text=roadmap_text)
            serializer = RoadmapSerializer(roadmap)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        try:
            timeout_sec, models_to_try = get_gemini_runtime_config()
            # Try several likely models in order until one succeeds.
            # Some deployments do not expose every Gemini model name, so we attempt
            # a few candidates and fall back gracefully.
            # Prefer the models that are commonly available in modern Google GenAI
            # deployments (based on the output from list_models()).

            roadmap_text = None
            last_exception = None
            used_model = None

            for candidate in models_to_try:
                try:
                    model = genai.GenerativeModel(candidate)
                    response = model.generate_content(
                        prompt,
                        request_options={"timeout": timeout_sec, "retry": None},
                    )

                    # Prefer .text if available
                    if hasattr(response, "text") and response.text:
                        candidate_text = response.text
                    else:
                        candidate_text = str(response)

                    if candidate_text and candidate_text.strip():
                        roadmap_text = candidate_text
                        used_model = candidate
                        logger.info("GenerateRoadmap: using model candidate '%s'", candidate)
                        break
                except Exception as e:
                    # record and continue to next candidate
                    last_exception = e
                    continue

            if not roadmap_text:
                logger.warning(
                    "GenerateRoadmap: model attempts failed, using fallback. Last error: %s",
                    str(last_exception) if last_exception else "none",
                )
                roadmap_text = build_fallback_roadmap(profile, skills_list, career_goal)
            # Optionally annotate which model was used (for debugging) at the top
            # we do not prepend debug metadata to the saved roadmap text here;
            # model usage is logged via the logger for diagnostics.

        except Exception:
            logger.exception("Gemini generation raised exception, using fallback.")
            roadmap_text = build_fallback_roadmap(profile, skills_list, career_goal)

        # Save the roadmap
        roadmap = Roadmap.objects.create(profile=profile, roadmap_text=roadmap_text)
        serializer = RoadmapSerializer(roadmap)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token view that uses our serializer supporting username/email login.
    """
    serializer_class = CustomTokenObtainPairSerializer


class CurrentUserView(APIView):
    """
    API endpoint to get the current authenticated user's data.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)


class ListGenaiModelsView(APIView):
    """Return a list of available models from the configured google.generativeai client.

    This endpoint is useful for debugging model availability in environments
    where not all Gemini model names are exposed.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        genai, gemini_unavailable_reason = get_configured_gemini_client()
        if genai is None:
            return Response(
                {"detail": f"Gemini API unavailable: {gemini_unavailable_reason}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            # Prefer a direct list_models() call if available
            models_raw = None
            if hasattr(genai, "list_models"):
                models_raw = genai.list_models()
            else:
                # Fallback: attempt to inspect common attributes
                models_raw = None

            model_names = []
            if models_raw is None:
                return Response({"detail": "The installed google-generativeai library does not expose a list_models() helper."}, status=status.HTTP_501_NOT_IMPLEMENTED)

            # Normalize common return shapes
            if isinstance(models_raw, (list, tuple)):
                for m in models_raw:
                    if isinstance(m, str):
                        model_names.append(m)
                    elif isinstance(m, dict):
                        name = m.get("name") or m.get("model") or m.get("id")
                        if name:
                            model_names.append(name)
                    else:
                        name = getattr(m, "name", None) or getattr(m, "model", None)
                        if name:
                            model_names.append(name)
            else:
                # Some clients return objects with a .models attribute
                if hasattr(models_raw, "models"):
                    for m in models_raw.models:
                        name = getattr(m, "name", None) or getattr(m, "model", None) or (m.get("name") if isinstance(m, dict) else None)
                        if name:
                            model_names.append(name)

            return Response({"available_models": model_names})

        except Exception as e:
            import traceback

            traceback.print_exc()
            return Response({"detail": f"Error listing models: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)