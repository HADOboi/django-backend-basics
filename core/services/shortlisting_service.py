from core.models import (
    Application,
    JOB_FULL_TIME,
    JOB_PART_TIME,
    JOB_REMOTE,
    JOB_INTERNSHIP,
)

THRESHOLDS = {
    JOB_FULL_TIME: 75,
    JOB_PART_TIME: 65,
    JOB_REMOTE: 80,
    JOB_INTERNSHIP: 60,
}

def auto_process_application(application):

    threshold = THRESHOLDS.get(application.job.job_type, 70)

    if application.ats_score >= threshold:
        return Application.STATUS_SHORTLISTED

    return Application.STATUS_REJECTED