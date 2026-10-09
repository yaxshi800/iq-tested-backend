from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import (
    Profile, Payment, TeacherProfile, Classroom, ClassMembership,
    Achievement, UserAchievement, DailyStreak,
)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Parollar mos emas."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "username", "email",
            "full_name", "passport_series", "phone_number",
            "plan", "plan_started_at", "plan_expires_at",
            "certificate_issued", "certificate_uuid", "certificate_downloads",
            "is_certificate_ready", "is_pro", "is_ultimate", "is_free",
            "created_at",
        ]
        read_only_fields = [
            "plan", "plan_started_at", "plan_expires_at",
            "certificate_issued", "certificate_uuid", "certificate_downloads",
            "is_certificate_ready", "is_pro", "is_ultimate", "is_free",
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "profile"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "plan", "amount", "currency",
            "card_type", "card_last4", "card_holder",
            "transaction_id", "status", "created_at", "completed_at",
        ]
        read_only_fields = ["transaction_id", "status", "created_at", "completed_at"]


class PaymentRequestSerializer(serializers.Serializer):
    plan = serializers.ChoiceField(choices=["pro", "ultimate"])
    card_number = serializers.CharField(min_length=13, max_length=25)
    card_holder = serializers.CharField(max_length=100)
    card_expiry = serializers.CharField(max_length=7)
    card_cvv = serializers.CharField(min_length=3, max_length=4)


# Teacher
class TeacherProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = TeacherProfile
        fields = ["username", "email", "school_name", "subject", "phone", "is_verified", "created_at"]
        read_only_fields = ["is_verified", "created_at"]


class ClassroomSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.username", read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Classroom
        fields = ["id", "name", "description", "invite_code", "grade", "is_active", "created_at", "teacher_name", "members_count"]
        read_only_fields = ["invite_code", "created_at"]

    def get_members_count(self, obj):
        return obj.members.count()


# Gamification
class AchievementSerializer(serializers.ModelSerializer):
    earned = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = ["id", "code", "name_uz", "description_uz", "icon", "color", "points", "order", "earned"]

    def get_earned(self, obj):
        user = self.context.get("user")
        if not user or not user.is_authenticated:
            return False
        return UserAchievement.objects.filter(user=user, achievement=obj).exists()


class DailyStreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStreak
        fields = ["current_streak", "longest_streak", "last_activity", "total_points"]