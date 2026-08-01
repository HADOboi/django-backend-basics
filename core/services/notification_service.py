from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone

from core.models import Notification, Application, EmailLog


def notify_application_status(application):
    if application.status == Application.STATUS_SHORTLISTED:
        title = "Application Shortlisted"
        message = (
            f"Congratulations! Your application for "
            f"'{application.job.title}' has been shortlisted."
        )

    elif application.status == Application.STATUS_REJECTED:
        title = "Application Rejected"
        message = (
            f"Your application for "
            f"'{application.job.title}' was not shortlisted."
        )

    else:
        return None

    return Notification.objects.create(
        user=application.candidate.user,
        title=title,
        message=message,
    )


def _send_email(
    subject,
    template_name,
    context,
    recipient,
    task_id=None,
):
    log = EmailLog.objects.create(
        recipient=recipient,
        subject=subject,
        status=EmailLog.STATUS_PENDING,
        task_id=task_id,
    )

    try:
        html_content = render_to_string(
            template_name,
            context,
        )

        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )

        email.attach_alternative(
            html_content,
            "text/html",
        )

        email.send()

        log.status = EmailLog.STATUS_SUCCESS
        log.sent_at = timezone.now()
        log.save(
            update_fields=[
                "status",
                "sent_at",
            ]
        )

    except Exception as exc:
        log.status = EmailLog.STATUS_FAILED
        log.error_message = str(exc)

        log.save(
            update_fields=[
                "status",
                "error_message",
            ]
        )

        raise


def send_application_submitted_email(
    application,
    task_id=None,
):
    context = {
        "application": application,
        "candidate": application.candidate,
        "job": application.job,
    }

    _send_email(
        subject="Application Submitted Successfully",
        template_name="emails/application_submitted.html",
        context=context,
        recipient=application.candidate.user.email,
        task_id=task_id,
    )


def send_shortlisted_email(
    application,
    task_id=None,
):
    context = {
        "application": application,
        "candidate": application.candidate,
        "job": application.job,
    }

    _send_email(
        subject="Congratulations! You have been shortlisted",
        template_name="emails/shortlisted.html",
        context=context,
        recipient=application.candidate.user.email,
        task_id=task_id,
    )


def send_rejected_email(
    application,
    task_id=None,
):
    context = {
        "application": application,
        "candidate": application.candidate,
        "job": application.job,
    }

    _send_email(
        subject="Application Status Update",
        template_name="emails/rejected.html",
        context=context,
        recipient=application.candidate.user.email,
        task_id=task_id,
    )