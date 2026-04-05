import json
import logging
import httpx
import contextvars
import functools
from backend.config import settings

logger = logging.getLogger(__name__)

_OLLAMA_URL = f"{settings.OLLAMA_BASE_URL}/chat/completions"
_MODEL = settings.OLLAMA_MODEL

# ContextVar for per-request model override (async-safe)
_model_override: contextvars.ContextVar[str] = contextvars.ContextVar('model_override', default=None)


def set_model_override(model: str):
    """Set the model for the current async context."""
    _model_override.set(model)


def reset_model_override(token):
    """Reset the model to previous value."""
    _model_override.reset(token)


def with_model(task: str):
    """
    Decorator for AI-generating functions.
    Sets the appropriate Ollama model for the duration of the function call.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, model=None, **kwargs):
            if model is None:
                from backend.services.model_router import get_model_for_task
                model = get_model_for_task(task)
            token = set_model_override(model)
            try:
                return await func(*args, **kwargs)
            finally:
                reset_model_override(token)
        return wrapper
    return decorator


async def generate_text(prompt: str, model: str = None) -> str:
    # Use context override if no explicit model provided
    if model is None:
        model = _model_override.get() or _MODEL
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(_OLLAMA_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error generating text via Ollama: {e}")
            raise


async def generate_json(prompt: str, model: str = None) -> dict:
    # Use context override if no explicit model provided
    if model is None:
        model = _model_override.get() or _MODEL
    full_prompt = prompt + "\n\nRespond ONLY with valid JSON, no markdown, no code blocks."
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": full_prompt}],
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(_OLLAMA_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"].strip()

            # Strip markdown fences if model adds them
            if text.startswith("```"):
                parts = text.split("```")
                if len(parts) >= 2:
                    text = parts[1]
                    if text.lower().startswith("json"):
                        text = text[4:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}. Raw response: {text[:500]}")
            raise ValueError(f"Invalid JSON response from Ollama: {e}")
        except Exception as e:
            logger.error(f"Error generating JSON via Ollama: {e}")
            raise
