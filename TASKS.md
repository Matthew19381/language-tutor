# TASKS — Language Tutor

_Ostatnia aktualizacja: 2026-03-26_
_Źródła: FEEDBACK.md + ZmianyTutor.txt (2026-03-18 → 2026-03-26)_

---

## P0 — Krytyczne (blokują użycie aplikacji)

- [x] **AUDIO-1** — Audio nie działa: edge-tts zwraca 403. Dodano retry 3x z exponential backoff (0.5s/1s/2s). ✅ (2026-03-26)
- [ ] **AUDIO-2** — Dodać audio do: lekcja (treść, dialog, słownictwo), fiszki, przegląd błędów, wymowa (wzorcowe zdanie), newsy. Audio generowane raz przy tworzeniu lekcji.
- [ ] **UI-1** — Cały interfejs zmienić na **polski** (zakładki, przyciski, etykiety, komunikaty, poziomy: Beginner → Początkujący).
- [ ] **LESSON-1** — Lekcja regeneruje się przy każdej zmianie zakładki lub odświeżeniu — naprawić.
- [ ] **LESSON-2** — Lekcja nie powinna zaczynać od Dnia 2 jeśli użytkownik nie ukończył Dnia 1.

---

## P1 — Wysokie (funkcje zepsute)

- [x] **TEST-1** — Cache pytań testu w localStorage per dzień/język. ✅ (2026-03-26)
- [ ] **TEST-2** — Test plasujący: pytania za łatwe, z przetłumaczonym tekstem (odpowiedź oczywista). Przebudować kalibrację.
- [ ] **TEST-3** — Test plasujący: pytanie z 2 lukami i 3 słowami w odpowiedzi — logicznie błędne. Naprawić generator pytań.
- [ ] **TIMER-1** — Minutnik zatrzymuje się i znika po kliknięciu w inną zakładkę. Minutnik ma być widoczny globalnie (layout), nie zatrzymywać się.
- [x] **STATS-1** — TodayCompletion: reaktywny useState + odświeżanie na focus okna. 4 aktywności: Lekcja, Test, Rozmowa, Newsy/Wymowa. ✅ (2026-03-26)
- [ ] **ERRORS-1** — Zakładka Błędy: nie pokazuje odpowiedzi użytkownika ani poprawnej — tylko wyjaśnienie. Dodać: moja odpowiedź / poprawna odpowiedź / wyjaśnienie.
- [x] **GRAMMAR-1** — Wyjaśnienie gramatyki: dodano `renderMarkdown()` obsługujący `#/##/###`, `**bold**`, listy. ✅ (2026-03-26)
- [x] **FLASHCARD-BTN** — Backend zwraca teraz czytelny komunikat gdy AI nie generuje koncepcji. ✅ (2026-03-26)

---

## P2 — Średnie (funkcje niekompletne)

- [x] **LANG-1** — Usunięto 1.5s setTimeout — zmiana języka przeładowuje stronę natychmiast. ✅ (2026-03-26)
- [x] **LANG-2** — Naprawiono needs_placement: was_new rejestrowane PRZED zapisem profilu. ✅ (2026-03-26)
- [ ] **LANG-3** — Zmiana języka nie resetuje poziomu (do weryfikacji po LANG-2).
- [ ] **LANG-4** — Wszystkie treści (Lekcja, Główna, Tips, Newsy itd.) osobne dla każdego uczonego języka.
- [ ] **TIPS-1** — Dzienne wskazówki generowane przy każdym wejściu na stronę. Ma być raz dziennie przy pierwszym wejściu.
- [x] **TIPS-2** — Prompt wzmocniony: CRITICAL - pisz w {native_language}. ✅ (2026-03-26)
- [x] **DIALOG-1** — Układ dialogu: naprawiono — teraz używa pola `speaker` zamiast alternującego indeksu. ✅ (2026-03-26)
- [ ] **FLASHCARD-1** — Fiszki: filtr po dacie/temacie dodania.
- [ ] **FLASHCARD-2** — Fiszki: AI sprawdza poprawność wpisanego słowa przed dodaniem do zbioru (żeby nie utrwalać błędów).
- [ ] **FLASHCARD-3** — Fiszki: opcja dodania polskiego słowa na przód / niemieckiego na tył (zamiast tylko niem→pol).
- [ ] **FLASHCARD-4** — Fiszki: nawigacja klawiaturą (Enter = odwróć, 1-4 = oceń i przejdź dalej). Przyciski oceny nie mają "latać" w górę/dół.
- [ ] **FLASHCARD-5** — Sprawdzanie duplikatów przy dodawaniu fiszki — komunikat jeśli już istnieje.
- [ ] **LESSON-3** — Historia lekcji: wskaźnik ukończenia per lekcja.
- [ ] **LESSON-4** — Generator przycisku "Następna lekcja" (nie "Wygeneruj nową — usuwa obecną").
- [ ] **LESSON-5** — Możliwość powrotu do wcześniejszych lekcji. Błędy z poprzednich lekcji uwzględniane w następnej.
- [ ] **LESSON-6** — Ćwiczenie czytania (i+1): w tekście zaznaczone tylko 2 z 6 nowych słów — naprawić.
- [ ] **LESSON-7** — Wymuszanie produkcji (Recall): dodać opcję ujawnienia tłumaczenia zdania.
- [ ] **LESSON-8** — W pobranych plikach: zawartość Gramatyka + Słownictwo + Dialog (bez reszty). Nazewnictwo folderu np. `Hiszpański_A1`. Integracja z Google Drive / Obsidian.
- [ ] **LESSON-9** — Pobrana lekcja: 3 pliki audio (Gramatyka, Słownictwo, Dialog) + film dopasowany do poziomu i tematu.
- [ ] **TEST-4** — Test: znacznie trudniejszy, powiązany z bieżącą lekcją.
- [ ] **TEST-5** — Po zakończeniu testu: opcja regeneracji uwzględniająca błędy z podsumowania.
- [ ] **ERRORS-2** — Zakładka Błędy: przyciski "Generuj fiszki z błędów" i "Generuj test z błędów".
- [ ] **ERRORS-3** — Analiza błędów w Statystykach: więcej rubryk (Gramatyka, Rozumienie, Wymowa, Rozmowa), każda rozwijalna z opisem co poprawić.
- [ ] **SPECIAL-CHARS** — Znaki specjalne (ä Ä ö Ö ü Ü ß): wyświetlać przy każdym polu tekstowym (nie tylko w ćwiczeniach).
- [ ] **TRANSLATE-1** — Panel tłumacza (górny lewy): autodetect języka (uczony ↔ polski), tylko tłumaczy słowo/zdanie, "Wytłumacz" jako opcja, po tłumaczeniu przycisk "Dodaj do fiszek", zamyka się po kliknięciu poza.
- [ ] **PRONUNCIATION-1** — Zakładka Wymowa: przycisk dodania zdania do fiszek.
- [ ] **PRONUNCIATION-2** — Zakładka Wymowa: przycisk generowania nowych zdań do ćwiczenia.
- [ ] **VIDEOS-1** — Zakładka Filmy: dodawanie ulubionych twórców (przycisk lub wpisanie nazwy).
- [ ] **GROK-1** — Generator promptu dla Grok: po polsku, widoczny i edytowalny przed skopiowaniem, zawiera temat dnia + błędy + słownictwo.
- [ ] **STATS-2** — Statystyki: usunąć pole Fiszki (użytkownik korzysta z Anki).
- [ ] **STATS-3** — Statystyki: zamiast eksportu CSV — rozwijana tabela historii lekcji (in-app).

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
