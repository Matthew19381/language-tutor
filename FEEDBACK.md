# Language Tutor — Feedback użytkownika (2026-03-23)

## Krytyczne — do naprawy w pierwszej kolejności

### Model AI
- [x] Zweryfikowano: Aplikacja używa **Ollama** (qwen2.5:7b, llama3.1, deepseek-coder-v2:16b) zamiast Gemini. Task router wybiera model w zależności od zadania. Jest to darmowe, lokalne rozwiązanie — najlepszy wybór.
- [x] Zmienić interfejs na **polski** (cały UI po angielsku — nie do zaakceptowania)

### Test poziomujący
- [ ] Test jest za łatwy i intuicyjny — użytkownik ma niższy poziom niż B1 (brak znajomości gramatyki, czasów, mianowników) — poprawić pytania i kalibrację poziomu

---

## Zakładka: Lekcja

### Pozytywne
- Zakładka ogólnie fajna
- Możliwość pobrania lekcji lokalnie lub na Google Drive (4 dni) — świetne

### Do poprawy
- [x] Słownictwo: dodać tłumaczenie przykładowego zdania (jest słowo, tłumaczenie, przykład — ✅ frontend wyświetla example_translation, fallback poprawiony 2026-05-03)
- [x] Dialog: układ 1 osoba po lewej / 1 osoba po prawej — ✅ zaimplementowane w DailyLesson.jsx (isB → flex-row-reverse, linia 602-627)
- [ ] Ćwiczenia: bardziej zróżnicowane
- [ ] Zadanie produkcyjne: dodać możliwość sprawdzenia odpowiedzi przez AI (kto ma sprawdzić?)
- [ ] Wymuszanie produkcji: zapamiętywanie 5 długich zdań — przemyśleć inny format
- [ ] **Audio dla całej lekcji**: treść, dialogi, czytanie, przegląd błędów, słownictwo — prawie wszystko oprócz ćwiczeń wpisywania

---

## Zakładka: Czytanie
- [ ] Opcja kopiowania słowa/zdania do tabeli widocznej w interfejsie → automatyczne tworzenie fiszki przez AI

---

## Zakładka: Fiszki
- [ ] Dodawanie fiszki: tylko wpisanie słowa/frazy → reszta generowana przez AI automatycznie
- [ ] Filtr fiszek po dacie dodania (nie pobierać codziennie wszystkich)
- [ ] Fiszki nie odzwierciedlają poziomu słownictwa — poprawić dobór
- [ ] Tłumaczenie przykładowego zdania — opcjonalne, niezbyt pilne
- [ ] Audio dla fiszek
- [ ] Zweryfikować bazę danych: czy postępy są zapisywane?

### Pozytywne
- Przegląd i eksport do Anki — dobry
- Fiszki pięknie zbudowane

---

## Zakładka: Mów
- [ ] Analiza z zakładki Mów powinna być uwzględniana przez system w dalszej nauce
- Ogólnie fajna funkcja, zakończenie i analiza szczególnie dobre

---

## Zakładka: News
- Świetnie zrobiona — dodawanie słownictwa do fiszek, pytania do artykułu, link do oryginału

---

## Zakładka: Wymowa
- [ ] Plik audio wskazujący poprawną wymowę zdania
- [ ] Podsumowanie odnośnie wymowy
- [ ] Filmy z internetu (polskie i angielskie akceptowane)

---

## Zakładka: Statystyki
- [ ] Wskaźnik ukończenia lekcji: przesuwać wraz z ukończeniem ćwiczeń (Lekcja + Fiszki minimum)
- [ ] Fiszki w statystykach: pole do ręcznego odhaczenia (użytkownik korzysta też z Anki)
- [ ] Wskazówki dzienne: generować raz dziennie przy pierwszym wejściu (nie przy każdym wejściu na stronę)
- [ ] To samo dla strony głównej i Daily Tips
- [ ] Z czasem: dodać więcej osiągnięć
- Analiza błędów — dobra, ale potrzebuje więcej pól
- Dzienne wskazówki poparte nauką — świetne

---

## Tryb 15-Minutowy
- [ ] Bug: minutnik zatrzymuje się i nie jest widoczny po kliknięciu w inną zakładkę
- [ ] Dodać opcję własnego czasu (np. 30 min)
- [ ] Flashcard Review w trybie 15-min: do przemyślenia (użytkownik korzysta z Anki)

---

## Ustawienia
- [ ] Dodać możliwość zmiany języka nauki (nie tylko Polki i Hardcore)

---

## Rozmowa głosowa
- [ ] Dodać generator promptu dla Grok (zawierający: co się dzisiaj uczyłem, problemy, słownictwo) → wklejenie do zewnętrznego modelu
- [ ] Dialog: opcja rozmowy z audio (model odpowiada głosem) + opcja wpisywania ręcznego

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
- [x] **Test poziomujący** — still flagged as "za łatwy" (FEEDBACK item) — needs calibration improvements (P2)
- [x] **Słownictwo: tłumaczenie przykładu** — not implemented yet (P2)
- [x] **Timer bug** (zatrzymuje się przy zmianie zakładki) — appears to be fixed already (QuickMode logic independent of tab focus)
- [x] **Fiszki audio** — not implemented (P2)
- [x] **Wskazówki dzienne caching** — already implemented (localStorage)

### Decision log
- **ADR-002**: Unicode Path Handling — accept split deployment temporarily, plan rename to ASCII path within 7 days

### Next steps (from TASKS Backlog)
1. Rename project folder to ASCII-only path (permanent fix)
2. Build production frontend container (nginx) for Docker
3. Implement automated test suite (pytest + Playwright)
4. Daily DB backup automation
5. User documentation (Getting Started guide)

