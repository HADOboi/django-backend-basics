from rest_framework import serializers
from .models import User, CandidateProfile, EmployerProfile


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone",
            "role",
            "password",
        ]

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            phone=validated_data.get("phone", ""),
            role=validated_data.get("role", User.ROLE_CANDIDATE),
            password=validated_data["password"],
        )

class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        fields = "__all__"
        read_only_fields = ["user"]

    def validate_expected_salary(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Expected salary cannot be negative."
            )
        return value

class EmployerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerProfile
        fields = "__all__"
        read_only_fields = ["user"]

    def validate_company_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Company name cannot be empty."
            )
        return value