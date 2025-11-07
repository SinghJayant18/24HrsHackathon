from .settings import settings


def generate_email_content(prompt: str) -> str:
    """
    Best-effort Gemini integration; falls back to prompt if library or
    API key is not available.
    """
    try:
        import google.generativeai as genai

        if not settings.gemini_api_key:
            return prompt
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        resp = model.generate_content(prompt)
        text = getattr(resp, "text", None)
        return text or prompt
    except Exception:
        return prompt
