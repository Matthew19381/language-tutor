"""
Model Router — wybiera odpowiedni model Ollama w zależności od typu zadania.

Uwaga: Modele muszą być wcześniej pobrane przez `ollama pull <model>`.
"""

def get_model_for_task(task: str, fallback: str = "qwen2.5:7b") -> str:
    """
    Zwróć nazwę modelu dla danego typu zadania.

    Args:
        task: Typ zadania — 'placement', 'lesson', 'conversation', 'code', 'news', 'pronunciation'
        fallback: Model używany jeśli task nieznany

    Returns:
        Nazwa modelu Ollama (np. 'llama3.1', 'qwen2.5:7b')
    """
    mapping = {
        # Szybkie, lekkie modele
        "placement": "qwen2.5:7b",          # test poziomujący — szybki, tani
        "pronunciation": "qwen2.5:7b",      # analiza wymowy — szybka

        # Jakościowe, kreatywne
        "lesson": "llama3.1",               # generowanie lekcji — kreatywny, długi context
        "conversation": "llama3.1",         # rozmowa — naturalny język
        "news": "llama3.1",                 # podsumowanie newsów — jakościowe

        # Specjalistyczne
        "code": "deepseek-coder-v2:16b",    # analiza kodu, debug
    }

    return mapping.get(task, fallback)


def get_available_models() -> list:
    """
    Zwróć listę dostępnych modeli (statyczna, do UI/help).
    """
    return [
        "qwen2.5:7b",
        "llama3.1",
        "deepseek-coder-v2:16b",
    ]
