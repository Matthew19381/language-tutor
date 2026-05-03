# TASKS — LinguaAI

_Ostatnia aktualizacja: 2026-04-05_
_Źródła: FEEDBACK.md, własne implementacje_

---

## P0 — Krytyczne (blokują użycie aplikacji)

- [x] **AUDIO-1** — Audio nie działa: edge-tts zwraca 403. Dodano retry 3x z exponential backoff (0.5s/1s/2s). ✅ (2026-03-26)
- [x] **AUDIO-2** — PlayButton dodany do: gramatyka (explanation), fiszki (słowo front+back), newsy (simplified_text), wymowa (fraza/custom). Dialog i słownictwo już miały. ✅ (2026-03-26)
- [x] **UI-1** — Nazwy języków spolszczone (German→Niemiecki itd.) w Stats, PlacementTest, Home, QuickMode. LANG_DISPLAY map per plik. ✅ (2026-03-26)
- [x] **LESSON-1** — useState(true) powodował flash spinnera przy powrocie. Fix: lazy initializer z readLessonCache() — loading=false i lesson=dane od razu przy mount. ✅ (2026-03-26)
- [x] **LESSON-2** — get_day_number liczyło wszystkie lekcje (nie tylko ukończone). Fix: liczenie tylko is_completed=True + sprawdzenie nieukończonych lekcji z poprzednich dni. ✅ (2026-03-26)

---

## P1 — Wysokie (funkcje zepsute)

- [x] **TEST-1** — Cache pytań testu w localStorage per dzień/język. ✅ (2026-03-26)
- [x] **TEST-2** — Prompt wzmocniony: zakaz dawania odpowiedzi w treści pytania, zakaz ujawniania tłumaczenia. ✅ (2026-03-26)
- [x] **TEST-3** — Prompt: fill_blank musi mieć DOKŁADNIE JEDNO ___ — nie więcej. ✅ (2026-03-26)
- [x] **TEST-4** — Placement test calibration: stricter scoring (A1 <30%, B1 <65%), conservative AI analysis — FIXED 2026-05-03
- [x] **TIMER-1** — Już zaimplementowany: Layout.jsx ma globalny badge (quickmode_start z localStorage), niezależny od stanu QuickMode. Timer nie zatrzymuje się przy zmianie zakładki. ✅ (2026-03-26)
- [x] **STATS-1** — TodayCompletion: reaktywny useState + odświeżanie na focus okna. 4 aktywności: Lekcja, Test, Rozmowa, Newsy/Wymowa. ✅ (2026-03-26)
- [x] **ERRORS-1** — Backend (stats.py) zwracał error/correction zamiast user_answer/correct_answer. Fix: nowe pola question/user_answer/correct_answer w get_all_errors + UI ErrorReview.jsx. ✅ (2026-03-26)
- [x] **GRAMMAR-1** — Wyjaśnienie gramatyki: dodano `renderMarkdown()` obsługujący `#/##/###`, `**bold**`, listy. ✅ (2026-03-26)
- [x] **FLASHCARD-BTN** — Backend zwraca teraz czytelny komunikat gdy AI nie generuje konceptów. ✅ (2026-03-26)

---

## P2 — Średnie (funkcje niekompletne)

- [x] **LANG-1** — Usunięto 1.5s setTimeout — zmiana języka przeładowuje stronę natychmiast. ✅ (2026-03-26)
- [x] **LANG-2** — Naprawiono needs_placement: was_new rejestrowane PRZED zapisem profilu. ✅ (2026-03-26)
- [x] **LANG-3** — Zweryfikowano: language_profiles[lang] przechowuje CEFR per język, przywracany przy zmianie. ✅ (2026-03-26)
- [x] **LANG-4** — Zweryfikowano: lesson_cache_{userId}_{lang}_{date}, news cache (user_id, language), tips czyszczone przy zmianie języka. ✅ (2026-03-26)
- [x] **TIPS-1** — Zweryfikowano: Home.jsx i Stats.jsx mają `return` przy cache hit — API nie jest wywoływane ponownie tego samego dnia. ✅ (2026-03-26)
- [x] **TIPS-2** — Prompt wzmocniony: CRITICAL - pisz w {native_language}. ✅ (2026-03-26)
- [x] **DIALOG-1** — Układ dialogu: naprawiono — teraz używa pola `speaker` zamiast alternującego indeksu. ✅ (2026-03-26)
- [x] **FLASHCARD-1** — Zweryfikowano: filtr daty (today/week/month) i filtr dnia lekcji już są w Flashcards.jsx. ✅ (2026-03-26)
- [x] **FLASHCARD-2** — Fiszki: AI sprawdza poprawność wpisanego słowa przed dodaniem do zbioru (żeby nie utrwalać błędów). ✅ (2026-03-26)
- [x] **FLASHCARD-3** — Fiszki: opcja dodania polskiego słowa na przód / niemieckiego na tył (zamiast tylko niem→pol). ✅ (2026-03-26)
- [x] **FLASHCARD-4** — Nawigacja klawiaturą: Space/Enter=odwróć, ←→=poprzednia/następna, 1-4=ocena. ✅ (2026-03-26)
- [x] **FLASHCARD-5** — Zweryfikowano: backend sprawdza duplikaty i zwraca "Fiszka X już istnieje". ✅ (2026-03-26)
- [x] **LESSON-3** — Historia lekcji: wskaźnik ukończenia per lekcja. Zweryfikowano: zielone/szare kółko + ✓ w Stats.jsx lines 293-306. ✅ (2026-03-26)
- [x] **LESSON-4** — Generator przycisku "Następna lekcja" (nie "Wygeneruj nową — usuwa obecną"). Zweryfikowano: DailyLesson.jsx przycisk Następna lekcja → POST /api/lessons/next bez usuwania. ✅ (2026-03-26)
- [x] **LESSON-5** — Możliwość powrotu do wcześniejszych lekcji. Błędy z poprzednich lekcji uwzględniane w następnej. Zweryfikowano: route /lesson/:lessonId, Stats.jsx linki, generate_next_lesson już używa user_errors. ✅ (2026-03-26)
- [x] **LESSON-6** — Poprawiono matching: strip punctuation + prefix match (4 chars) + include match — łapie odmienione formy. ✅ (2026-03-26)
- [x] **LESSON-7** — Zweryfikowano: TranslationReveal już istnieje i jest używany w OutputForcingCard. ✅ (2026-03-26)
- [x] **LESSON-8** — W pobranych plikach: zawartość Gramatyka + Słownictwo + Dialog (bez reszty). Nazewnictwo folderu np. `Hiszpański_A1`. Integracja z Google Drive / Obsidian. ✅ (2026-03-26)
- [x] **LESSON-9** — Pobrana lekcja: 3 pliki audio (Gramatyka, Słownictwo, Dialog) + film dopasowany do poziomu i tematu. ✅ (2026-03-26)
- [x] **TEST-4** — Test: znacznie trudniejszy, powiązany z bieżącą lekcją. ✅ (2026-03-26)
- [x] **TEST-5** — Po zakończeniu testu: opcja regeneracji uwzględniająca błędy z podsumowania. ✅ (2026-03-26)
- [x] **ERRORS-2** — Zakładka Błędy: przyciski "Generuj fiszki z błędów" i "Generuj test z błędów". ✅ (2026-03-26)
- [x] **ERRORS-3** — Analiza błędów w Statystykach: więcej rubryk (Gramatyka, Rozumienie, Wymowa, Rozmowa), każda rozwijalna z opisem co poprawić. ✅ (2026-03-26)
- [x] **SPECIAL-CHARS** — SpecialCharHelper dodany do: textarea zadania produkcyjnego + textarea recall w OutputForcingCard. ✅ (2026-03-26)
- [x] **TRANSLATE-1** — Tłumacz: autodetect języka (cyrylica/inne → target→PL, reszta → PL→target), przycisk "Wytłumacz", "Dodaj do fiszek" po tłumaczeniu, zamknięcie przez klik poza. ✅ (2026-03-26)
- [x] **PRONUNCIATION-1** — Zakładka Wymowa: przycisk dodania zdania do fiszek. ✅ (2026-03-26)
- [x] **PRONUNCIATION-2** — Zakładka Wymowa: przycisk generowania nowych zdań do ćwiczenia. ✅ (2026-03-26)
- [x] **VIDEOS-1** — Zakładka Filmy: dodawanie ulubionych twórców (przycisk lub wpisanie nazwy). ✅ (2026-03-26)
- [x] **GROK-1** — Zweryfikowano: prompt po polsku (conversation.py), edytowalny textarea + przycisk kopiowania w Conversation.jsx. ✅ (2026-03-26)
- [x] **STATS-2** — Zweryfikowano: `flashcards` jest destrukturyzowane ale nie renderowane w Stats.jsx. ✅ (2026-03-26)
- [x] **STATS-3** — Usunięto przycisk CSV. Historia lekcji: wszystkie lekcje z backendu, domyślnie 7 ostatnich, "Pokaż wszystkie" toggle. ✅ (2026-03-26)

---

## P3 — Niskie (UI/UX dopracowanie)

- [x] **NAV-1** — Kolejność zakładek: Główna → Lekcja → Wymowa → Mów → Fiszki → Test → Newsy → Filmy → Timer → Statystyki → [tabela fiszek po prawej]. Zweryfikowano: NavBar.jsx lines 36-47 — kolejność identyczna. ✅ (2026-03-26)
- [x] **TIMER-2** — Timer: opcja własnego czasu (np. 30 min, nie tylko 15 min). Zweryfikowano: QuickMode.jsx — przyciski 5/10/15/20/30 min. ✅ (2026-03-26)
- [x] **TIMER-3** — Ostatnie 5 sekund: licznik się powiększa i miga na czerwono. Zweryfikowano: QuickMode.jsx — text-7xl + animate-blink gdy <=5s. ✅ (2026-03-26)
- [x] **TIMER-4** — Licznik czasu: 3x większy, po prawej na dole ekranu. Fix: Layout.jsx badge text-2xl → text-4xl. ✅ (2026-03-26)
- [x] **TIMER-5** — Usunąć "Flashcard Review" z trybu Timer (użytkownik korzysta z Anki). Zweryfikowano: quickmode.py nie ma fiszek w planie. ✅ (2026-03-26)
- [x] **HOME-1** — Zakładka Główna: usunąć "Fiszki do powtórki" z Aktywności. Usunięto ActionCard /flashcards z Home.jsx. ✅ (2026-03-26)
- [x] **HOME-2** — Sekcja Aktywności: zmienić nazwę z "Dzisiejsze Aktywności" na "Aktywności", zawierać wszystkie aktywności do nauki. Zweryfikowano: Home.jsx — już "Aktywności". ✅ (2026-03-26)
- [x] **SETTINGS-1** — Ustawienia: w liście języków nauki pokazywać aktualnie uczony język dla łatwego dostępu. Zweryfikowano: Stats.jsx — aktywny język ma indigo border/bg. ✅ (2026-03-26)
- [x] **HARDCORE** — Tryb Hardcore: zmienia język tylko częściowo — naprawić pełną zmianę na język uczony. Fix: settings.py _UI_EN uzupełniony o wszystkie brakujące klucze (home/test/conv/lesson/flash/pronun). ✅ (2026-03-26)
- [x] **ACHIEVEMENTS** — Wszystkie tytuły i opisy osiągnięć przetłumaczone na polski. ✅ (2026-03-26)
- [x] **FLASHCARD-TABLE** — Tabela szybkiego dodawania fiszek: widoczna na każdej zakładce (stały element layoutu), od razu pokazuje pole do wpisania po kliknięciu. Zweryfikowano: NavBar.jsx — inline input "Dodaj fiszkę..." na desktop (hidden md:flex). ✅ (2026-03-26)
- [x] **READING-COPY** — Zakładka Czytanie: opcja kopiowania słowa/zdania do tabeli → AI tworzy fiszkę automatycznie. ✅ (2026-03-26)
- [x] **MOW-ANALYSIS** — Analiza z zakładki Mów uwzględniana w systemie nauki i w Analizie błędów. ✅ (2026-03-26)
- [x] **ERRORS-4** — Zakładka Błędy: wklejenie podsumowania rozmowy z Grok → analiza i ocena wymowy/rozmowy. ✅ (2026-03-26)
- [x] **CONCEPTS** — Koncepcje gramatyczne: generowane do fiszek lub jako rozwijalna tabela w Statystykach. ✅ (2026-03-26)
- [x] **AI-MODEL** — Zweryfikować czy Gemini to najlepszy darmowy wybór (do decyzji). Gemini 2.0 Flash: darmowy tier, szybki, dobra jakość JSON. Alternatywy (GPT-4o-mini, Llama) wymagają płatnego API lub self-hosting. Decyzja: pozostać na Gemini 2.0 Flash. ✅ (2026-03-26)
- [x] **VOICE-1** — Rozpoznawanie mowy w konwersacji (Web Speech API). ✅ (2026-04-05)
- [x] **VOICE-2** — TTS (text-to-speech) na wiadomościach AI używając edge-tts. ✅ (2026-04-05)
- [x] **READ-SENTENCE** — Dodanie całego zdania do fiszek z sekcji czytania (comprehensible input). ✅ (2026-04-05)
- [x] **NEWS-CACHE** — Daily cache dla newsów w localStorage (language + user specific). ✅ (2026-04-05)
- [x] **VIDEOS-TOGGLE** — Toggle "Tylko język docelowy" vs "Język docelowy + polskie wyjaśnienia". ✅ (2026-04-05)

---

## Ukończone (wszystkie)

**Razem: 58 zadań P0-P3 + 6 nowych Phase 1-3 + 1 calibration fix = 64 zakończone.**

---

## FEEDBACK.md — Bugs to Fix

- [x] **PLACEMENT-CAL** — Placement test too easy, bad calibration → FIXED 2026-05-03 (stricter scoring + conservative AI analysis)
- [ ] **VOCAB-EXAMPLE** — Słownictwo: dodać tłumaczenie przykładowego zdania
- [ ] **DIALOG-LAYOUT** — Dialog: układ 1 osoba po lewej / 1 osoba po prawej (marked [x] in FEEDBACK but needs verification)
- [~] **EXERCISES-VARIETY** — Ćwiczenia: bardziej zróżnicowane → IN PROGRESS (prompt enforced: 5 unique types required) 2026-05-03
- [x] **PRODUCTION-TASK** — Zadanie produkcyjne: sprawdzanie odpowiedzi przez AI → FIXED 2026-05-03 (backend: /api/lessons/{id}/evaluate-production, frontend: UI with score/feedback/corrections)
- [x] **SENTENCE-MEMORY** — Wymuszenie produkcji: zapamiętywanie 5 długich zdań → FIXED 2026-05-03 (changed from 1-2 short sentences to 5 LONG sentences, 75-100 words total)
- [x] **AUDIO-LESSON** — Audio dla całej lekcji: treść, dialogi, czytanie, przegląd błędów, słownictwo → FIXED 2026-05-03 (backend: generate_full_lesson_audio, frontend: PlayButton for vocab/dialogue/reading/errors)
- [ ] **READING-COPY** — Opcja kopiowania słowa/zdania do tabeli widocznej w interfejsie → automatyczne tworzenie fiszki
- [x] **FLASHCARD-AUTO** — Dodawanie fiszki: tylko wpisanie słowa/frazy → reszta generowana przez AI → FIXED 2026-05-03 (backend: /flashcards/{id}/add-ai, frontend: addFlashcardAI)
- [x] **FLASHCARD-FILTER** — Filtr fiszek po dacie dodania → FIXED 2026-05-03 (frontend: dateFilter 'today'/'week'/'month', lessonFilter by day)
- [x] **FLASHCARD-VOCAB** — Fiszki nie odzwierciedlają poziomu słownictwa → FIXED 2026-05-03 (frontend: filterCards() + CEFR UI added, backend: cefr_level already set)
- [x] **FLASHCARD-AUDIO** — Audio dla fiszek → FIXED 2026-05-03 (backend: generate_flashcard_audio, frontend: PlayButton on each card)
- [~] **STATS-COMPLETION** — Wskaźnik ukończenia lekcji: przesuwać wraz z ukończeniem ćwiczeń → IN PROGRESS (frontend: flashcards added to TodayCompletion activities, needs backend completion check) 2026-05-03
- [ ] **STATS-FLASHCARDS** — Fiszki w statystykach: pole do ręcznego odhaczenia
- [ ] **STATS-TIPS** — Wskazówki dzienne: generować raz dziennie przy pierwszym wejściu
- [ ] **PRONUNCIATION-AUDIO** — Plik audio wskazujący poprawną wymowę zdania
- [ ] **PRONUNCIATION-SUMMARY** — Podsumowanie odnośnie wymowy
- [~] **TIMER-BUG** — Bug: minutnik zatrzymuje się i nie jest widoczny po kliknięciu w inną zakładkę → IN PROGRESS (Layout.jsx: visibilitychange listener added, QuickMode.jsx: timer recalculation) 2026-05-03
- [ ] **SETTINGS-LANG** — Dodać możliwość zmiany języka nauki
- [ ] **GROK-PROMPT** — Dodać generator promptu dla Grok
- [ ] **GROK-VOICE** — Dialog: opcja rozmowy z audio

---

## Backlog — Future Work

- [ ] **Unicode/npm permanent fix** — Rename project folder to ASCII-only path (e.g., `G:\Projects\LinguaAI`) or migrate to WSL2 to enable full Docker/dev workflow | 🔧 IN PROGRESS
- [x] **Port standardization** — Migrated: 8000→8001 ✅ 2026-05-03 (unified standard)
- [x] **API prefix standardization** — Migrated: /api/→/api/v1/ ✅ 2026-05-03 (unified standard)
- [x] **Docker frontend** — Build production-ready frontend container (nginx) and integrate with docker-compose (currently backend-only in Docker) — TODO
- [ ] **schemas/ directory** — Add Pydantic models for request/response validation ✅ 2026-05-03
- [ ] **Testy.exe** — Create automated test suite: pytest (backend API) + Playwright/Cypress (UI smoke tests)
- [ ] **Backup strategy** — Scheduled daily backup of `LinguaAI.db` with retention policy (7 days)
- [ ] **User documentation** — "Getting Started" guide with screenshots, FAQ (PDF/HTML)

---

## Wymagające decyzji / Otwarte

- [ ] **Finalny wybór architektury** — Dockeryzacja całego stacku vs. lokalne uruchamianie (backend+frontend z różnych ścieżek)
- [ ] **Ścieżki projektu** — rename folder na ASCII (prawidłowe rozwiązanie npm Unicode bug) — C:\LinguaAI lub G:\Projects\LinguaAI
- [ ] **Backup DB** — automatyzacja i lokalizacja backupów (cloud? lokalny NAS?)
- [ ] **Testy** — framework do wyboru (pytest + Playwright recommended)
- [ ] **Dokumentacja** — format (PDF vs online README) i poziom szczegółowości
