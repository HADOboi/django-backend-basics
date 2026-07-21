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
]