from core.models import Application
from datetime import time
from django.utils import timezone

AI_CALL_MIN_ATS_SCORE = 70

AI_CALL_START_TIME = time(9, 0)
AI_CALL_END_TIME = time(18, 0)

def is_application_eligible(application):
    if application.status not in (
        Application.STATUS_APPLIED,
        Application.STATUS_SHORTLISTED,
    ):
        return {
            "eligible": False,
            "reason": "Application already processed.",
        }

    if application.job.status != "ACTIVE":
        return {
            "eligible": False,
            "reason": "Job is not active.",
        }

    if not application.candidate.resume:
        return {
            "eligible": False,
            "reason": "Candidate has not uploaded a resume.",
        }

    if not application.candidate.is_available_for_ai_call:
        return {
            "eligible": False,
            "reason": "Candidate is not available for AI call.",
        }

    current_time = timezone.localtime().time()

    if not AI_CALL_START_TIME <= current_time <= AI_CALL_END_TIME:
        return {
            "eligible": False,
            "reason": "Outside AI call time window.",
        }

    if application.ats_score is None:
        return {
            "eligible": False,
            "reason": "ATS score not generated.",
        }

    if application.ats_score < AI_CALL_MIN_ATS_SCORE:
        return {
            "eligible": False,
            "reason": "ATS score below AI call threshold.",
        }

    return {
        "eligible": True,
        "reason": None,
    }
