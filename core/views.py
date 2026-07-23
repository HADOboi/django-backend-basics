from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from accounts.models import CandidateProfile

from .permissions import IsEmployer, IsCandidate, IsAdmin
from .models import Job, Application, ApplicationStatusHistory, STATUS_ACTIVE
from .serializers import JobSerializer, JobStatusSerializer, ApplicationSerializer, ApplicationStatusSerializer, ApplicationStatusHistorySerializer, EmployerApplicationSerializer

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import JobFilter

class ApplyJobAPIView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsCandidate]

    def perform_create(self, serializer):
        candidate = self.request.user.candidate_profile
        job = serializer.validated_data["job"]

        if job.status != STATUS_ACTIVE:
            raise ValidationError(
                {"job": "This job is no longer accepting applications."}
            )

        if Application.objects.filter(
            candidate=candidate,
            job=job,
        ).exists():
            raise ValidationError(
                {"job": "You have already applied for this job."}
            )

        if not candidate.resume:
            raise ValidationError(
                {"resume": "Please upload your resume before applying."}
            )

        application = serializer.save(candidate=candidate)

        candidate.resume.open("rb")

        application.resume_snapshot.save(
            candidate.resume.name.split("/")[-1],
            ContentFile(candidate.resume.read()),
            save=True,
        )

        candidate.resume.close()

class CandidateApplicationListAPIView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsCandidate]

    def get_queryset(self):
        return (
            Application.objects.filter(
                candidate=self.request.user.candidate_profile
            )
            .select_related("job")
            .order_by("-applied_at")
        )

class ApplicationStatusUpdateAPIView(generics.UpdateAPIView):
    queryset = Application.objects.select_related("job", "candidate")
    serializer_class = ApplicationStatusSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        application = self.get_object()

        old_status = application.status

        updated_application = serializer.save()

        ApplicationStatusHistory.objects.create(
            application=updated_application,
            old_status=old_status,
            new_status=updated_application.status,
            changed_by=self.request.user,
        )

    def get_queryset(self):
        return Application.objects.filter(
            job__employer=self.request.user.employer_profile
        )

class EmployerApplicationListAPIView(generics.ListAPIView):
    serializer_class = EmployerApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Application.objects
            .select_related("candidate", "job")
            .filter(
                job__employer=self.request.user.employer_profile
            )
            .order_by("-applied_at")
        )

class JobListAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = JobSerializer
    queryset = (
        Job.objects.filter(status="ACTIVE")
        .select_related("employer")
        .order_by("-created_at")
    )

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = JobFilter

    search_fields = [
        "title",
        "description",
        "skills",
        "location",
    ]
    ordering_fields = [
        "created_at",
        "title",
        "salary_min",
        "salary_max",
    ]

class JobCreateAPIView(generics.CreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsEmployer]

    def perform_create(self, serializer):
        serializer.save(
            employer=self.request.user.employer_profile
        )

class JobUpdateAPIView(generics.UpdateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsEmployer]

    def get_queryset(self):
        return Job.objects.filter(
            employer=self.request.user.employer_profile
        )

class JobStatusAPIView(generics.UpdateAPIView):
    serializer_class = JobStatusSerializer
    permission_classes = [IsEmployer]

    def get_queryset(self):
        return Job.objects.filter(
            employer=self.request.user.employer_profile
        )
#no need PATCh endpoint here because UpdateAPIView already
#knows how to use PATCH and PUT

class FeaturedJobListAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = JobSerializer

    queryset = (
        Job.objects.filter(
            status="ACTIVE",
            is_featured=True
        )
        .select_related("employer")
        .order_by("-created_at")
    )

class LatestJobListAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = JobSerializer

    queryset = (
        Job.objects.filter(status="ACTIVE")
        .select_related("employer")
        .order_by("-created_at")
    )

class ApplicationStatusHistoryAPIView(generics.ListAPIView):
    serializer_class = ApplicationStatusHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        application = get_object_or_404(
            Application,
            pk=self.kwargs["pk"],
            job__employer=self.request.user.employer_profile,
        )

        return application.status_history.all()

class UserTestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "User API Working"
        })