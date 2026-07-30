from core.models import Application


def is_application_eligible(application):
    if application.status != Application.STATUS_APPLIED:
        return {
            "eligible": False,
            "reason": "Application already processed.",
        }

    if not application.candidate.resume:
        return {
            "eligible": False,
            "reason": "Candidate has not uploaded a resume.",
        }

    if application.ats_score is None:
        return {
            "eligible": False,
            "reason": "ATS score not generated.",
        }

    return {
        "eligible": True,
        "reason": None,
    }