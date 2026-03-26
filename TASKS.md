# TASKS — Language Tutor

_Ostatnia aktualizacja: 2026-03-26_
_Źródła: FEEDBACK.md + ZmianyTutor.txt (2026-03-18 → 2026-03-26)_

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
- [x] **TIMER-1** — Już zaimplementowany: Layout.jsx ma globalny badge (quickmode_start z localStorage), niezależny od stanu QuickMode. Timer nie zatrzymuje się przy zmianie zakładki. ✅ (2026-03-26)
- [x] **STATS-1** — TodayCompletion: reaktywny useState + odświeżanie na focus okna. 4 aktywności: Lekcja, Test, Rozmowa, Newsy/Wymowa. ✅ (2026-03-26)
- [x] **ERRORS-1** — Backend (stats.py) zwracał error/correction zamiast user_answer/correct_answer. Fix: nowe pola question/user_answer/correct_answer w get_all_errors + UI ErrorReview.jsx. ✅ (2026-03-26)
- [x] **GRAMMAR-1** — Wyjaśnienie gramatyki: dodano `renderMarkdown()` obsługujący `#/##/###`, `**bold**`, listy. ✅ (2026-03-26)
- [x] **FLASHCARD-BTN** — Backend zwraca teraz czytelny komunikat gdy AI nie generuje koncepcji. ✅ (2026-03-26)

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
- [ ] **LESSON-3** — Historia lekcji: wskaźnik ukończenia per lekcja.
- [ ] **LESSON-4** — Generator przycisku "Następna lekcja" (nie "Wygeneruj nową — usuwa obecną").
- [ ] **LESSON-5** — Możliwość powrotu do wcześniejszych lekcji. Błędy z poprzednich lekcji uwzględniane w następnej.
- [x] **LESSON-6** — Poprawiono matching: strip punctuation + prefix match (4 chars) + include match — łapie odmienione formy. ✅ (2026-03-26)
- [x] **LESSON-7** — Zweryfikowano: TranslationReveal już istnieje i jest używany w OutputForcingCard. ✅ (2026-03-26)
- [ ] **LESSON-8** — W pobranych plikach: zawartość Gramatyka + Słownictwo + Dialog (bez reszty). Nazewnictwo folderu np. `Hiszpański_A1`. Integracja z Google Drive / Obsidian.
- [ ] **LESSON-9** — Pobrana lekcja: 3 pliki audio (Gramatyka, Słownictwo, Dialog) + film dopasowany do poziomu i tematu.
- [ ] **TEST-4** — Test: znacznie trudniejszy, powiązany z bieżącą lekcją.
- [ ] **TEST-5** — Po zakończeniu testu: opcja regeneracji uwzględniająca błędy z podsumowania.
- [ ] **ERRORS-2** — Zakładka Błędy: przyciski "Generuj fiszki z błędów" i "Generuj test z błędów".
- [ ] **ERRORS-3** — Analiza błędów w Statystykach: więcej rubryk (Gramatyka, Rozumienie, Wymowa, Rozmowa), każda rozwijalna z opisem co poprawić.
- [x] **SPECIAL-CHARS** — SpecialCharHelper dodany do: textarea zadania produkcyjnego + textarea recall w OutputForcingCard. ✅ (2026-03-26)
- [x] **TRANSLATE-1** — Tłumacz: autodetect języka (cyrylica/inne → target→PL, reszta → PL→target), przycisk "Wytłumacz", "Dodaj do fiszek" po tłumaczeniu, zamknięcie przez klik poza. ✅ (2026-03-26)
- [x] **PRONUNCIATION-1** — Zakładka Wymowa: przycisk dodania zdania do fiszek. ✅ (2026-03-26)
- [x] **PRONUNCIATION-2** — Zakładka Wymowa: przycisk generowania nowych zdań do ćwiczenia. ✅ (2026-03-26)
- [ ] **VIDEOS-1** — Zakładka Filmy: dodawanie ulubionych twórców (przycisk lub wpisanie nazwy).
- [x] **GROK-1** — Zweryfikowano: prompt po polsku (conversation.py), edytowalny textarea + przycisk kopiowania w Conversation.jsx. ✅ (2026-03-26)
- [x] **STATS-2** — Zweryfikowano: `flashcards` jest destrukturyzowane ale nie renderowane w Stats.jsx. ✅ (2026-03-26)
- [x] **STATS-3** — Usunięto przycisk CSV. Historia lekcji: wszystkie lekcje z backendu, domyślnie 7 ostatnich, "Pokaż wszystkie" toggle. ✅ (2026-03-26)

---

## P3 — Niskie (UI/UX dopracowanie)

- [ ] **NAV-1** — Kolejność zakładek: Główna → Lekcja → Wymowa → Mów → Fiszki → Test → Newsy → Filmy → Timer → Statystyki → [tabela fiszek po prawej].
- [ ] **TIMER-2** — Timer: opcja własnego czasu (np. 30 min, nie tylko 15 min).
- [ ] **TIMER-3** — Ostatnie 5 sekund: licznik się powiększa i miga na czerwono.
- [ ] **TIMER-4** — Licznik czasu: 3x większy, po prawej na dole ekranu.
- [ ] **TIMER-5** — Usunąć "Flashcard Review" z trybu Timer (użytkownik korzysta z Anki).
- [ ] **HOME-1** — Zakładka Główna: usunąć "Fiszki do powtórki" z Aktywności.
- [ ] **HOME-2** — Sekcja Aktywności: zmienić nazwę z "Dzisiejsze Aktywności" na "Aktywności", zawierać wszystkie aktywności do nauki.
- [ ] **SETTINGS-1** — Ustawienia: w liście języków nauki pokazywać aktualnie uczony język dla łatwego dostępu.
- [ ] **HARDCORE** — Tryb Hardcore: zmienia język tylko częściowo — naprawić pełną zmianę na język uczony.
- [x] **ACHIEVEMENTS** — Wszystkie tytuły i opisy osiągnięć przetłumaczone na polski. ✅ (2026-03-26)
- [ ] **FLASHCARD-TABLE** — Tabela szybkiego dodawania fiszek: widoczna na każdej zakładce (stały element layoutu), od razu pokazuje pole do wpisania po kliknięciu.
- [ ] **READING-COPY** — Zakładka Czytanie: opcja kopiowania słowa/zdania do tabeli → AI tworzy fiszkę automatycznie.
- [ ] **MOW-ANALYSIS** — Analiza z zakładki Mów uwzględniana w systemie nauki i w Analizie błędów.
- [ ] **ERRORS-4** — Zakładka Błędy: wklejenie podsumowania rozmowy z Grok → analiza i ocena wymowy/rozmowy.
- [ ] **CONCEPTS** — Koncepcje gramatyczne: generowane do fiszek lub jako rozwijalna tabela w Statystykach.
- [ ] **AI-MODEL** — Zweryfikować czy Gemini to najlepszy darmowy wybór (do decyzji).

---

## Licznik

| Priorytet | Liczba zadań |
|---|---|
| P0 Krytyczne | 5 |
| P1 Wysokie | 8 |
| P2 Średnie | 28 |
| P3 Niskie | 17 |
| **RAZEM** | **58** |
