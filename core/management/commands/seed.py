from django.core.management.base import BaseCommand

from accounts.models import User, CandidateProfile, EmployerProfile
from core.models import (
    Job,
    JOB_FULL_TIME,
    STATUS_ACTIVE,
)


class Command(BaseCommand):
    help = "Create demo users, profiles and jobs"

    def handle(self, *args, **kwargs):

        # ---------------- Employer ----------------

        employer, created = User.objects.get_or_create(
            username="employer",
            defaults={
                "email": "employer@test.com",
                "phone": "9999999991",
                "role": User.ROLE_EMPLOYER,
            },
        )

        employer.set_password("123456")
        employer.save()

        employer_profile, _ = EmployerProfile.objects.get_or_create(
            user=employer,
            defaults={
                "company_name": "Demo Company",
                "company_domain": "Software",
                "company_size": "50-100",
            },
        )

        # ---------------- Candidate ----------------

        candidate, created = User.objects.get_or_create(
            username="candidate",
            defaults={
                "email": "candidate@test.com",
                "phone": "9999999992",
                "role": User.ROLE_CANDIDATE,
            },
        )

        candidate.set_password("123456")
        candidate.save()

        CandidateProfile.objects.get_or_create(
            user=candidate,
            defaults={
                "skills": "Python, Django",
                "education": "B.Tech CSE",
                "experience": "Fresher",
                "expected_salary": 500000,
            },
        )

        # ---------------- Jobs ----------------

        for i in range(1, 6):
            Job.objects.get_or_create(
                employer=employer_profile,
                title=f"Backend Developer {i}",
                defaults={
                    "description": "Demo backend developer job.",
                    "skills": "Python, Django, REST",
                    "experience": 1,
                    "salary_min": 30000,
                    "salary_max": 50000,
                    "location": "Kochi",
                    "job_type": JOB_FULL_TIME,
                    "status": STATUS_ACTIVE,
                    "is_featured": False,
                },
            )

        self.stdout.write(
            self.style.SUCCESS("Demo data created successfully.")
        )