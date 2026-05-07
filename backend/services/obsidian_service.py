import logging
import os
from datetime import date

logger = logging.getLogger(__name__)

OBSIDIAN_DIR = os.path.join(os.path.dirname(__file__), "..", "exports", "obsidian")


def generate_obsidian_md(lesson_data: dict) -> str:
    """Generate Obsidian-compatible Markdown from lesson data.

    Exported content: Gramatyka + Słownictwo + Dialog only (core study material).
    """
    content = lesson_data.get("content", {})
    title = lesson_data.get("title", "Lesson")
    topic = lesson_data.get("topic", "General")
    cefr = lesson_data.get("cefr_level", "A1")
    language = lesson_data.get("language", "Unknown")
    day_number = lesson_data.get("day_number", 1)
    today = date.today().isoformat()

    lang_tag = language.lower().replace(" ", "-")

    lines = [
        "---",
        f"tags: [{lang_tag}, {cefr.lower()}, lekcja]",
        f"date: {today}",
        f"topic: {topic}",
        f"cefr: {cefr}",
        f"language: {language}",
        "---",
        "",
        f"# Lekcja {day_number}: {title}",
        "",
    ]

    # Grammar explanation
    explanation = content.get("explanation", "")
    if explanation:
        lines += [
            "## Gramatyka",
            "",
            explanation,
            "",
        ]

    # Vocabulary table
    vocabulary = content.get("vocabulary", [])
    if vocabulary:
        lines += [
            "## Słownictwo",
            "",
            "| Słowo | Tłumaczenie | Przykład |",
            "|-------|-------------|---------|",
        ]
        for item in vocabulary:
            word = item.get("word", "").replace("|", "\\|")
            translation = item.get("translation", "").replace("|", "\\|")
            example = item.get("example", "").replace("|", "\\|")
            lines.append(f"| {word} | {translation} | {example} |")
        lines.append("")

    # Dialogue
    dialogue = content.get("dialogue", {})
    if dialogue:
        lines += ["## Dialog", ""]
        if dialogue.get("context"):
            lines += [f"> {dialogue['context']}", ""]
        for line in dialogue.get("lines", []):
            speaker = line.get("speaker", "?")
            text = line.get("text", "")
            translation = line.get("translation", "")
            lines.append(f"**{speaker}:** {text}")
            if translation:
                lines.append(f"  *({translation})*")
        lines.append("")

    return "\n".join(lines)


def _folder_name(language: str, cefr: str) -> str:
    """Return folder name like 'Hiszpański_A1'."""
    safe_lang = "".join(c if c.isalnum() else "_" for c in language).strip("_")
    safe_cefr = cefr.replace(" ", "").replace("+", "plus")
    return f"{safe_lang}_{safe_cefr}"


def save_obsidian_md(lesson_data: dict, lesson_id: int) -> str:
    """Save Obsidian Markdown to file and return the file path.

    Files are saved in a subfolder named {Language}_{CEFR} (e.g. Hiszpanski_A1).
    """
    language = lesson_data.get("language", "Unknown")
    cefr = lesson_data.get("cefr_level", "A1")
    folder = _folder_name(language, cefr)
    dest_dir = os.path.join(OBSIDIAN_DIR, folder)
    os.makedirs(dest_dir, exist_ok=True)

    title = lesson_data.get("title", f"lesson_{lesson_id}")
    day_number = lesson_data.get("day_number", lesson_id)
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)[:50].strip()
    filename = f"Lekcja_{day_number:02d}_{safe_title}.md"
    filepath = os.path.join(dest_dir, filename)

    md_content = generate_obsidian_md(lesson_data)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)

    logger.info(f"Saved Obsidian markdown: {filepath}")
    return filepath
