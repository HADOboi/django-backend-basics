from core.services.shortlisting_service import auto_process_application
from core.services.notification_service import notify_application_status

from core.tasks import (
    send_shortlisted_email_task,
    send_rejected_email_task,
)
from core.services.eligibility_service import is_application_eligible
from core.models import Application

def process_application(application):

    eligibility = is_application_eligible(application)

    if not eligibility["eligible"]:
        return application

    new_status = auto_process_application(application)

    if application.status != new_status:
        application.status = new_status
        application.save(update_fields=["status"])

        notify_application_status(application)

        if application.status == Application.STATUS_SHORTLISTED:
            send_shortlisted_email_task.delay(application.id)

        elif application.status == Application.STATUS_REJECTED:
            send_rejected_email_task.delay(application.id)

    return application

from core.models import Application


def process_pending_applications():
    applications = Application.objects.filter(
        status=Application.STATUS_APPLIED
    )

    for application in applications:
        process_application(application)

    return applications.count()