from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_ADMIN = "ADMIN"
    ROLE_EMPLOYER = "EMPLOYER"
    ROLE_CANDIDATE = "CANDIDATE"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_EMPLOYER, "Employer"),
        (ROLE_CANDIDATE, "Candidate"),
    ]

    email = models.EmailField(unique=True)
    phone = models.CharField(
            max_length=15,
            unique=True,
            blank=True,
            )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CANDIDATE,
    )

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

class CandidateProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="candidate_profile"
    )

    def __str__(self):
        return self.user.email


class EmployerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employer_profile"
    )

    def __str__(self):
        return self.user.email