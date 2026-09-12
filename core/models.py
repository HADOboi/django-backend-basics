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

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["job_type"]),
            models.Index(fields=["location"]),
            models.Index(fields=["created_at"]),
        ]

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

    AI_CALL_QUEUED = "QUEUED"
    AI_CALL_IN_PROGRESS = "IN_PROGRESS"
    AI_CALL_COMPLETED = "COMPLETED"
    AI_CALL_FAILED = "FAILED"

    AI_CALL_STATUS_CHOICES = [
        (AI_CALL_QUEUED, "Queued"),
        (AI_CALL_IN_PROGRESS, "In Progress"),
        (AI_CALL_COMPLETED, "Completed"),
        (AI_CALL_FAILED, "Failed"),
    ]

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

    ats_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    ai_call_status = models.CharField(
        max_length=20,
        choices=AI_CALL_STATUS_CHOICES,
        null=True,
        blank=True,
    )

    ai_call_scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-applied_at"]

        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["candidate"]),
            models.Index(fields=["job"]),
            models.Index(fields=["applied_at"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["candidate", "job"],
                name="unique_candidate_job_application",
            )
        ]

    def __str__(self):
        return f"{self.candidate} -> {self.job}"

class SavedJob(models.Model):
    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="saved_jobs",
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="saved_by_candidates",
    )

    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-saved_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["candidate", "job"],
                name="unique_saved_job",
            )
        ]

    def __str__(self):
        return f"{self.candidate} saved {self.job}"

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

class AuditLog(models.Model):
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )

    action = models.CharField(max_length=255)

    target = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.admin.username} - "
            f"{self.action} - "
            f"{self.target}"
        )

class Notification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    title = models.CharField(max_length=255)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.title}"

class EmailLog(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAILED = "FAILED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    recipient = models.EmailField()
    subject = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    task_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    error_message = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    sent_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.subject} -> {self.recipient}"

class AIInterviewSession(models.Model):
    STATUS_ACTIVE = "ACTIVE"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_FAILED = "FAILED"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="ai_interview_sessions",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"AI Interview Session #{self.id}"


class AIQuestion(models.Model):
    session = models.ForeignKey(
        AIInterviewSession,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    question_text = models.TextField()

    question_order = models.PositiveIntegerField()

    asked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["question_order"]

        constraints = [
            models.UniqueConstraint(
                fields=["session", "question_order"],
                name="unique_session_question_order",
            )
        ]

    def __str__(self):
        return f"Question {self.question_order} - Session #{self.session_id}"


class AIAnswer(models.Model):
    question = models.OneToOneField(
        AIQuestion,
        on_delete=models.CASCADE,
        related_name="answer",
    )

    transcript = models.JSONField(
        default=dict,
        blank=True,
    )

    answered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer - Question #{self.question_id}"


class CallLog(models.Model):
    CALL_INITIATED = "INITIATED"
    CALL_ANSWERED = "ANSWERED"
    CALL_MISSED = "MISSED"
    CALL_FAILED = "FAILED"
    CALL_COMPLETED = "COMPLETED"

    STATUS_CHOICES = [
        (CALL_INITIATED, "Initiated"),
        (CALL_ANSWERED, "Answered"),
        (CALL_MISSED, "Missed"),
        (CALL_FAILED, "Failed"),
        (CALL_COMPLETED, "Completed"),
    ]

    session = models.ForeignKey(
        AIInterviewSession,
        on_delete=models.CASCADE,
        related_name="call_logs",
    )

    triggered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_call_logs",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=CALL_INITIATED,
    )

    trigger_reason = models.TextField()

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    ended_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Call Log #{self.id} - Session #{self.session_id}"
