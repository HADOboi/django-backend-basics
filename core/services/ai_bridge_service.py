import httpx

from django.conf import settings


class AIBridgeService:
    """
    Central integration layer for external AI and voice services.
    """

    def __init__(self):
        self.api_key = settings.AI_API_KEY
        self.base_url = settings.AI_API_BASE_URL
        self.fallback_base_url = settings.AI_FALLBACK_API_BASE_URL
        self.fallback_api_key = settings.AI_API_KEY

        if not self.api_key:
            raise ValueError("AI_API_KEY is not configured.")

        if not self.base_url:
            raise ValueError("AI_API_BASE_URL is not configured.")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _post(self, endpoint, payload, retries=3):
        urls = [self.base_url]

        if self.fallback_base_url:
            urls.append(self.fallback_base_url)

        last_error = None

        for base_url in urls:
            url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

            for attempt in range(retries):
                try:
                    response = httpx.post(
                        url,
                        headers=self._headers(),
                        json=payload,
                        timeout=30.0,
                    )

                    if response.status_code == 429:
                        last_error = RuntimeError(
                            "AI API rate limit exceeded."
                        )

                        if attempt == retries - 1:
                            break

                        continue

                    response.raise_for_status()
                    return response.json()

                except httpx.HTTPError as error:
                    last_error = error

                    if attempt == retries - 1:
                        break

        raise last_error

    def select_voice(self, gender, language):
        voices = {
            "male": {
                "en": "male_en",
                "hi": "male_hi",
                "ml": "male_ml",
                "ta": "male_ta",
            },
            "female": {
                "en": "female_en",
                "hi": "female_hi",
                "ml": "female_ml",
                "ta": "female_ta",
            },
        }

        gender = gender.lower()
        language = language.lower()

        try:
            return voices[gender][language]
        except KeyError:
            raise ValueError(
                f"Unsupported voice configuration: gender={gender}, language={language}"
            )

    def trigger_outbound_call(self, phone_number, voice_id, language, script):
        payload = {
            "phone_number": phone_number,
            "voice_id": voice_id,
            "language": language,
            "script": script,
        }

        return self._post("/calls", payload)

    def generate_ai_response(self, prompt):
        payload = {
            "prompt": prompt,
        }

        return self._post("/llm/generate", payload)

    def transcribe_audio(self, audio_url, language):
        payload = {
            "audio_url": audio_url,
            "language": language,
        }

        return self._post("/stt/transcribe", payload)

    def synthesize_speech(self, text, voice_id, language):
        payload = {
            "text": text,
            "voice_id": voice_id,
            "language": language,
        }

        return self._post("/tts/synthesize", payload)
