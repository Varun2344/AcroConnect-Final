import os
import re

views_file = r'backend/core/views.py'
with open(views_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix SkillViewSet permissions
old_skill_view = '''class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]'''

new_skill_view = '''class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        if not self.request.user.is_tpo:
            raise PermissionDenied("Only TPOs can create skills.")
        serializer.save()'''

if old_skill_view in content:
    content = content.replace(old_skill_view, new_skill_view)

# Add RequiredSkillViewSet if it doesn't exist
if 'class RequiredSkillViewSet' not in content:
    required_skill_view = '''
class RequiredSkillViewSet(viewsets.ModelViewSet):
    queryset = RequiredSkill.objects.select_related("job_posting", "skill")
    serializer_class = RequiredSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = RequiredSkill.objects.select_related("job_posting", "skill")
        return queryset

    def perform_create(self, serializer):
        if not self.request.user.is_tpo:
            raise PermissionDenied("Only TPO users can add required skills.")
        serializer.save()

    def perform_update(self, serializer):
        if not self.request.user.is_tpo:
            raise PermissionDenied("Only TPO users can update required skills.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_tpo:
            raise PermissionDenied("Only TPO users can delete required skills.")
        instance.delete()
'''
    # Insert before RoadmapViewSet
    content = content.replace('class RoadmapViewSet', required_skill_view + '\nclass RoadmapViewSet')

with open(views_file, 'w', encoding='utf-8') as f:
    f.write(content)

urls_file = r'backend/core/urls.py'
with open(urls_file, 'r', encoding='utf-8') as f:
    urls_content = f.read()

if 'router.register(r"required-skills", views.RequiredSkillViewSet)' not in urls_content:
    urls_content = urls_content.replace(
        'router.register(r"job-postings", views.JobPostingViewSet)',
        'router.register(r"job-postings", views.JobPostingViewSet)\nrouter.register(r"required-skills", views.RequiredSkillViewSet)'
    )
    with open(urls_file, 'w', encoding='utf-8') as f:
        f.write(urls_content)

print("Backend updated successfully!")
