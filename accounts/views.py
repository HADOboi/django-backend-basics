from rest_framework import generics
from .serializers import SignupSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")

        token = RefreshToken(refresh)
        token.blacklist()

        return Response({
            "message": "Logged out successfully"
        })