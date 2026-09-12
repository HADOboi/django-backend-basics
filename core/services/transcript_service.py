from core.models import AIAnswer


def store_transcript(question, transcript_data):
    """
    Store structured voice-to-text transcript data for an AI question.
    """
    answer, _ = AIAnswer.objects.update_or_create(
        question=question,
        defaults={
            "transcript": transcript_data,
        },
    )

    return answer
