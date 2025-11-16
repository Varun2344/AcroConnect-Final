from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    CustomUser,
    Skill,
    StudentProfile,
    StudentSkillSet,
    JobPosting,
    RequiredSkill,
    Roadmap,
)


class StudentSkillSetInline(admin.TabularInline):
    model = StudentSkillSet
    extra = 1
    autocomplete_fields = ["skill"]


class RequiredSkillInline(admin.TabularInline):
    model = RequiredSkill
    extra = 1
    autocomplete_fields = ["skill"]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    search_fields = ["skill_name"]
    list_display = ("skill_name", "category")


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "is_tpo")
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("is_tpo",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("is_tpo",)}),)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "cgpa")
    search_fields = ("full_name", "user__email")
    inlines = [StudentSkillSetInline]

    @admin.display(description="Email")
    def email(self, obj):
        return obj.user.email


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "posted_on")
    search_fields = ("title", "company", "tpo_user__username", "tpo_user__email")
    inlines = [RequiredSkillInline]


admin.site.register(StudentSkillSet)
admin.site.register(RequiredSkill)
admin.site.register(Roadmap)
