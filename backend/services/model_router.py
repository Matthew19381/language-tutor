"""
Model Router — wybiera odpowiedni model w zależności od typu zadania i dostawcy.

Uwaga: Modele muszą być dostępne w Twoim koncie OpenRouter (dla openrouter)
lub Google AI Studio (dla gemini).

Darmowe modele oznaczone :free suffixem (tylko OpenRouter).
"""

from backend.config import settings


def get_model_for_task(task: str, fallback: str = None) -> str:
    """
    Zwróć nazwę modelu dla danego typu zadania i aktywnego dostawcy.

    Args:
        task: Typ zadania — 'placement', 'lesson', 'conversation', 'news', 'pronunciation'
        fallback: Model używany jeśli task nieznany (domyślnie zależy od providera)

    Returns:
        Nazwa modelu (np. 'google/gemini-2.0-flash-exp:free' dla openrouter
        lub 'gemini-2.0-flash' dla gemini direct)
    """
    provider = settings.AI_PROVIDER.lower()

    if provider == "gemini":
        return _get_gemini_model(task, fallback)
    else:
        return _get_openrouter_model(task, fallback)


def _get_openrouter_model(task: str, fallback: str = None) -> str:
    """Zwróć model OpenRouter dla danego zadania."""
    if fallback is None:
        fallback = "google/gemini-2.0-flash-exp:free"

    mapping = {
        # Szybkie, lekkie modele (darmowe :free)
        "placement": "qwen/qwen2.5-7b-instruct:free",      # test poziomujący — szybki, tani
        "pronunciation": "qwen/qwen2.5-7b-instruct:free",  # analiza wymowy — szybka

        # Jakościowe, kreatywne (darmowe lub tanie)
        "lesson": "google/gemini-2.0-flash-exp:free",      # generowanie lekcji — kreatywny, długi context
        "conversation": "google/gemini-2.0-flash-exp:free",  # rozmowa — naturalny język
        "news": "google/gemini-2.0-flash-exp:free",        # podsumowanie newsów — jakościowe

        # Specjalistyczne (płatne, najlepsze)
        "code": "openai/gpt-4o:latest",                     # analiza kodu, debug
    }

    return mapping.get(task, fallback)


def _get_gemini_model(task: str, fallback: str = None) -> str:
    """Zwróć model Gemini Direct API dla danego zadania."""
    if fallback is None:
        fallback = "gemini-2.0-flash"

    mapping = {
        # Modele Gemini dla różnych zadań
        "placement": "gemini-2.0-flash",
        "lesson": "gemini-2.0-flash",
        "conversation": "gemini-2.0-flash",
        "news": "gemini-2.0-flash",
        "pronunciation": "gemini-2.0-flash",
        "code": "gemini-2.0-pro",
    }

    return mapping.get(task, fallback)


def get_available_models(provider: str = None) -> list:
    """
    Zwróć listę dostępnych modeli dla danego providera.

    Args:
        provider: 'gemini', 'openrouter', lub None (zwraca dla aktywnego)
    """
    if provider is None:
        provider = settings.AI_PROVIDER.lower()

    if provider == "gemini":
        return [
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-2.0-pro",
        ]
    else:
        return [
            "google/gemini-2.0-flash-exp:free",
            "qwen/qwen2.5-7b-instruct:free",
            "meta-llama/llama-3.1-8b-instruct:free",
            "openai/gpt-4o-mini",
            "openai/gpt-4o",
        ]
