from django.urls import path
from .views import SignupView, LogoutView, CandidateProfileAPIView, EmployerProfileAPIView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path(
        "signup/",
        SignupView.as_view(),
        name="signup",
    ),

    path(
        "login/",
        TokenObtainPairView.as_view(),
        name="login",
    ),

    path(
        "refresh/",
        TokenRefreshView.as_view(),
        name="refresh",
    ),

    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),

    path(
        "candidate/profile/",
        CandidateProfileAPIView.as_view(),
        name = "candidate-profile",
    ),

    path(
        "employer/profile/",
        EmployerProfileAPIView.as_view(),
        name="employer-profile",
    ),
]