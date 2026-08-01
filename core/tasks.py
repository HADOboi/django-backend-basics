from celery import shared_task

from core.models import Application
from core.services.notification_service import (
    send_application_submitted_email,
    send_shortlisted_email,
    send_rejected_email,
)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_application_submitted_email_task(
        application,
        task_id=None,
    ):
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
    