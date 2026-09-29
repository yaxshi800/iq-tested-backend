from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Profile, Payment


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
        read_only_fields = [
            "transaction_id", "status", "created_at", "completed_at",
        ]


class PaymentRequestSerializer(serializers.Serializer):
    plan = serializers.ChoiceField(choices=["pro", "ultimate"])
    card_number = serializers.CharField(min_length=13, max_length=25)
    card_holder = serializers.CharField(max_length=100)
    card_expiry = serializers.CharField(max_length=7)
    card_cvv = serializers.CharField(min_length=3, max_length=4)