# CHANGELOG — LinguaAI

Format: newest first. Każdy wpis: wersja (jeśli dotyczy) + data + opis.

---

## 2026-03-26

### Fix: Audio, UI, Logika zakładek
- **audio_service.py** — retry 3x z backoff dla błędów edge-tts 403
- **achievement_service.py** — wszystkie osiągnięcia przetłumaczone na polski
- **lesson_generator.py** — tipy generowane w native_language (wzmocniony prompt)
- **routers/lessons.py** — concept-flashcards: czytelny błąd gdy AI zwraca 0 konceptów
- **DailyLesson.jsx** — renderMarkdown: obsługa `#`, `##`, `###`, `**bold**`, list
- **DailyLesson.jsx** — dialog: układ lewa/prawa na podstawie pola `speaker`
- **placement.py** — needs_placement: True tylko dla nowych języków (`was_new`)
- **Stats.jsx** — zmiana języka: natychmiastowy reload, czyszczenie lesson cache
- **Stats.jsx** — TodayCompletion: reaktywny useState, odświeżanie na focus
- **DailyTest.jsx** — cache pytań testu w localStorage (nie regeneruje się przy re-wejściu)

---

## Wcześniej (przed 2026-03-26)

Historia commitów w git: `git log --oneline`
