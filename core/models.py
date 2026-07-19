from django.db import models
from accounts.models import EmployerProfile, CandidateProfile

JOB_FULL_TIME = "FULL_TIME"
JOB_PART_TIME = "PART_TIME"
JOB_REMOTE = "REMOTE"
JOB_INTERNSHIP = "INTERNSHIP"

JOB_TYPE_CHOICES = [
    (JOB_FULL_TIME, "Full Time"),
    (JOB_PART_TIME, "Part Time"),
    (JOB_REMOTE, "Remote"),
    (JOB_INTERNSHIP, "Internship"),
]


STATUS_ACTIVE = "ACTIVE"
STATUS_INACTIVE = "INACTIVE"

STATUS_CHOICES = [
    (STATUS_ACTIVE, "Active"),
    (STATUS_INACTIVE, "Inactive"),
]

class Job(models.Model):
    employer = models.ForeignKey(
        EmployerProfile,
        on_delete=models.CASCADE,
        related_name="jobs"
    )
    title = models.CharField(max_length=255)

    description = models.TextField()

    skills = models.TextField()

    experience = models.PositiveIntegerField()

    salary_min = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    salary_max = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    location = models.CharField(max_length=255)

    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        default=JOB_FULL_TIME
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Application(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    ]

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    applied_at = models.DateTimeField(auto_now_add=True)
    cover_letter = models.TextField()

    def __str__(self):
        return f"{self.candidate} -> {self.job}"