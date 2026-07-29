import re

from accounts.utils.resume_parser import parse_resume

SKILLS_WEIGHT = 60
EXPERIENCE_WEIGHT = 25
EDUCATION_WEIGHT = 15

def extract_job_skills(job):
    """
    Extract and normalize skills from a job.
    """
    if not job.skills:
        return []

    return [
        skill.strip().lower()
        for skill in job.skills.split(",")
        if skill.strip()
    ]

def calculate_skill_score(job_skills, resume_skills):
    """
    Calculate the skill matching score.
    """
    if not job_skills:
        return 0

    matched_skills = set(job_skills) & set(
        skill.lower() for skill in resume_skills
    )

    match_ratio = len(matched_skills) / len(job_skills)

    return round(match_ratio * SKILLS_WEIGHT, 2)

def calculate_experience_score(required_experience, candidate_experience):
    """
    Calculate the experience matching score.
    """
    if candidate_experience is None:
        return 0

    if required_experience <= 0:
            return EXPERIENCE_WEIGHT

    if candidate_experience >= required_experience:
        return EXPERIENCE_WEIGHT

    match_ratio = candidate_experience / required_experience

    return round(match_ratio * EXPERIENCE_WEIGHT, 2)

def calculate_education_score(candidate_education):
    """
    Calculate the education score.
    """
    if not candidate_education:
        return 0

    preferred_qualifications = {
        "b.tech",
        "bachelor of technology",
        "b.e",
        "bachelor of engineering",
        "m.tech",
        "master of technology",
        "m.e",
        "master of engineering",
        "mca",
        "bca",
    }

    candidate = {
        education.lower()
        for education in candidate_education
    }

    if candidate & preferred_qualifications:
        return EDUCATION_WEIGHT

    return 0

def calculate_ats_score(job, parsed_resume):
    """
    Calculate the overall ATS score.
    """
    job_skills = extract_job_skills(job)

    skill_score = calculate_skill_score(
        job_skills,
        parsed_resume["skills"],
    )

    experience_score = calculate_experience_score(
        job.experience,
        parsed_resume["experience_years"],
    )

    education_score = calculate_education_score(
        parsed_resume["education"],
    )

    total_score = round(
        skill_score +
        experience_score +
        education_score,
        2,
    )

    return {
        "total_score": total_score,
        "skill_score": skill_score,
        "experience_score": experience_score,
        "education_score": education_score,
    }


def generate_ats_score(candidate, job):
    """
    Generate the ATS score for a candidate against a job.
    """
    parsed_resume = parse_resume(candidate.resume.path)

    return calculate_ats_score(
        job,
        parsed_resume,
    )