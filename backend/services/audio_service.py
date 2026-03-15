import edge_tts
import asyncio
import os
import logging

logger = logging.getLogger(__name__)

# Voice map for languages
VOICE_MAP = {
    "German": "de-DE-KatjaNeural",
    "English": "en-US-JennyNeural",
    "French": "fr-FR-DeniseNeural",
    "Spanish": "es-ES-ElviraNeural",
    "Italian": "it-IT-ElsaNeural",
    "Portuguese": "pt-BR-FranciscaNeural",
    "Dutch": "nl-NL-ColetteNeural",
    "Polish": "pl-PL-ZofiaNeural",
    "Russian": "ru-RU-SvetlanaNeural",
    "Japanese": "ja-JP-NanamiNeural",
    "Chinese": "zh-CN-XiaoxiaoNeural",
    "Korean": "ko-KR-SunHiNeural",
}

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "audio")


def ensure_audio_dir():
    """Ensure the audio directory exists."""
    os.makedirs(AUDIO_DIR, exist_ok=True)


async def generate_audio(text: str, language: str, output_path: str) -> str:
    """Generate audio for the given text using edge-tts."""
    ensure_audio_dir()
    voice = VOICE_MAP.get(language, "en-US-JennyNeural")

    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        logger.info(f"Audio generated: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        raise


async def generate_vocabulary_audio(
    vocabulary: list,
    language: str,
    lesson_id: int
) -> list:
    """Generate audio for vocabulary words in a lesson."""
    ensure_audio_dir()
    audio_files = []

    for i, vocab_item in enumerate(vocabulary):
        word = vocab_item.get("word", "")
        if not word:
            continue

        filename = f"lesson_{lesson_id}_vocab_{i}_{word[:20].replace(' ', '_')}.mp3"
        output_path = os.path.join(AUDIO_DIR, filename)

        # Skip if already exists
        if os.path.exists(output_path):
            audio_files.append({
                "word": word,
                "audio_path": f"/audio/{filename}"
            })
            continue

        try:
            await generate_audio(word, language, output_path)
            audio_files.append({
                "word": word,
                "audio_path": f"/audio/{filename}"
            })
        except Exception as e:
            logger.warning(f"Could not generate audio for word '{word}': {e}")
            audio_files.append({
                "word": word,
                "audio_path": None
            })

    return audio_files


async def generate_dialogue_audio(
    dialogue_lines: list,
    language: str,
    lesson_id: int
) -> list:
    """Generate audio for dialogue lines."""
    ensure_audio_dir()
    audio_files = []

    # Use different voices for Speaker A and B
    voices = {
        "A": VOICE_MAP.get(language, "en-US-JennyNeural"),
        "B": get_alternate_voice(language)
    }

    for i, line in enumerate(dialogue_lines):
        speaker = line.get("speaker", "A")
        text = line.get("text", "")
        if not text:
            continue

        filename = f"lesson_{lesson_id}_dialogue_{i}.mp3"
        output_path = os.path.join(AUDIO_DIR, filename)

        if os.path.exists(output_path):
            audio_files.append({
                "speaker": speaker,
                "text": text,
                "audio_path": f"/audio/{filename}"
            })
            continue

        try:
            voice = voices.get(speaker, VOICE_MAP.get(language, "en-US-JennyNeural"))
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            audio_files.append({
                "speaker": speaker,
                "text": text,
                "audio_path": f"/audio/{filename}"
            })
        except Exception as e:
            logger.warning(f"Could not generate dialogue audio: {e}")
            audio_files.append({
                "speaker": speaker,
                "text": text,
                "audio_path": None
            })

    return audio_files


def get_alternate_voice(language: str) -> str:
    """Get an alternate voice for the second speaker."""
    alternate_voices = {
        "German": "de-DE-ConradNeural",
        "English": "en-US-GuyNeural",
        "French": "fr-FR-HenriNeural",
        "Spanish": "es-ES-AlvaroNeural",
        "Italian": "it-IT-DiegoNeural",
        "Portuguese": "pt-BR-AntonioNeural",
        "Dutch": "nl-NL-MaartenNeural",
        "Polish": "pl-PL-MarekNeural",
    }
    return alternate_voices.get(language, "en-US-GuyNeural")


async def generate_flashcard_audio(
    word: str,
    language: str,
    flashcard_id: int
) -> str:
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
