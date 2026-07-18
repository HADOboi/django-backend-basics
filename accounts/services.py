from .models import CandidateProfile, EmployerProfile

def get_candidate_profile(user):
    try:
        return CandidateProfile.objects.get(user=user)
    except CandidateProfile.DoesNotExist:
        return None


def get_employer_profile(user):
    try:
        return EmployerProfile.objects.get(user=user)
    except EmployerProfile.DoesNotExist:
        return None