from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import (
    User,
    EmployerProfile,
    CandidateProfile,
)

from .models import Job, Application

class JobFlowTests(APITestCase):
    def setUp(self):
        self.password = "TestPass123!"

        self.employer_user = User.objects.create_user(
            username="employer1",
            email="employer@test.com",
            phone="9876543200",
            password=self.password,
            role="EMPLOYER",
        )

        self.employer_profile = self.employer_user.employer_profile

        self.employer_profile.company_name = "Test Company"
        self.employer_profile.is_verified = True
        self.employer_profile.save()

        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "employer1",
                "password": self.password,
            },
            format="json",
        )

        self.token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )

    def test_employer_can_create_job(self):
        response = self.client.post(
            "/api/jobs/create/",
            {
                "title": "Python Developer",
                "description": "Backend Developer",
                "skills": "Python,Django",
                "experience": 2,
                "salary_min": 30000,
                "salary_max": 50000,
                "location": "Kochi",
                "job_type": "FULL_TIME",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(Job.objects.count(), 1)

        job = Job.objects.first()

        self.assertEqual(job.title, "Python Developer")
        self.assertEqual(job.employer, self.employer_profile)

    def test_candidate_cannot_create_job(self):
        candidate_user = User.objects.create_user(
            username="candidate1",
            email="candidate@test.com",
            phone="9876543210",
            password="TestPass123!",
            role="CANDIDATE",
        )

        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "candidate1",
                "password": "TestPass123!",
            },
            format="json",
        )

        token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        response = self.client.post(
            "/api/jobs/create/",
            {
                "title": "Unauthorized Job",
                "description": "Should Fail",
                "skills": "Python",
                "experience": 1,
                "salary_min": 10000,
                "salary_max": 20000,
                "location": "Kochi",
                "job_type": "FULL_TIME",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(Job.objects.count(), 0)

    def test_unverified_employer_cannot_create_job(self):
        self.employer_profile.is_verified = False
        self.employer_profile.save()

        response = self.client.post(
            "/api/jobs/create/",
            {
                "title": "Python Developer",
                "description": "Backend Developer",
                "skills": "Python,Django",
                "experience": 2,
                "salary_min": 30000,
                "salary_max": 50000,
                "location": "Kochi",
                "job_type": "FULL_TIME",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(Job.objects.count(), 0)
    
    def test_public_job_list(self):
        Job.objects.create(
            employer=self.employer_profile,
            title="Python Developer",
            description="Backend Developer",
            skills="Python,Django",
            experience=2,
            salary_min=30000,
            salary_max=50000,
            location="Kochi",
            job_type="FULL_TIME",
        )

        response = self.client.get("/api/jobs/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data["results"]), 1)

        self.assertEqual(
            response.data["results"][0]["title"],
            "Python Developer",
        )

    def test_employer_cannot_update_other_employers_job(self):
        employer2 = User.objects.create_user(
            username="employer2",
            email="employer2@test.com",
            phone="9876543211",
            password="TestPass123!",
            role="EMPLOYER",
        )

        employer2_profile = employer2.employer_profile
        employer2_profile.company_name = "Company B"
        employer2_profile.is_verified = True
        employer2_profile.save()

        job = Job.objects.create(
            employer=employer2_profile,
            title="Original Title",
            description="Backend",
            skills="Python",
            experience=2,
            salary_min=30000,
            salary_max=50000,
            location="Kochi",
            job_type="FULL_TIME",
        )

        response = self.client.patch(
            f"/api/jobs/{job.id}/",
            {
                "title": "Hacked Title",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        job.refresh_from_db()

        self.assertEqual(
            job.title,
            "Original Title",
        )

    def test_employer_cannot_access_admin_platform_stats(self):
        response = self.client.get(
            "/api/admin/platform-stats/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_candidate_cannot_apply_twice(self):
        candidate = User.objects.create_user(
            username="candidate2",
            email="candidate2@test.com",
            phone="9876543212",
            password="TestPass123!",
            role="CANDIDATE",
        )

        candidate_profile = candidate.candidate_profile

        candidate_profile.resume = SimpleUploadedFile(
            "resume.pdf",
            b"Dummy Resume",
            content_type="application/pdf",
        )
        candidate_profile.save()

        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "candidate2",
                "password": "TestPass123!",
            },
            format="json",
        )

        token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        job = Job.objects.create(
            employer=self.employer_profile,
            title="Python Developer",
            description="Backend",
            skills="Python",
            experience=2,
            salary_min=30000,
            salary_max=50000,
            location="Kochi",
            job_type="FULL_TIME",
        )

        Application.objects.create(
            candidate=candidate_profile,
            job=job,
            resume_snapshot=SimpleUploadedFile(
                "resume.pdf",
                b"Dummy Resume"
            ),
            cover_letter="Already applied",
        )

        response = self.client.post(
            "/api/applications/apply/",
            {
                "job": job.id,
                "cover_letter": "Trying again",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Application.objects.count(),
            1,
        )