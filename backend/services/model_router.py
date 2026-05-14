"""
Model Router — wybiera odpowiedni model w zależności od typu zadania i dostawcy.

OpenRouter free models (May 2026): 30+ models with :free suffix.
Rate limits: 20 req/min, 200 req/day per free model.

Gemini Direct API: requires Google AI Studio API key.
"""

from backend.config import settings


# ── Complete OpenRouter free model catalog (May 2026) ──────────────────────
# Format: "model_id"  # context_length | category | notes

OPENROUTER_FREE_MODELS = {
    # ── Premium tier (256K-1M context) ──────────────────────────────────────
    "openrouter/owl-alpha":           "1.0M | agentic | tools, long-context, foundation",
    "inclusionai/ring-2.6-1t:free":   "262K | reasoning | tools, 1T params",
    "google/gemma-4-26b-a4b-it:free": "262K | multimodal | vision+tools",
    "google/gemma-4-31b-it:free":    "262K | multimodal | vision+tools",
    "arcee-ai/trinity-large-thinking:free": "262K | reasoning | tools, thinking",
    "nvidia/nemotron-3-super-120b-a12b:free": "262K | reasoning | MoE, tools",
    "qwen/qwen3-next-80b-a3b-instruct:free":  "262K | instruct | tools, MoE",
    "qwen/qwen3-coder:free":         "262K | coding | best free coding model",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free": "256K | multimodal | vision+tools",
    "deepseek/deepseek-v4-flash:free": "256K | general | programming, reasoning",

    # ── Standard tier (128-131K context) ───────────────────────────────────
    "nvidia/nemotron-3-nano-30b-a3b:free": "256K | general | tools",
    "minimax/minimax-m2.5:free":     "197K | general | tools, strong generalist",
    "openai/gpt-oss-120b:free":      "131K | general | OpenAI open-weight",
    "openai/gpt-oss-20b:free":       "131K | general | OpenAI open-weight, fast",
    "z-ai/glm-4.5-air:free":        "131K | general | tools, fast",
    "meta-llama/llama-3.3-70b-instruct:free": "66K | general | tools, Meta",
    "meta-llama/llama-3.2-3b-instruct:free":  "131K | general | lightweight",
    "nousresearch/hermes-3-llama-3.1-405b:free": "131K | general | 405B params",
    "baidu/cobuddy:free":            "131K | general | tools",
    "poolside/laguna-xs.2:free":     "131K | general | tools",
    "poolside/laguna-m.1:free":      "131K | general | tools",

    # ── Lightweight tier (33K context) ──────────────────────────────────────
    "liquid/lfm-2.5-1.2b-thinking:free":  "33K | reasoning | thinking, tiny",
    "liquid/lfm-2.5-1.2b-instruct:free":  "33K | general | tiny, fast",
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free": "33K | general | uncensored",

    # ── Vision / multimodal ────────────────────────────────────────────────
    "nvidia/nemotron-nano-12b-v2-vl:free": "128K | multimodal | vision+tools",
    "google/lyria-3-pro-preview":    "1.0M | vision | (not :free, listed for ref)",
    "baidu/qianfan-ocr-fast:free":   "66K | vision | OCR",

    # ── Auto-router ────────────────────────────────────────────────────────
    "openrouter/free":               "200K | auto | auto-selects best free model",
}

# All model IDs with :free suffix (for validation)
OPENROUTER_FREE_MODEL_IDS = [
    k for k in OPENROUTER_FREE_MODELS.keys() if k.endswith(":free")
]


def get_model_for_task(task: str, fallback: str = None) -> str:
    """
    Zwróć nazwę modelu dla danego typu zadania i aktywnego dostawcy.

    Args:
        task: Typ zadania — 'placement', 'lesson', 'conversation', 'news',
              'pronunciation', 'code', 'reasoning', 'multimodal'
        fallback: Model używany jeśli task nieznany

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
    """
    Zwróć model OpenRouter dla danego zadania.

    Strategia:
    - Lekcie/rozmowy/newsy → jakościowe modele z długim kontekstem
    - Testy poziomujące/wymowa → szybkie, lekkie modele
    - Code/reasoning → specjalistyczne modele
    - Fallback → openrouter/free (auto-select)
    """
    if fallback is None:
        fallback = "openrouter/free"  # auto-select best free model

    mapping = {
        # ── Szybkie, lekkie (placement, pronunciation) ──────────────────
        "placement": "meta-llama/llama-3.2-3b-instruct:free",
        "pronunciation": "liquid/lfm-2.5-1.2b-instruct:free",

        # ── Jakościowe, kreatywne (długi context) ───────────────────────
        "lesson": "deepseek/deepseek-v4-flash:free",
        "conversation": "minimax/minimax-m2.5:free",
        "news": "google/gemma-4-26b-a4b-it:free",
        "test": "deepseek/deepseek-v4-flash:free",

        # ── Specjalistyczne ──────────────────────────────────────────────
        "code": "qwen/qwen3-coder:free",
        "reasoning": "nvidia/nemotron-3-super-120b-a12b:free",
        "multimodal": "google/gemma-4-26b-a4b-it:free",
    }

    return mapping.get(task, fallback)


def _get_gemini_model(task: str, fallback: str = None) -> str:
    """Zwróć model Gemini Direct API dla danego zadania."""
    if fallback is None:
        fallback = "gemini-2.0-flash"

    mapping = {
        "placement": "gemini-2.0-flash-lite",
        "lesson": "gemini-2.0-flash",
        "conversation": "gemini-2.0-flash",
        "news": "gemini-2.0-flash",
        "pronunciation": "gemini-2.0-flash-lite",
        "test": "gemini-2.0-flash",
        "code": "gemini-2.0-pro",
        "reasoning": "gemini-2.0-pro",
        "multimodal": "gemini-2.0-flash",
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
        # Return all :free models from the catalog
        return sorted(OPENROUTER_FREE_MODEL_IDS)


def validate_model(model_id: str) -> bool:
    """
    Sprawdź czy model jest w katalogu darmowych modeli OpenRouter.

    Args:
        model_id: Nazwa modelu do walidacji

    Returns:
        True jeśli model jest dostępny jako darmowy
    """
    return model_id in OPENROUTER_FREE_MODELS or model_id == "openrouter/free"
