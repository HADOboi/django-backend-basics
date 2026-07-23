from django.db import models
from accounts.models import EmployerProfile, CandidateProfile
from accounts.models import User

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

    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Application(models.Model):
    STATUS_APPLIED = "APPLIED"
    STATUS_SHORTLISTED = "SHORTLISTED"
    STATUS_INTERVIEW = "INTERVIEW"
    STATUS_REJECTED = "REJECTED"
    STATUS_SELECTED = "SELECTED"

    STATUS_CHOICES = [
        (STATUS_APPLIED, "Applied"),
        (STATUS_SHORTLISTED, "Shortlisted"),
        (STATUS_INTERVIEW, "Interview Scheduled"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_SELECTED, "Selected"),
    ]

    ALLOWED_STATUS_TRANSITIONS = {
        STATUS_APPLIED: [
            STATUS_SHORTLISTED,
            STATUS_REJECTED,
        ],
        STATUS_SHORTLISTED: [
            STATUS_INTERVIEW,
            STATUS_REJECTED,
        ],
        STATUS_INTERVIEW: [
            STATUS_SELECTED,
            STATUS_REJECTED,
        ],
        STATUS_SELECTED: [],
        STATUS_REJECTED: [],
    }

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    resume_snapshot = models.FileField(
        upload_to="application_resumes/"
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_APPLIED,
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    cover_letter = models.TextField()

    class Meta:
        ordering = ["-applied_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["candidate", "job"],
                name="unique_candidate_job_application",
            )
        ]

    def __str__(self):
        return f"{self.candidate} -> {self.job}"

class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="status_history",
    )

    old_status = models.CharField(max_length=30)

    new_status = models.CharField(max_length=30)

    changed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]

    def __str__(self):
        return (
            f"{self.application.id}: "
            f"{self.old_status} -> {self.new_status}"
        )