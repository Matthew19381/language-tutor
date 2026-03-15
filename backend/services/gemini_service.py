import google.generativeai as genai
import json
import logging
from backend.config import settings

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")


async def generate_text(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        raise


async def generate_json(prompt: str) -> dict:
    full_prompt = prompt + "\n\nRespond ONLY with valid JSON, no markdown, no code blocks."
    try:
        response = model.generate_content(full_prompt)
        text = response.text.strip()

        # Clean up if model adds markdown code blocks
        if text.startswith("```"):
            parts = text.split("```")
            if len(parts) >= 2:
                text = parts[1]
                if text.startswith("json"):
                    text = text[4:]
                elif text.startswith("JSON"):
                    text = text[4:]

        text = text.strip()

        # Remove any trailing backticks
        if text.endswith("```"):
            text = text[:-3].strip()

        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}. Raw response: {text[:500]}")
        raise ValueError(f"Invalid JSON response from Gemini: {e}")
    except Exception as e:
        logger.error(f"Error generating JSON: {e}")
        raise
