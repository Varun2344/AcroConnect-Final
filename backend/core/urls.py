from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CustomUserViewSet,
    SkillViewSet,
    StudentProfileViewSet,
    StudentSkillSetViewSet,
    JobPostingViewSet,
    RoadmapViewSet,
    GenerateRoadmapView,
    CurrentUserView,
    ListGenaiModelsView,
)

router = DefaultRouter()
router.register(r"users", CustomUserViewSet)
router.register(r"skills", SkillViewSet)
router.register(r"student-profiles", StudentProfileViewSet)
router.register(r"student-skill-sets", StudentSkillSetViewSet)
router.register(r"job-postings", JobPostingViewSet)
router.register(r"roadmaps", RoadmapViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("generate-roadmap/", GenerateRoadmapView.as_view(), name="generate-roadmap"),
    path("users/me/", CurrentUserView.as_view(), name="current-user"),
    path("genai-models/", ListGenaiModelsView.as_view(), name="genai-models"),
]

