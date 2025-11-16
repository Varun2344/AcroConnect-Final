import os
import logging

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

# Try to import and configure Gemini API (optional)
try:
    import google.generativeai as genai
    # Get API key from environment variable, or use the provided key as fallback
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyBUNzTdzHsB5qMpj8Izqb5MdhyF0KAOfNk")
    genai.configure(api_key=api_key)
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

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




class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [permissions.IsAuthenticated()]

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


class StudentSkillSetViewSet(viewsets.ModelViewSet):
    queryset = StudentSkillSet.objects.select_related("student_profile", "skill")
    serializer_class = StudentSkillSetSerializer
    permission_classes = [permissions.IsAuthenticated]


class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.select_related("user").prefetch_related("student_skill_set__skill")
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

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


class RoadmapViewSet(viewsets.ModelViewSet):
    queryset = Roadmap.objects.select_related("profile", "profile__user")
    serializer_class = RoadmapSerializer
    permission_classes = [permissions.IsAuthenticated]


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

        # Build detailed prompt for AI
        prompt = f"""You are a career guidance AI assistant. Create a personalized learning roadmap for a student.

Student Information:
- Name: {profile.full_name}
- CGPA: {profile.cgpa}
- Career Goal: {career_goal}
- Current Skills: {skills_text}

Please create a comprehensive, step-by-step learning roadmap that will help this student achieve their career goal. The roadmap should:
1. Be specific and actionable
2. Build upon their current skills
3. Include milestones and checkpoints
4. Suggest learning resources and next steps
5. Be realistic and achievable

Format the roadmap in a clear, structured way with sections and bullet points."""

        if not GEMINI_AVAILABLE:
            return Response(
                {"detail": "Gemini API is not available. Please install google-generativeai package and set GEMINI_API_KEY environment variable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            # Try several likely models in order until one succeeds.
            # Some deployments do not expose every Gemini model name, so we attempt
            # a few candidates and fall back gracefully.
            # Prefer the models that are commonly available in modern Google GenAI
            # deployments (based on the output from list_models()).
            models_to_try = [
                "gemini-flash-latest",
                "gemini-pro-latest",
                "gemini-2.5-flash",
                "gemini-2.5-pro",
                "gemini-2.5-flash-lite",
                "gemini-2.0-flash",
                "gemini-2.0-flash-lite",
                "gemini-1.5-flash",
                "text-bison-001",
            ]

            roadmap_text = None
            last_exception = None
            used_model = None

            for candidate in models_to_try:
                try:
                    model = genai.GenerativeModel(candidate)
                    response = model.generate_content(prompt)

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
                # No model produced usable text
                detail_msg = (
                    "No usable model available. Tried models: "
                    + ", ".join(models_to_try)
                    + ", "
                    + (f"last error: {str(last_exception)}" if last_exception else "no exception captured")
                )
                return Response({"detail": detail_msg}, status=status.HTTP_502_BAD_GATEWAY)
            # Optionally annotate which model was used (for debugging) at the top
            # we do not prepend debug metadata to the saved roadmap text here;
            # model usage is logged via the logger for diagnostics.

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Gemini API Error: {error_details}")
            return Response(
                {"detail": f"Error generating roadmap: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

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
        if not GEMINI_AVAILABLE:
            return Response(
                {"detail": "Gemini API (google-generativeai) is not installed or not configured."},
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