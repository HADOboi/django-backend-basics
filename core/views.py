from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .permissions import IsEmployer, IsCandidate, IsAdmin
from .models import Job
from .serializers import JobSerializer, JobStatusSerializer

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class JobListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer
    queryset = Job.objects.select_related("employer")

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "job_type",
        "location",
        "title",
    ]
    search_fields = [
        "title",
        "description",
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

class UserTestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "User API Working"
        })