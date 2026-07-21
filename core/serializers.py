from rest_framework import serializers
from .models import Job, Application

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = [
            "employer",
            "created_at",
            "updated_at",
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