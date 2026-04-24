from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from .models import JobPosting, Roadmap, Skill, StudentProfile


User = get_user_model()


class AuthenticationFlowTests(APITestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            username="student1",
            email="student1@example.com",
            password=self.password,
            is_tpo=False,
        )

    def test_token_login_with_username(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "student1", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_token_login_with_email(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "student1@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


class PermissionAndOwnershipTests(APITestCase):
    def setUp(self):
        self.student_password = "StrongPass123!"
        self.other_password = "StrongPass456!"
        self.tpo_password = "StrongPass789!"

        self.student = User.objects.create_user(
            username="student_main",
            email="student_main@example.com",
            password=self.student_password,
            is_tpo=False,
        )
        self.other_student = User.objects.create_user(
            username="student_other",
            email="student_other@example.com",
            password=self.other_password,
            is_tpo=False,
        )
        self.tpo = User.objects.create_user(
            username="tpo1",
            email="tpo1@example.com",
            password=self.tpo_password,
            is_tpo=True,
        )

        self.student_profile, _ = StudentProfile.objects.update_or_create(
            user=self.student,
            defaults={
                "full_name": "Main Student",
                "phone": "12345",
                "cgpa": 8.1,
                "career_goal": "Backend Engineer",
            },
        )
        self.other_profile, _ = StudentProfile.objects.update_or_create(
            user=self.other_student,
            defaults={
                "full_name": "Other Student",
                "phone": "54321",
                "cgpa": 7.5,
                "career_goal": "Data Analyst",
            },
        )

    def test_user_registration_cannot_set_is_tpo(self):
        response = self.client.post(
            "/api/v1/users/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "StrongPass999!",
                "is_tpo": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = User.objects.get(username="newuser")
        self.assertFalse(created.is_tpo)

    def test_student_only_sees_own_profile(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/v1/student-profiles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.student_profile.id)

    def test_student_cannot_create_job_posting(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            "/api/v1/job-postings/",
            {"title": "SDE Intern", "company": "Acme", "description": "Role desc"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_tpo_can_create_job_posting(self):
        self.client.force_authenticate(user=self.tpo)
        response = self.client.post(
            "/api/v1/job-postings/",
            {"title": "SDE Intern", "company": "Acme", "description": "Role desc"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(JobPosting.objects.count(), 1)
        self.assertEqual(JobPosting.objects.first().tpo_user_id, self.tpo.id)

    def test_student_skillset_creation_ignores_foreign_profile_id(self):
        skill = Skill.objects.create(skill_name="Python", category="Programming")
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            "/api/v1/student-skill-sets/",
            {
                "student_profile_id": self.other_profile.id,
                "skill_id": skill.id,
                "skill_level": 4,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["student_profile"], self.student_profile.id)


class RoadmapEndpointTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="roadmap_student",
            email="roadmap_student@example.com",
            password="StrongPass123!",
            is_tpo=False,
        )
        self.profile, _ = StudentProfile.objects.update_or_create(
            user=self.user,
            defaults={
                "full_name": "Roadmap Student",
                "phone": "99999",
                "cgpa": 8.7,
                "career_goal": "AI Engineer",
            },
        )

    def test_generate_roadmap_uses_fallback_when_gemini_not_configured(self):
        self.client.force_authenticate(user=self.user)
        with patch("core.views.get_configured_gemini_client", return_value=(None, "missing key")):
            response = self.client.post("/api/v1/generate-roadmap/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Roadmap.objects.count(), 1)
        self.assertIn("Fallback Mode", response.data["roadmap_text"])

    def test_genai_models_endpoint_reports_unavailable_reason(self):
        self.client.force_authenticate(user=self.user)
        with patch("core.views.get_configured_gemini_client", return_value=(None, "missing key")):
            response = self.client.get("/api/v1/genai-models/")
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("missing key", response.data["detail"])
