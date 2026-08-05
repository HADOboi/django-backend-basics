from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

from .models import User

class AuthenticationTests(APITestCase):
    def test_candidate_signup_success(self):
        url = "/api/auth/signup/"

        data = {
            "username": "candidate1",
            "email": "candidate1@test.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "role": "CANDIDATE",
            "first_name": "Test",
            "last_name": "Candidate",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.first()

        self.assertEqual(user.role, "CANDIDATE")
        self.assertTrue(user.check_password("TestPass123!"))

    def test_user_login_success(self):
        password = "TestPass123!"

        User.objects.create_user(
            username="candidate1",
            email="candidate1@test.com",
            password=password,
            role="CANDIDATE",
        )

        url = "/api/auth/login/"

        data = {
            "username": "candidate1",
            "password": password,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_login_invalid_password(self):
        User.objects.create_user(
            username="candidate1",
            email="candidate1@test.com",
            password="CorrectPassword123!",
            role="CANDIDATE",
        )

        url = "/api/auth/login/"

        data = {
            "username": "candidate1",
            "password": "WrongPassword123!",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)