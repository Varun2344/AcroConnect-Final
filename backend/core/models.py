from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Application-specific user model that distinguishes TPO users from students.
    """

    email = models.EmailField(unique=True)
    is_tpo = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["email"]

    def __str__(self) -> str:
        role = "TPO" if self.is_tpo else "Student"
        return f"{self.username} ({role})"


class Skill(models.Model):
    """
    Canonical list of skills that can be referenced by students and job postings.
    """

    skill_name = models.CharField(max_length=128, unique=True)
    category = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ["skill_name"]

    def __str__(self) -> str:
        return self.skill_name


class StudentProfile(models.Model):
    """
    Extended profile for student users.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile"
    )
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    cgpa = models.FloatField()
    resume_url = models.URLField(blank=True)
    career_goal = models.TextField(blank=True, help_text="Student's career goal or aspiration")
    skills = models.ManyToManyField(
        Skill, through="StudentSkillSet", related_name="student_profiles", blank=True
    )

    class Meta:
        ordering = ["full_name"]

    def __str__(self) -> str:
        return self.full_name


class JobPosting(models.Model):
    """
    Job postings created and managed by TPO users.
    """

    tpo_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_postings"
    )
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True)
    required_skills = models.ManyToManyField(
        Skill, through="RequiredSkill", related_name="job_postings", blank=True
    )

    class Meta:
        ordering = ["-posted_on"]

    def __str__(self) -> str:
        return self.title


class StudentSkillSet(models.Model):
    """
    Through model representing a student's proficiency for a specific skill.
    """

    student_profile = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="student_skill_set"
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="student_skill_set")
    skill_level = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("student_profile", "skill")
        verbose_name = "Student Skill"
        verbose_name_plural = "Student Skill Set"

    def __str__(self) -> str:
        return f"{self.student_profile} - {self.skill} ({self.skill_level})"


class RequiredSkill(models.Model):
    """
    Through model representing the skill requirements for a job posting.
    """

    job_posting = models.ForeignKey(
        JobPosting, on_delete=models.CASCADE, related_name="required_skills_details"
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="required_by_jobs")
    required_level = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("job_posting", "skill")
        verbose_name = "Required Skill"
        verbose_name_plural = "Required Skills"

    def __str__(self) -> str:
        return f"{self.job_posting}: {self.skill} (Level {self.required_level})"


class Roadmap(models.Model):
    """
    AI-generated roadmap for a student profile.
    """

    profile = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="roadmaps"
    )
    roadmap_text = models.TextField()
    generated_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-generated_on"]

    def __str__(self) -> str:
        return f"Roadmap for {self.profile.full_name} on {self.generated_on:%Y-%m-%d}"
