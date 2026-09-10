from celery import shared_task

from core.models import Application
from core.services.notification_service import (
    send_application_submitted_email,
    send_shortlisted_email,
    send_rejected_email,
)

from core.services.ats_service import generate_ats_score

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_application_submitted_email_task(self, application_id):
    application = Application.objects.get(pk=application_id)

    send_application_submitted_email(
        application,
        task_id=self.request.id,
    )

    return f"Email sent for application {application.id}"

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_shortlisted_email_task(self, application_id):
    application = Application.objects.get(pk=application_id)
    send_shortlisted_email(application)
    return f"Shortlisted email sent for application {application.id}"

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_rejected_email_task(self, application_id):
    application = Application.objects.get(pk=application_id)
    send_rejected_email(application)
    return f"Rejected email sent for application {application.id}"

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def generate_ats_score_task(self, application_id):
    application = Application.objects.select_related(
        "candidate",
        "job",
    ).get(pk=application_id)

    score = generate_ats_score(
        application.candidate,
        application.job,
    )

    application.ats_score = score["total_score"]
    application.save(update_fields=["ats_score"])

    return (
        f"ATS score generated for application "
        f"{application.id}: {score['total_score']}"
    )

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def trigger_ai_processing_task(self, application_id):
    from django.utils import timezone

    from core.models import Application
    from core.services.eligibility_service import is_application_eligible

    application = Application.objects.select_related(
        "candidate",
        "job",
    ).get(pk=application_id)

    eligibility = is_application_eligible(application)

    if not eligibility["eligible"]:
        if eligibility["reason"] == "Outside AI call time window.":
            application.ai_call_status = Application.AI_CALL_QUEUED
            application.save(update_fields=["ai_call_status"])
            return f"AI call queued for application {application.id}"

        application.ai_call_status = Application.AI_CALL_FAILED
        application.save(update_fields=["ai_call_status"])
        return f"AI call not eligible: {eligibility['reason']}"

    application.ai_call_status = Application.AI_CALL_IN_PROGRESS
    application.save(update_fields=["ai_call_status"])

    # Placeholder for future AI/LLM call integration.
    application.ai_call_status = Application.AI_CALL_COMPLETED
    application.ai_call_scheduled_at = timezone.now()
    application.save(
        update_fields=[
            "ai_call_status",
            "ai_call_scheduled_at",
        ]
    )

    return f"AI call completed for application {application.id}"

@shared_task
def process_queued_ai_calls():
    from core.models import Application

    applications = Application.objects.filter(
        ai_call_status=Application.AI_CALL_QUEUED
    )

    for application in applications:
        trigger_ai_processing_task.delay(application.id)

    return f"{applications.count()} queued AI calls processed"

@shared_task
def process_pending_applications_task():
    from core.services.automation_service import process_pending_applications

    process_pending_applications()
    return "Pending applications processed"
