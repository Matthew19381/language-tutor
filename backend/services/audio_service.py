import asyncio
import os
import logging
from functools import partial

logger = logging.getLogger(__name__)

LANGUAGE_CODES = {
    "German": "de",
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "Italian": "it",
    "Portuguese": "pt",
    "Dutch": "nl",
    "Polish": "pl",
    "Russian": "ru",
    "Japanese": "ja",
    "Chinese": "zh-CN",
    "Korean": "ko",
}

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "audio")


def ensure_audio_dir():
    os.makedirs(AUDIO_DIR, exist_ok=True)


def _generate_audio_sync(text: str, lang_code: str, output_path: str):
    """Synchronous gTTS generation — run in thread pool."""
    from gtts import gTTS
    tts = gTTS(text=text, lang=lang_code, slow=False)
    tts.save(output_path)


async def generate_audio(text: str, language: str, output_path: str) -> str:
    """Generate audio for the given text using gTTS."""
    ensure_audio_dir()
    lang_code = LANGUAGE_CODES.get(language, "de")
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, partial(_generate_audio_sync, text, lang_code, output_path))
        logger.info(f"Audio generated: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        raise


async def generate_vocabulary_audio(vocabulary: list, language: str, lesson_id: int) -> list:
    """Generate audio for vocabulary words in a lesson."""
    ensure_audio_dir()
    audio_files = []

    for i, vocab_item in enumerate(vocabulary):
        word = vocab_item.get("word", "")
        if not word:
            continue

        filename = f"lesson_{lesson_id}_vocab_{i}_{word[:20].replace(' ', '_')}.mp3"
        output_path = os.path.join(AUDIO_DIR, filename)

        if os.path.exists(output_path):
            audio_files.append({"word": word, "audio_path": f"/audio/{filename}"})
            continue

        try:
            await generate_audio(word, language, output_path)
            audio_files.append({"word": word, "audio_path": f"/audio/{filename}"})
        except Exception as e:
            logger.warning(f"Could not generate audio for word '{word}': {e}")
            audio_files.append({"word": word, "audio_path": None})

    return audio_files


async def generate_dialogue_audio(dialogue_lines: list, language: str, lesson_id: int) -> list:
    """Generate audio for dialogue lines."""
    ensure_audio_dir()
    audio_files = []

    for i, line in enumerate(dialogue_lines):
        text = line.get("text", "")
        speaker = line.get("speaker", "A")
        if not text:
            continue

        filename = f"lesson_{lesson_id}_dialogue_{i}.mp3"
        output_path = os.path.join(AUDIO_DIR, filename)

        if os.path.exists(output_path):
            audio_files.append({"speaker": speaker, "text": text, "audio_path": f"/audio/{filename}"})
            continue

        try:
            await generate_audio(text, language, output_path)
            audio_files.append({"speaker": speaker, "text": text, "audio_path": f"/audio/{filename}"})
        except Exception as e:
            logger.warning(f"Could not generate dialogue audio: {e}")
            audio_files.append({"speaker": speaker, "text": text, "audio_path": None})

    return audio_files


async def generate_flashcard_audio(word: str, language: str, flashcard_id: int) -> str:
    """Generate audio for a single flashcard word."""
    ensure_audio_dir()
    filename = f"flashcard_{flashcard_id}_{word[:20].replace(' ', '_')}.mp3"
    output_path = os.path.join(AUDIO_DIR, filename)

    if os.path.exists(output_path):
        return f"/audio/{filename}"

    try:
        await generate_audio(word, language, output_path)
        return f"/audio/{filename}"
    except Exception as e:
        logger.error(f"Error generating flashcard audio: {e}")
        return None


async def generate_full_lesson_audio(lesson_content: dict, language: str, lesson_id: int) -> dict:
    """Generate audio for all lesson sections: vocabulary, dialogue, reading text, output forcing."""
    ensure_audio_dir()
    result = {}

    # Vocabulary words
    vocabulary = lesson_content.get("vocabulary", [])
    if vocabulary:
        try:
            vocab_audio = await generate_vocabulary_audio(vocabulary, language, lesson_id)
            result["vocabulary"] = vocab_audio
        except Exception as e:
            logger.warning(f"Vocab audio failed: {e}")

    # Dialogue lines
    dialogue = lesson_content.get("dialogue", [])
    if dialogue:
        try:
            dialogue_audio = await generate_dialogue_audio(dialogue, language, lesson_id)
            result["dialogue"] = dialogue_audio
        except Exception as e:
            logger.warning(f"Dialogue audio failed: {e}")

    # Reading practice (comprehensible_input)
    ci = lesson_content.get("comprehensible_input", {})
    ci_text = ci.get("text", "") if isinstance(ci, dict) else ""
    if ci_text:
        try:
            filename = f"lesson_{lesson_id}_reading.mp3"
            output_path = os.path.join(AUDIO_DIR, filename)
            if not os.path.exists(output_path):
                await generate_audio(ci_text[:500], language, output_path)
            result["reading"] = f"/audio/{filename}"
        except Exception as e:
            logger.warning(f"Reading audio failed: {e}")

    # Output forcing text
    of = lesson_content.get("output_forcing", {})
    of_text = of.get("text", "") or of.get("sentence", "") if isinstance(of, dict) else ""
    if of_text:
        try:
            filename = f"lesson_{lesson_id}_output_forcing.mp3"
            output_path = os.path.join(AUDIO_DIR, filename)
            if not os.path.exists(output_path):
                await generate_audio(of_text[:300], language, output_path)
            result["output_forcing"] = f"/audio/{filename}"
        except Exception as e:
            logger.warning(f"Output forcing audio failed: {e}")

    return result
