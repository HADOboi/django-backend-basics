from rest_framework import serializers
from .models import Job, Application, ApplicationStatusHistory

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = [
            "employer",
            "created_at",
            "updated_at",
        ]

class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["status"]

    def validate_status(self, value):
        current_status = self.instance.status

        allowed = Application.ALLOWED_STATUS_TRANSITIONS[current_status]

        if value not in allowed:
            raise serializers.ValidationError(
                f"Cannot change status from {current_status} to {value}."
            )

        return value

class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.EmailField(
        source="changed_by.email",
        read_only=True,
    )

    class Meta:
        model = ApplicationStatusHistory
        fields = [
            "old_status",
            "new_status",
            "changed_by_email",
            "changed_at",
        ]

class JobStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["status"]
    
class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "id",
            "job",
            "resume_snapshot",
            "status",
            "applied_at",
        ]
        read_only_fields = [
            "id",
            "resume_snapshot",
            "status",
            "applied_at",
        ]

class EmployerApplicationSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(
        source="candidate.user.get_full_name",
        read_only=True,
    )

    candidate_email = serializers.EmailField(
        source="candidate.user.email",
        read_only=True,
    )

    job_title = serializers.CharField(
        source="job.title",
        read_only=True,
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "candidate_name",
            "candidate_email",
            "job_title",
            "resume_snapshot",
            "status",
            "applied_at",
        ]