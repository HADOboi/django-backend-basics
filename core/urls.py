from django.urls import path
from .views import (
    JobListAPIView,
    JobCreateAPIView,
    JobUpdateAPIView,
    JobStatusAPIView,
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
]