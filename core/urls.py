from django.urls import path
from .views import (
    JobListAPIView,
    JobCreateAPIView,
    JobUpdateAPIView,
    JobStatusAPIView,
    FeaturedJobListAPIView,
    LatestJobListAPIView,
    CandidateApplicationListAPIView,
    ApplyJobAPIView,
    ApplicationStatusUpdateAPIView,
    EmployerApplicationListAPIView,
    ApplicationStatusHistoryAPIView,
    EmployerJobListAPIView,
    EmployerDashboardAPIView,
    UserTestAPIView,
)

urlpatterns = [
    path('jobs/', JobListAPIView.as_view()),
    path('jobs/create/', JobCreateAPIView.as_view()),
    path("jobs/<int:pk>/", JobUpdateAPIView.as_view()),
    path('user/test/', UserTestAPIView.as_view()),
    path(
        "jobs/<int:pk>/status/",
        JobStatusAPIView.as_view(),
    ),
    path(
        "jobs/featured/",
        FeaturedJobListAPIView.as_view(),
    ),
    path(
        "jobs/latest/",
        LatestJobListAPIView.as_view(),
    ),
    path(
        "applications/",
        CandidateApplicationListAPIView.as_view(),
        name="candidate-applications",
    ),
    path(
        "applications/apply/",
        ApplyJobAPIView.as_view(),
        name="apply-job",
    ),
    path(
        "applications/<int:pk>/status/",
        ApplicationStatusUpdateAPIView.as_view(),
    ),
    path(
        "employer/applications/",
        EmployerApplicationListAPIView.as_view(),
    ),
    path(
        "applications/<int:pk>/history/",
        ApplicationStatusHistoryAPIView.as_view(),
    ),
    path(
        "employer/jobs/",
        EmployerJobListAPIView.as_view(),
    ),
    path(
        "employer/dashboard/",
        EmployerDashboardAPIView.as_view(),
    ),
]