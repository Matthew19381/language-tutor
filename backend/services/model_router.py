"""
Model Router — wybiera odpowiedni model OpenRouter w zależności od typu zadania.

Uwaga: Modele muszą być dostępne w Twoim koncie OpenRouter.
Darmowe modele oznaczone :free suffixem.
"""

def get_model_for_task(task: str, fallback: str = "google/gemini-2.0-flash-exp:free") -> str:
    """
    Zwróć nazwę modelu OpenRouter dla danego typu zadania.

    Args:
        task: Typ zadania — 'placement', 'lesson', 'conversation', 'news', 'pronunciation'
        fallback: Model używany jeśli task nieznany

    Returns:
        Nazwa modelu OpenRouter (np. 'google/gemini-2.0-flash-exp:free')
    """
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


def get_available_models() -> list:
    """
    Zwróć listę dostępnych modeli (do UI/help).
    """
    return [
        "google/gemini-2.0-flash-exp:free",
        "qwen/qwen2.5-7b-instruct:free",
        "meta-llama/llama-3.1-8b-instruct:free",
        "openai/gpt-4o-mini",
        "openai/gpt-4o",
    ]
