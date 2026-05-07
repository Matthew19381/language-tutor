# LinguaAI - User Guide

## Getting Started

### 1. Create an Account

1. Open the app at `http://localhost:5173`
2. Click **"Rozpocznij naukę"**
3. Enter your name, native language, and target language
4. Complete the 20-question placement test
5. Receive your CEFR level and personalized study plan

### 2. Daily Lesson

- A new lesson is generated every day based on your CEFR level
- Complete the lesson to earn **+25 XP**
- Lessons include: vocabulary, grammar, reading, and output forcing

### 3. Tests

| Test Type | When | XP Reward |
|-----------|------|-----------|
| Daily Test | After each lesson | score × 0.5 (max 50) |
| Weekly Test | Every 7 days | score × 0.5 (max 50) |
| Placement Test | When changing language | Determines CEFR level |

### 4. Spaced Repetition Flashcards

- Review flashcards daily for vocabulary retention
- The system adjusts review intervals based on your performance (SM-2 algorithm)
- Export to Anki format if needed

### 5. Conversation Practice

- Practice speaking with AI conversation partner
- Get real-time feedback on grammar and vocabulary
- Analysis available after each session

### 6. News Reading

- Simplified news articles based on your CEFR level
- Switch languages using the language selector
- Articles are fetched from RSS feeds and simplified by AI

## CEFR Levels

| Level | Name (Polish) | Description |
|-------|-----------------|-------------|
| A1 | Początkujący | Beginner - basic phrases |
| A2 | Podstawowy | Elementary - simple sentences |
| B1 | Średni | Intermediate - familiar topics |
| B2 | Zaawansowany | Upper-intermediate - complex texts |
| C1 | Zaawansowany+ | Advanced - nuanced meaning |
| C2 | Mistrz | Mastery - near-native fluency |

## Achievements

Earn XP to level up and unlock achievements!

- **Level curve**: Level `n` requires `(n-1)² × 20` total XP
- **50 levels** total
- Achievements are displayed as toast notifications when unlocked

## Multiple Languages

You can learn multiple languages simultaneously:

1. Go to your profile
2. Click "Change Language"
3. Complete a placement test for the new language
4. Switch between languages anytime

Your progress is tracked separately for each language.

## Tips

- **Streak**: Log in daily to maintain your streak
- **Output Forcing**: Practice producing language, not just recognizing it
- **Interleaved Review**: Previous topics are mixed into new lessons
- **Comprehensible Input**: Reading materials are +1 level above your current

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + Enter` | Submit answer |
| `Esc` | Close modal |
| `1-4` | Select multiple choice answer |

## Troubleshooting

**Lesson not loading?**
- Check that the backend is running on `http://localhost:8000`
- Verify your `GEMINI_API_KEY` is set in `backend/.env`

**Audio not playing?**
- Ensure backend is running
- Check browser console for CORS errors

**Flashcards not showing?**
- Complete at least one lesson to generate flashcards
- Check the "Flashcards" tab in the navigation
