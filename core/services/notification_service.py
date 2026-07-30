from core.models import Notification, Application


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