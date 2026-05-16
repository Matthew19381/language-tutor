# LinguaAI — User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Daily Lessons](#daily-lessons)
3. [Tests](#tests)
4. [Flashcards (Spaced Repetition)](#flashcards-spaced-repetition)
5. [Conversation Practice](#conversation-practice)
6. [Voice Chat](#voice-chat)
7. [News Reading](#news-reading)
8. [Pronunciation Trainer](#pronunciation-trainer)
9. [YouTube Videos](#youtube-videos)
10. [Error Review](#error-review)
11. [Quick Mode](#quick-mode)
12. [XP & Levels](#xp--levels)
13. [Achievements](#achievements)
14. [Multiple Languages](#multiple-languages)
15. [Google Drive Backup](#google-drive-backup)
16. [Keyboard Shortcuts](#keyboard-shortcuts)
17. [Troubleshooting](#troubleshooting)
18. [FAQ](#faq)

---

## Getting Started

### 1. Create Your Profile

1. Open the app at `http://localhost:5173`
2. Click **"Start Learning"**
3. Enter your name, native language, and target language
4. Complete the 20-question placement test
5. Receive your CEFR level and personalized study plan

> **Tip:** Don't stress about the placement test. If the result doesn't match your expectations, you can retake it or change your level in Settings.

### 2. Navigation

The app has the following sections (in order):
**Home → Lesson → Pronunciation → Speak → Flashcards → Test → News → Videos → Timer → Stats**

---

## Daily Lessons

A new lesson is generated every day based on your CEFR level and recent progress.

**Lesson structure:**
1. **Vocabulary** — new words with translations and example sentences
2. **Grammar** — rules explained with examples (Markdown formatted)
3. **Comprehensible Input (i+1)** — reading material slightly above your current level, with new words highlighted
4. **Interleaved Review** — mixed review of topics from the last 7 days
5. **Output Forcing** — hide-and-recall exercise (hide text, try to reproduce from memory)

**Scoring:** +25 XP per completed lesson

### Audio Playback
- Click the **Play** button next to any text section
- Audio is generated in real-time using edge-tts
- Available for: vocabulary, grammar, dialogues, reading, error review

### PDF Export
1. Open a completed lesson
2. Click **"Export PDF"**
3. File includes vocabulary table and lesson content

---

## Tests

| Test Type | When | Max XP |
|-----------|------|--------|
| Daily Test | Every day (based on lesson) | 50 |
| Weekly Test | Every 7 days (full week review) | 50 |
| Placement Test | When changing language | — |

**Scoring:** `score × 0.5` XP (max 50 XP per test)

After completing a test, you can:
- Review errors with AI-generated explanations
- Generate flashcards from mistakes
- Regenerate a new test incorporating your errors

---

## Flashcards (Spaced Repetition)

The flashcard system uses spaced repetition to optimize long-term retention.

### How it works:
- The algorithm schedules reviews based on your performance
- Well-known cards appear less frequently
- Difficult cards return more often

### Reviewing flashcards:
1. Go to the **Flashcards** tab
2. Cards due for today are shown automatically
3. Click a card to flip it (front → back)
4. Rate your recall (0–5):
   - **0–2**: Poor — card returns soon
   - **3–4**: Good — standard interval
   - **5**: Perfect — longer interval

**Scoring:** +2 XP per review

### Adding flashcards:
- Type a word/phrase → AI generates the rest automatically
- Add from reading (click any word in Comprehensible Input)
- Add from errors (Error Review → "Generate flashcards from errors")

### Export to Anki:
1. Go to **Flashcards**
2. Click **"Export to Anki"**
3. Download the `.apkg` file and import into Anki

---

## Conversation Practice

Practice speaking with an AI conversation partner powered by Google Gemini.

### Starting a conversation:
1. Go to the **Conversation** tab
2. Type your message or use the microphone (Web Speech API)
3. AI responds with text and voice (TTS)
4. Get real-time grammar corrections and vocabulary suggestions

### Features:
- **Grammar corrections** — AI highlights mistakes and provides correct forms
- **Vocabulary suggestions** — better word choices
- **Session analysis** — after the conversation, get a detailed evaluation
- **Editable system prompt** — customize the AI's behavior in Stats → Voice Chat Prompt

---

## Voice Chat

Have a voice conversation with AI directly in the browser.

### How it works:
1. Go to the **Conversation** tab
2. Click the microphone icon to record your message
3. AI responds with text and voice (TTS)
4. Edit the system prompt in **Stats** → **Voice Chat Prompt**

### Requirements:
- Browser with Web Speech API support (Chrome, Edge)
- Microphone access
- Backend running on `http://localhost:8001`

---

## News Reading

Read simplified news articles matched to your CEFR level.

### Features:
- Fetched from RSS feeds (BBC, CNN, etc.)
- Simplified by AI using the i+1 method
- New vocabulary highlighted
- Full article audio playback
- Daily cache (per language)

---

## Pronunciation Trainer

Improve your pronunciation using **faster-whisper** speech recognition.

### How it works:
1. Go to the **Pronunciation** tab
2. Select a reference phrase or type your own
3. Click the microphone and speak
4. Get transcription and scoring:
   - **Word-level score** (0–100%)
   - **Phoneme highlighting**
   - **Overall feedback** and tips

> **Tip:** Record in a quiet environment for best results.

---

## YouTube Videos

Learn through YouTube videos matched to your level.

### Features:
- Search educational videos
- Filter by CEFR level
- Access transcripts
- Listen to selected fragments
- Toggle: target language only vs. target language + native language subtitles

---

## Error Review

The **Errors** section in Stats collects all your mistakes from tests, lessons, and conversations.

### Features:
- **Error categories**: Grammar, Comprehension, Pronunciation, Conversation — each expandable with improvement tips
- **Generate flashcards from errors** — automatically creates flashcards from questions you got wrong
- **Generate test from errors** — creates a new test focusing on your weak areas
- **Conversation analysis** — paste a voice chat summary → AI evaluates pronunciation and fluency

---

## Quick Mode

Short on time? Use **Quick Mode** for a focused 15-minute session.

### How it works:
1. Go to the **Timer** tab
2. Choose duration: 5, 10, 15, 20, or 30 minutes
3. AI generates a quick activity plan
4. Timer badge stays visible in the bottom-right corner (persists across tab switches)

### Features:
- Custom duration (5–30 minutes)
- Last 5 seconds: counter enlarges and blinks red
- Timer continues even when switching tabs

---

## XP & Levels

### Levels (1–50)

Level progression follows a quadratic curve:
```
Level n requires: (n-1)² × 20 total XP
```

| Level | Total XP | | Level | Total XP |
|-------|----------|-|-------|----------|
| 1     | 0        | | 10    | 1,620    |
| 2     | 20       | | 20    | 7,220    |
| 5     | 320      | | 30    | 16,820   |
| 10    | 1,620    | | 50    | 48,020   |

### Earning XP

| Action | XP |
|--------|-----|
| Complete lesson | +25 |
| Daily test (max) | +50 |
| Weekly test (max) | +50 |
| Flashcard review | +2 |
| Conversation (10 messages) | +15 |

---

## Achievements

Unlock achievements by reaching milestones:
- **Fast Learner** — Complete 10 lessons
- **Test Master** — Score 90%+ on 5 tests
- **Streak Champion** — Study 7 days in a row
- **Level Up!** — Reach the next level

Achievements appear as toast notifications (auto-dismiss after 4 seconds).

---

## Multiple Languages

Learn multiple languages simultaneously:

1. Go to **Stats**
2. Click on a different language
3. Complete a placement test for the new language
4. Switch between languages anytime

Progress is tracked separately for each language.

---

## Google Drive Backup

Back up your progress to Google Drive.

### Setup:
1. Go to **Stats** → **Settings**
2. Click **"Connect to Google Drive"**
3. Authorize the app
4. Choose backup frequency (daily/weekly)

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + Enter` | Submit answer |
| `Esc` | Close modal |
| `1-4` | Select multiple choice answer |
| `Space / Enter` | Flip flashcard |
| `← →` | Previous / Next flashcard |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Lesson not loading | Check backend is running on `http://localhost:8001` |
| Audio not playing | Check browser supports Web Audio API; check console (F12) for CORS errors |
| Pronunciation not working | Check microphone permissions; use Chrome/Edge |
| Test won't submit | Refresh page, check internet connection |
| No new achievements | Check Stats → Achievements tab |
| Voice Chat not responding | Verify `GEMINI_API_KEY` is set in `backend/.env` |
| Error 429 (Too Many Requests) | Too many requests — wait a moment and retry |
| Error 403 | You're trying to access another user's resources |

---

## FAQ

**Q: Can I learn more than one language?**
A: Yes! Switch between languages in the Stats tab. Progress is tracked separately per language.

**Q: How do I change my CEFR level?**
A: Retake the placement test in Stats, or start learning a new language.

**Q: Is my data safe?**
A: All data is stored locally in a SQLite database on your machine. The app only communicates with the Gemini API for content generation.

**Q: How do I back up my data?**
A: Go to **Stats** → **Settings** → **Backup**. You can also connect to Google Drive.

**Q: Why is my lesson the same as yesterday?**
A: Lessons are generated once per day. Click "Next Lesson" in the Lesson tab for a new one.

**Q: How do I export flashcards to Anki?**
A: Go to **Flashcards** → **Export to Anki**. The `.apkg` file downloads automatically.

**Q: Can I use the app offline?**
A: No — an internet connection is required for the Gemini API (lesson generation, tests, conversations).
