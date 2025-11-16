from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser, StudentProfile


@receiver(post_save, sender=CustomUser)
def create_student_profile(sender, instance, created, **kwargs):
    """
    Signal receiver to automatically create a StudentProfile when a new student user is created.
    """
    if created and not instance.is_tpo:
        # Get full name from user, fallback to username if not available
        full_name = instance.get_full_name() or instance.username
        
        StudentProfile.objects.create(
            user=instance,
            full_name=full_name,
            phone="",
            cgpa=0.0,
        )

