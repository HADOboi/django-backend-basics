from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .permissions import IsEmployer, IsCandidate, IsAdmin
from .models import Job
from .serializers import JobSerializer


class JobListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer
    queryset = Job.objects.all()

    def get(self, request):
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)


class JobCreateAPIView(APIView):
    permission_classes = [IsEmployer]

    def post(self, request):
        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserTestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "User API Working"
        })