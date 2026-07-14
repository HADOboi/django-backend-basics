from rest_framework import generics
from .serializers import SignupSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .models import CandidateProfile, EmployerProfile
from .serializers import CandidateProfileSerializer, EmployerProfileSerializer

import os

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")

        token = RefreshToken(refresh)
        token.blacklist()

        return Response({
            "message": "Logged out successfully"
        })

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]


class CandidateProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = CandidateProfile.objects.get(user=request.user)
            serializer = CandidateProfileSerializer(profile)
            return Response(serializer.data)

        except CandidateProfile.DoesNotExist:
            return Response(
                {"message": "Candidate profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request):
        try:
            profile = CandidateProfile.objects.get(user=request.user)
        except CandidateProfile.DoesNotExist:
            return Response(
                {"message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CandidateProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request):
        try:
            profile = CandidateProfile.objects.get(user=request.user)
        except CandidateProfile.DoesNotExist:
            return Response(
                {"message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        profile.is_deleted = True
        profile.save()

        return Response(
            {"message": "Profile deleted successfully"},
            status=status.HTTP_200_OK
        )


class EmployerProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = EmployerProfile.objects.get(user=request.user)
            serializer = EmployerProfileSerializer(profile)
            return Response(serializer.data)

        except EmployerProfile.DoesNotExist:
            return Response(
                {"message": "Employer profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request):
        try:
            profile = EmployerProfile.objects.get(user=request.user)
        except EmployerProfile.DoesNotExist:
            return Response(
                {"message": "Employer profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EmployerProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request):
        try:
            profile = EmployerProfile.objects.get(user=request.user)
        except EmployerProfile.DoesNotExist:
            return Response(
                {"message": "Employer profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        profile.is_deleted = True
        profile.save()

        return Response(
            {"message": "Employer profile deleted successfully"},
            status=status.HTTP_200_OK
        )


class ResumeUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            profile = CandidateProfile.objects.get(user=request.user)
        except CandidateProfile.DoesNotExist:
            return Response(
                {"error": "Candidate profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if "resume" not in request.FILES:
            return Response(
                {"error": "No resume file uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        resume = request.FILES["resume"]

        allowed_extensions = [".pdf", ".doc", ".docx"]
        extension = os.path.splitext(resume.name)[1].lower()

        if extension not in allowed_extensions:
            return Response(
                {"error": "Only PDF, DOC and DOCX files are allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        max_size = 5 * 1024 * 1024  # 5 MB

        if resume.size > max_size:
            return Response(
                {"error": "File size must not exceed 5 MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if profile.resume:
            profile.resume.delete(save=False)

        profile.resume = resume
        profile.save()

        return Response(
            {
                "message": "Resume uploaded successfully.",
                "resume": profile.resume.url,
            },
            status=status.HTTP_200_OK
        )