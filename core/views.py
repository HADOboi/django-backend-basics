from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.db.models.functions import TruncDate

from rest_framework.views import APIView
from rest_framework import generics, status, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from accounts.models import CandidateProfile, EmployerProfile, User
from accounts.utils.resume_parser import parse_resume
from accounts.views import get_candidate_profile

from .services.ats_service import generate_ats_score
from .services.shortlisting_service import auto_process_application
from .services.notification_service import notify_application_status
from .services.automation_service import process_application

from .permissions import IsEmployer, IsCandidate, IsAdmin
from .models import (
    Job, 
    Application, 
    ApplicationStatusHistory, 
    SavedJob,
    AuditLog,
    STATUS_ACTIVE,
)
from .serializers import (
    JobSerializer, 
    JobStatusSerializer, 
    ApplicationSerializer, 
    ApplicationStatusSerializer, 
    ApplicationStatusHistorySerializer, 
    SavedJobSerializer,
    EmployerApplicationSerializer,
)

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import JobFilter

class AdminBlockUserAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        if not user.is_active:
            return Response(
                {
                    "message": "User is already blocked."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = False
        user.save()

        AuditLog.objects.create(
            admin=request.user,
            action="Blocked User",
            target=user.email,
        )

        return Response(
            {
                "message": "User blocked successfully."
            },
            status=status.HTTP_200_OK,
        )

class AdminUnblockUserAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        if user.is_active:
            return Response(
                {
                    "message": "User is already active."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save()

        AuditLog.objects.create(
            admin=request.user,
            action="Unblocked User",
            target=user.email,
        )

        return Response(
            {
                "message": "User unblocked successfully."
            },
            status=status.HTTP_200_OK,
        )

class AdminJobListAPIView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return (
            Job.objects.select_related("employer", "employer__user")
            .order_by("-created_at")
        )

class AdminDeleteJobAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, pk):
        job = get_object_or_404(Job, pk=pk)

        title = job.title

        AuditLog.objects.create(
            admin=request.user,
            action="Deleted Job",
            target=job.title,
        )

        job.delete()

        return Response(
            {
                "message": f"Job '{title}' deleted successfully."
            },
            status=status.HTTP_200_OK,
        )

class AdminFlagUserAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        if user.is_flagged:
            return Response(
                {
                    "message": "User is already flagged."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_flagged = True
        user.save()

        AuditLog.objects.create(
            admin=request.user,
            action="Flagged User",
            target=user.email,
        )

        return Response(
            {
                "message": "User flagged successfully."
            },
            status=status.HTTP_200_OK,
        )

class AdminPlatformStatsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        data = {
            "total_users": User.objects.count(),
            "total_employers": User.objects.filter(
                role=User.ROLE_EMPLOYER
            ).count(),
            "total_candidates": User.objects.filter(
                role=User.ROLE_CANDIDATE
            ).count(),
            "verified_employers": User.objects.filter(
                role=User.ROLE_EMPLOYER,
                employer_profile__is_verified=True,
            ).count(),
            "blocked_users": User.objects.filter(
                is_active=False
            ).count(),
            "flagged_users": User.objects.filter(
                is_flagged=True
            ).count(),
            "total_jobs": Job.objects.count(),
            "total_applications": Application.objects.count(),
        }

        return Response(data)

class AdminUserGrowthAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        growth = (
            User.objects
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(users=Count("id"))
            .order_by("date")
        )

        return Response(growth)

class AdminJobActivityAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        jobs = (
            Job.objects
            .annotate(
                application_count=Count("application")
            )
            .values(
                "id",
                "title",
                "status",
                "created_at",
                "application_count",
            )
            .order_by("-created_at")
        )

        return Response(jobs)

class AdminAuditLogAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        logs = (
            AuditLog.objects.select_related("admin")
            .values(
                "id",
                "admin__username",
                "action",
                "target",
                "created_at",
            )
        )

        return Response(logs)

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

        ats_result = generate_ats_score(
            candidate,
            job,
        )

        application.ats_score = ats_result["total_score"]

        application.save(update_fields=["ats_score"])

        process_application(application)

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

class SaveJobAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsCandidate]

    def post(self, request, job_id):
        candidate = request.user.candidate_profile
        job = get_object_or_404(Job, id=job_id)

        saved_job, created = SavedJob.objects.get_or_create(
            candidate=candidate,
            job=job,
        )

        if not created:
            return Response(
                {"message": "Job already saved."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Job saved successfully."},
            status=status.HTTP_201_CREATED,
        )

class SavedJobListAPIView(generics.ListAPIView):
    serializer_class = SavedJobSerializer
    permission_classes = [IsAuthenticated, IsCandidate]

    def get_queryset(self):
        return (
            SavedJob.objects.filter(
                candidate=self.request.user.candidate_profile
            )
            .select_related("job")
            .order_by("-saved_at")
        )

class RemoveSavedJobAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsCandidate]

    def delete(self, request, job_id):
        candidate = request.user.candidate_profile

        saved_job = get_object_or_404(
            SavedJob,
            candidate=candidate,
            job_id=job_id,
        )

        saved_job.delete()

        return Response(
            {"message": "Job removed from saved jobs."},
            status=status.HTTP_200_OK,
        )

class CandidateInterviewStatusAPIView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsCandidate]

    def get_queryset(self):
        return (
            Application.objects.filter(
                candidate=self.request.user.candidate_profile,
                status__in=[
                    Application.STATUS_SHORTLISTED,
                    Application.STATUS_INTERVIEW,
                    Application.STATUS_SELECTED,
                ],
            )
            .select_related("job")
            .order_by("-applied_at")
        )

class ApplicationTimelineAPIView(generics.ListAPIView):
    serializer_class = ApplicationStatusHistorySerializer
    permission_classes = [IsAuthenticated, IsCandidate]

    def get_queryset(self):
        application = get_object_or_404(
            Application,
            id=self.kwargs["application_id"],
            candidate=self.request.user.candidate_profile,
        )

        return (
            ApplicationStatusHistory.objects.filter(
                application=application
            )
            .order_by("changed_at")
        )

class CandidateRecommendationAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCandidate]

    def get(self, request):
        candidate = request.user.candidate_profile

        candidate_skills = {
            skill.strip().lower()
            for skill in candidate.skills.split(",")
            if skill.strip()
        }

        applied_job_ids = Application.objects.filter(
            candidate=candidate
        ).values_list("job_id", flat=True)

        saved_job_ids = SavedJob.objects.filter(
            candidate=candidate
        ).values_list("job_id", flat=True)

        jobs = Job.objects.filter(
            status=STATUS_ACTIVE
        ).exclude(
            id__in=applied_job_ids
        ).exclude(
            id__in=saved_job_ids
        )

        recommended_jobs = []

        for job in jobs:
            job_skills = {
                skill.strip().lower()
                for skill in job.skills.split(",")
                if skill.strip()
            }

            matched_skills = candidate_skills.intersection(job_skills)

            if matched_skills:
                recommended_jobs.append(job)

        serializer = JobSerializer(
            recommended_jobs,
            many=True
        )

        return Response(serializer.data)

class EmployerApplicationListAPIView(generics.ListAPIView):
    serializer_class = EmployerApplicationSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [SearchFilter]

    search_fields = [
        "candidate__user__first_name",
        "candidate__user__last_name",
        "candidate__user__email",
    ]

    def get_queryset(self):
        queryset = (
            Application.objects
            .select_related("candidate", "job")
            .filter(
                job__employer=self.request.user.employer_profile
            )
        )

        status = self.request.query_params.get("status")

        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by("-applied_at")

class RankedCandidatesAPIView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def get(self, request, job_id):
        job = get_object_or_404(
            Job,
            pk=job_id,
            employer=request.user.employer_profile,
        )

        applications = (
            Application.objects.filter(job=job)
            .select_related(
                "candidate",
                "candidate__user",
            )
            .order_by("-ats_score", "-applied_at")
        )

        data = []

        for index, application in enumerate(applications, start=1):
            data.append({
                "rank": index,
                "candidate": application.candidate.user.get_full_name(),
                "email": application.candidate.user.email,
                "ats_score": application.ats_score,
                "status": application.status,
            })

        return Response(
            {
                "job": job.title,
                "candidates": data,
            },
            status=status.HTTP_200_OK,
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
        employer = self.request.user.employer_profile

        if not employer.is_verified:
            raise serializers.ValidationError(
                {
                    "detail": "Employer account is not verified."
                }
            )

        serializer.save(
            employer=employer
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

class EmployerJobListAPIView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Job.objects.filter(
                employer=self.request.user.employer_profile
            )
            .order_by("-created_at")
        )

class EmployerDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employer = request.user.employer_profile

        jobs = Job.objects.filter(employer=employer)

        applications = Application.objects.filter(
            job__employer=employer
        )

        total_applications = applications.count()

        shortlisted = applications.filter(
            status=Application.STATUS_SHORTLISTED
        ).count()

        if total_applications == 0:
            shortlist_ratio = 0
        else:
            shortlist_ratio = round(
                (shortlisted / total_applications) * 100,
                2,
            )

        data = {
            "total_jobs": jobs.count(),
            "active_jobs": jobs.filter(status=STATUS_ACTIVE).count(),
            "total_applications": total_applications,
            "applied": applications.filter(
                status=Application.STATUS_APPLIED
            ).count(),
            "shortlisted": shortlisted,
            "shortlist_ratio": shortlist_ratio,
            "interview": applications.filter(
                status=Application.STATUS_INTERVIEW
            ).count(),
            "selected": applications.filter(
                status=Application.STATUS_SELECTED
            ).count(),
            "rejected": applications.filter(
                status=Application.STATUS_REJECTED
            ).count(),
        }

        return Response(data)




class AdminEmployerApprovalAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, pk):
        employer = get_object_or_404(
            EmployerProfile,
            pk=pk,
        )

        if employer.is_verified:
            return Response(
                {
                    "message": "Employer is already approved."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        employer.is_verified = True
        employer.save()

        AuditLog.objects.create(
            admin=request.user,
            action="Approved Employer",
            target=employer.user.email,
        )

        return Response(
            {
                "message": "Employer approved successfully."
            },
            status=status.HTTP_200_OK,
        )


class ATSScoreAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        profile = get_candidate_profile(request.user)

        if not profile.resume:
            return Response(
                {
                    "error": "No resume uploaded."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        job = get_object_or_404(Job, pk=job_id)

        ats_score = generate_ats_score(
            profile,
            job,
        )

        return Response(
            {
                "message": "ATS score calculated successfully.",
                "data": ats_score,
            },
            status=status.HTTP_200_OK,
        )

class ApplicationAutomationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        if not hasattr(request.user, "employer_profile"):
            return Response(
                {"detail": "Only employers can process applications."},
                status=status.HTTP_403_FORBIDDEN,
            )

        application = get_object_or_404(
            Application.objects.select_related(
                "job",
                "candidate",
            ),
            pk=pk,
            job__employer=request.user.employer_profile,
        )

        ats_result = generate_ats_score(
            application.candidate,
            application.job,
        )

        application.ats_score = ats_result["total_score"]
        application.save(update_fields=["ats_score"])

        process_application(application)

        return Response(
            {
                "message": "Application processed successfully.",
                "application_id": application.id,
                "ats_score": application.ats_score,
                "status": application.status,
            },
            status=status.HTTP_200_OK,
        )

class UserTestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "User API Working"
        })