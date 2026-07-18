import os

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CandidateProfile, EmployerProfile
from .serializers import CandidateProfileSerializer, EmployerProfileSerializer, SignupSerializer
from .services import (get_candidate_profile,get_employer_profile,)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = (".pdf", ".doc", ".docx")

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
        profile = get_candidate_profile(request.user)

        if not profile:
            return Response(
                {"message": "Candidate profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CandidateProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = get_candidate_profile(request.user)
        if not profile:
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
        profile = get_candidate_profile(request.user)
        if not profile:
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
        profile = get_employer_profile(request.user)

        if not profile:
            return Response(
                {"message": "Employer profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = EmployerProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = get_employer_profile(request.user)
        if not profile:
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
        profile = get_employer_profile(request.user)
        if not profile:
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
        profile = get_candidate_profile(request.user)
        if not profile:
            return Response(
                {"message": "Candidate profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if "resume" not in request.FILES:
            return Response(
                {"message": "No resume file uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        uploaded_resume = request.FILES["resume"]

        ALLOWED_CONTENT_TYPES = (
            "application/pdf", 
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        if uploaded_resume.content_type not  in ALLOWED_CONTENT_TYPES:
            return Response(
                {"message": "Invalid file type."},
                status=status.HTTP_400_BAD_REQUEST,
                
            )

        extension = os.path.splitext(uploaded_resume.name)[1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            return Response(
                {"message": "Only PDF, DOC and DOCX files are allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if uploaded_resume.size > MAX_FILE_SIZE:
            return Response(
                {"message": "File size must not exceed 5 MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if profile.resume:
            profile.resume.delete(save=False)

        profile.resume = uploaded_resume
        profile.save()

        return Response(
            {
                "message": "Resume uploaded successfully.",
                "resume": profile.resume.url,
            },
            status=status.HTTP_200_OK
        )