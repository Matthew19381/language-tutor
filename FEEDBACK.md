# Language Tutor — Feedback użytkownika (2026-03-23)

## Krytyczne — do naprawy w pierwszej kolejności

### Model AI
- [x] Zweryfikowano: Aplikacja używa **Ollama** (qwen2.5:7b, llama3.1, deepseek-coder-v2:16b) zamiast Gemini. Task router wybiera model w zależności od zadania. Jest to darmowe, lokalne rozwiązanie — najlepszy wybór.
- [x] Zmienić interfejs na **polski** (cały UI po angielsku — nie do zaakceptowania)

### Test poziomujący
- [x] Test jest za łatwy i intuicyjny — poprawiono: 20 pytań z lepszą dystrybucją CEFR, bardziej restrykcyjne reguły (bez cognatów, bez podpowiedzi w pytaniach), konserwatywna kalibracja (fallback: <20% → A1, <40% → A1, <55% → A2)

---

## Zakładka: Lekcja

### Pozytywne
- Zakładka ogólnie fajna
- Możliwość pobrania lekcji lokalnie lub na Google Drive (4 dni) — świetne

### Do poprawy
- [x] Słownictwo: dodać tłumaczenie przykładowego zdania ✅
- [x] Dialog: układ 1 osoba po lewej / 1 osoba po prawej ✅
- [x] Ćwiczenia: bardziej zróżnicowane ✅
- [x] Zadanie produkcyjne: sprawdzanie odpowiedzi przez AI ✅
- [x] Wymuszanie produkcji: zapamiętywanie 5 długich zdań ✅
- [x] **Audio dla całej lekcji** ✅

---

## Zakładka: Czytanie
- [x] Opcja kopiowania słowa/zdania → automatyczne tworzenie fiszki przez AI ✅ (text selection popup w News.jsx)

---

## Zakładka: Fiszki
- [x] Dodawanie fiszki: tylko wpisanie słowa/frazy → reszta generowana przez AI ✅ (add-ai endpoint)
- [x] Filtr fiszek po dacie dodania ✅ (dateFilter: today/week/month)
- [x] Fiszki nie odzwierciedlają poziomu słownictwa ✅ (CEFR filter w Flashcards.jsx)
- [x] Tłumaczenie przykładowego zdania ✅ (example_translation)
- [x] Audio dla fiszek ✅ (PlayButton + generate_audio endpoint)
- [x] Zweryfikować bazę danych: czy postępy są zapisywane? ✅ (FSRS fields poprawnie zapisywane)

### Pozytywne
- Przegląd i eksport do Anki — dobry
- Fiszki pięknie zbudowane

---

## Zakładka: Mów
- [x] Analiza z zakładki Mów powinna być uwzględniana przez system w dalszej nauce ✅ (errors → TestResult)
- Ogólnie fajna funkcja, zakończenie i analiza szczególnie dobre

---

## Zakładka: News
- Świetnie zrobiona — dodawanie słownictwa do fiszek, pytania do artykułu, link do oryginału

---

## Zakładka: Wymowa
- [x] Plik audio wskazujący poprawną wymowę zdania ✅ (PlayButton na zdaniach w PronunciationTrainer.jsx)
- [x] Podsumowanie odnośnie wymowy ✅ (session summary z avg/best score, problem words)
- [ ] Filmy z internetu (polskie i angielskie akceptowane)

---

## Zakładka: Statystyki
- [x] Wskaźnik ukończenia lekcji ✅ (TodayCompletion component)
- [x] Fiszki w statystykach: pole do ręcznego odhaczenia (użytkownik korzysta też z Anki) ✅ (checkbox "Powtórzone w Anki" w Stats.jsx, localStorage)
- [x] Wskazówki dzienne: generować raz dziennie przy pierwszym wejściu ✅ (localStorage caching)
- [x] Z czasem: dodać więcej osiągnięć ✅ (57 achievement types)
- Analiza błędów — dobra, ale potrzebuje więcej pól
- Dzienne wskazówki poparte nauką — świetne

---

## Tryb 15-Minutowy
- [x] Bug: minutnik zatrzymuje się i nie jest widoczny po kliknięciu w inną zakładkę ✅ (QuickMode niezależny od tab focus)
- [x] Dodać opcję własnego czasu (np. 30 min) ✅ (custom input 1-120 min + presets 5/10/15/20/30/45/60)
- [x] Flashcard Review w trybie 15-min: do przemyślenia ✅ (użytkownik korzysta z Anki — OK)

---

## Ustawienia
- [x] Dodać możliwość zmiany języka nauki ✅ (Stats.jsx grid 5 języków + updateUserLanguage endpoint)

---

## Rozmowa głosowa
- [x] Dodać generator promptu dla Voice Chat ✅ (getVoiceChatPrompt endpoint)
- [x] Dialog: opcja rozmowy z audio (model odpowiada głosem) + opcja wpisywania ręcznego ✅ (voiceMode + sendVoiceMessage)

---

## Pytanie otwarte
- Czy zmienić model AI w projekcie? — do decyzji

---

## 2026-04-06 — Updates

### Deployment resolved (partial)
- ✅ **Unicode bug workaround**: npm blocked on G:\ path with Polish chars → frontend node_modules moved to `C:\LinguaAI` temporarily
- ✅ **App running**: Backend (8001, from G:\), Frontend (5173, from C:\), Ollama (11434)
- ⚠️ **Split deployment**: Backend and source on G:\, frontend runtime on C:\ — **not ideal**, needs permanent rename
- ✅ **All P0-P3 features verified**: 63 tasks complete, app fully functional

### Feedback items status
- [x] **Test poziomujący** — poprawiona kalibracja (2026-05-17)
- [x] **Słownictwo: tłumaczenie przykładu** ✅
- [x] **Timer bug** ✅
- [x] **Fiszki audio** ✅
- [x] **Wskazówki dzienne caching** ✅

### Decision log
- **ADR-002**: Unicode Path Handling — accept split deployment temporarily, plan rename to ASCII path within 7 days

### Next steps (from TASKS Backlog)
1. Rename project folder to ASCII-only path (permanent fix)
2. Build production frontend container (nginx) for Docker
3. Implement automated test suite (pytest + Playwright)
4. Daily DB backup automation
5. User documentation (Getting Started guide)
