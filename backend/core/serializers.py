from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import (
    CustomUser,
    Skill,
    StudentProfile,
    StudentSkillSet,
    RequiredSkill,
    JobPosting,
    Roadmap,
)


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    name = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False)
    cgpa = serializers.FloatField(write_only=True, required=False, default=0.0)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "name",
            "phone",
            "cgpa",
            "is_tpo",
            "is_active",
        ]
        read_only_fields = ["id", "is_active"]

    def create(self, validated_data):
        # Extract fields that don't belong to User model
        name = validated_data.pop("name", None)
        phone = validated_data.pop("phone", None)
        cgpa = validated_data.pop("cgpa", 0.0)
        password = validated_data.pop("password")
        
        # Set is_active to True for new users
        validated_data["is_active"] = True
        
        # Create the user
        user = CustomUser.objects.create(**validated_data)
        
        # Hash the password properly using set_password
        user.set_password(password)
        user.save()
        
        # Create StudentProfile if name and phone are provided
        if name and phone:
            StudentProfile.objects.create(
                user=user,
                full_name=name,
                phone=phone,
                cgpa=cgpa,
            )
        
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that allows login with either username or email.
    """
    username_field = 'username'

    def validate(self, attrs):
        """
        Override validate to support both username and email login.
        """
        username_or_email = attrs.get('username')
        password = attrs.get('password')

        if not username_or_email or not password:
            raise serializers.ValidationError(
                'Must include "username" and "password".',
                code='authorization'
            )

        # Try to find user by username first, then by email
        try:
            user = CustomUser.objects.get(username=username_or_email)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(email=username_or_email)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError(
                    'No active account found with the given credentials.',
                    code='authorization'
                )

        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError(
                'User account is disabled.',
                code='authorization'
            )

        # Verify password
        if not user.check_password(password):
            raise serializers.ValidationError(
                'No active account found with the given credentials.',
                code='authorization'
            )

        # Update attrs with the actual username for token generation
        attrs['username'] = user.username

        # Call parent validate to generate tokens
        data = super().validate(attrs)
        return data


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "skill_name", "category"]


class StudentSkillSetSerializer(serializers.ModelSerializer):
    student_profile = serializers.PrimaryKeyRelatedField(read_only=True)
    student_profile_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentProfile.objects.all(),
        source="student_profile",
        write_only=True,
        required=False,
    )
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), source="skill", write_only=True
    )

    class Meta:
        model = StudentSkillSet
        fields = [
            "id",
            "student_profile",
            "student_profile_id",
            "skill",
            "skill_id",
            "skill_level",
        ]
        read_only_fields = ["id", "student_profile", "skill"]


class RequiredSkillSerializer(serializers.ModelSerializer):
    job_posting = serializers.PrimaryKeyRelatedField(read_only=True)
    job_posting_id = serializers.PrimaryKeyRelatedField(
        queryset=JobPosting.objects.all(),
        source="job_posting",
        write_only=True,
        required=False,
    )
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), source="skill", write_only=True
    )

    class Meta:
        model = RequiredSkill
        fields = [
            "id",
            "job_posting",
            "job_posting_id",
            "skill",
            "skill_id",
            "required_level",
        ]
        read_only_fields = ["id", "job_posting", "skill"]


class StudentProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source="user",
        write_only=True,
        required=False,
    )
    skill_assignments = StudentSkillSetSerializer(
        source="student_skill_set", many=True, read_only=True
    )

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "user",
            "user_id",
            "full_name",
            "phone",
            "cgpa",
            "resume_url",
            "career_goal",
            "skill_assignments",
        ]


class JobPostingSerializer(serializers.ModelSerializer):
    tpo_user = CustomUserSerializer(read_only=True)
    tpo_user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source="tpo_user", write_only=True
    )
    required_skills = RequiredSkillSerializer(
        source="required_skills_details", many=True, read_only=True
    )

    class Meta:
        model = JobPosting
        fields = [
            "id",
            "tpo_user",
            "tpo_user_id",
            "title",
            "company",
            "description",
            "posted_on",
            "required_skills",
        ]
        read_only_fields = ["id", "tpo_user", "posted_on", "required_skills"]


class RoadmapSerializer(serializers.ModelSerializer):
    profile = StudentProfileSerializer(read_only=True)
    profile_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentProfile.objects.all(), source="profile", write_only=True
    )

    class Meta:
        model = Roadmap
        fields = ["id", "profile", "profile_id", "roadmap_text", "generated_on"]
        read_only_fields = ["id", "profile", "generated_on"]

