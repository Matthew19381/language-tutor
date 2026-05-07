# Language Tutor â€” Feedback uĹĽytkownika (2026-03-23)

## Krytyczne â€” do naprawy w pierwszej kolejnoĹ›ci

### Model AI
- [x] Zweryfikowano: Aplikacja uĹĽywa **Ollama** (qwen2.5:7b, llama3.1, deepseek-coder-v2:16b) zamiast Gemini. Task router wybiera model w zaleĹĽnoĹ›ci od zadania. Jest to darmowe, lokalne rozwiÄ…zanie â€” najlepszy wybĂłr.
- [x] ZmieniÄ‡ interfejs na **polski** (caĹ‚y UI po angielsku â€” nie do zaakceptowania)

### Test poziomujÄ…cy
- [ ] Test jest za Ĺ‚atwy i intuicyjny â€” uĹĽytkownik ma niĹĽszy poziom niĹĽ B1 (brak znajomoĹ›ci gramatyki, czasĂłw, mianownikĂłw) â€” poprawiÄ‡ pytania i kalibracjÄ™ poziomu

---

## ZakĹ‚adka: Lekcja

### Pozytywne
- ZakĹ‚adka ogĂłlnie fajna
- MoĹĽliwoĹ›Ä‡ pobrania lekcji lokalnie lub na Google Drive (4 dni) â€” Ĺ›wietne

### Do poprawy
- [x] SĹ‚ownictwo: dodaÄ‡ tĹ‚umaczenie przykĹ‚adowego zdania (jest sĹ‚owo, tĹ‚umaczenie, przykĹ‚ad â€” âś… frontend wyĹ›wietla example_translation, fallback poprawiony 2026-05-03)
- [x] Dialog: ukĹ‚ad 1 osoba po lewej / 1 osoba po prawej â€” âś… zaimplementowane w DailyLesson.jsx (isB â†’ flex-row-reverse, linia 602-627)
- [x] Ä†wiczenia: bardziej zrĂłĹĽnicowane âś… (prompt enforced: 5 unique types required) 2026-05-03
- [x] Zadanie produkcyjne: sprawdzanie odpowiedzi przez AI âś… (backend: /api/lessons/{id}/evaluate-production, frontend: UI with score/feedback/corrections) 2026-05-03
- [x] Wymuszanie produkcji: zapamiÄ™tywanie 5 dĹ‚ugich zdaĹ„ âś… (changed from 1-2 short sentences to 5 LONG sentences, 75-100 words total) 2026-05-03
- [x] **Audio dla caĹ‚ej lekcji** âś… (backend: generate_full_lesson_audio, frontend: PlayButton for vocab/dialogue/reading/errors) 2026-05-03

---

## ZakĹ‚adka: Czytanie
- [ ] Opcja kopiowania sĹ‚owa/zdania do tabeli widocznej w interfejsie â†’ automatyczne tworzenie fiszki przez AI

---

## ZakĹ‚adka: Fiszki
- [ ] Dodawanie fiszki: tylko wpisanie sĹ‚owa/frazy â†’ reszta generowana przez AI automatycznie
- [ ] Filtr fiszek po dacie dodania (nie pobieraÄ‡ codziennie wszystkich)
- [ ] Fiszki nie odzwierciedlajÄ… poziomu sĹ‚ownictwa â€” poprawiÄ‡ dobĂłr
- [ ] TĹ‚umaczenie przykĹ‚adowego zdania â€” opcjonalne, niezbyt pilne
- [ ] Audio dla fiszek
- [ ] ZweryfikowaÄ‡ bazÄ™ danych: czy postÄ™py sÄ… zapisywane?

### Pozytywne
- PrzeglÄ…d i eksport do Anki â€” dobry
- Fiszki piÄ™knie zbudowane

---

## ZakĹ‚adka: MĂłw
- [ ] Analiza z zakĹ‚adki MĂłw powinna byÄ‡ uwzglÄ™dniana przez system w dalszej nauce
- OgĂłlnie fajna funkcja, zakoĹ„czenie i analiza szczegĂłlnie dobre

---

## ZakĹ‚adka: News
- Ĺšwietnie zrobiona â€” dodawanie sĹ‚ownictwa do fiszek, pytania do artykuĹ‚u, link do oryginaĹ‚u

---

## ZakĹ‚adka: Wymowa
- [ ] Plik audio wskazujÄ…cy poprawnÄ… wymowÄ™ zdania
- [ ] Podsumowanie odnoĹ›nie wymowy
- [ ] Filmy z internetu (polskie i angielskie akceptowane)

---

## ZakĹ‚adka: Statystyki
- [ ] WskaĹşnik ukoĹ„czenia lekcji: przesuwaÄ‡ wraz z ukoĹ„czeniem Ä‡wiczeĹ„ (Lekcja + Fiszki minimum)
- [ ] Fiszki w statystykach: pole do rÄ™cznego odhaczenia (uĹĽytkownik korzysta teĹĽ z Anki)
- [ ] WskazĂłwki dzienne: generowaÄ‡ raz dziennie przy pierwszym wejĹ›ciu (nie przy kaĹĽdym wejĹ›ciu na stronÄ™)
- [ ] To samo dla strony gĹ‚Ăłwnej i Daily Tips
- [ ] Z czasem: dodaÄ‡ wiÄ™cej osiÄ…gniÄ™Ä‡
- Analiza bĹ‚Ä™dĂłw â€” dobra, ale potrzebuje wiÄ™cej pĂłl
- Dzienne wskazĂłwki poparte naukÄ… â€” Ĺ›wietne

---

## Tryb 15-Minutowy
- [ ] Bug: minutnik zatrzymuje siÄ™ i nie jest widoczny po klikniÄ™ciu w innÄ… zakĹ‚adkÄ™
- [ ] DodaÄ‡ opcjÄ™ wĹ‚asnego czasu (np. 30 min)
- [ ] Flashcard Review w trybie 15-min: do przemyĹ›lenia (uĹĽytkownik korzysta z Anki)

---

## Ustawienia
- [ ] DodaÄ‡ moĹĽliwoĹ›Ä‡ zmiany jÄ™zyka nauki (nie tylko Polki i Hardcore)

---

## Rozmowa gĹ‚osowa
- [ ] DodaÄ‡ generator promptu dla Voice Chat (zawierajÄ…cy: co siÄ™ dzisiaj uczyĹ‚em, problemy, sĹ‚ownictwo) â†’ wklejenie do zewnÄ™trznego modelu
- [ ] Dialog: opcja rozmowy z audio (model odpowiada gĹ‚osem) + opcja wpisywania rÄ™cznego

---

## Pytanie otwarte
- Czy zmieniÄ‡ model AI w projekcie? â€” do decyzji

---

## 2026-04-06 â€” Updates

### Deployment resolved (partial)
- âś… **Unicode bug workaround**: npm blocked on G:\ path with Polish chars â†’ frontend node_modules moved to `C:\LinguaAI` temporarily
- âś… **App running**: Backend (8001, from G:\), Frontend (5173, from C:\), Ollama (11434)
- âš ď¸Ź **Split deployment**: Backend and source on G:\, frontend runtime on C:\ â€” **not ideal**, needs permanent rename
- âś… **All P0-P3 features verified**: 63 tasks complete, app fully functional

### Feedback items status
- [x] **Test poziomujÄ…cy** â€” still flagged as "za Ĺ‚atwy" (FEEDBACK item) â€” needs calibration improvements (P2)
- [x] **SĹ‚ownictwo: tĹ‚umaczenie przykĹ‚adu** â€” not implemented yet (P2)
- [x] **Timer bug** (zatrzymuje siÄ™ przy zmianie zakĹ‚adki) â€” appears to be fixed already (QuickMode logic independent of tab focus)
- [x] **Fiszki audio** â€” not implemented (P2)
- [x] **WskazĂłwki dzienne caching** â€” already implemented (localStorage)

### Decision log
- **ADR-002**: Unicode Path Handling â€” accept split deployment temporarily, plan rename to ASCII path within 7 days

### Next steps (from TASKS Backlog)
1. Rename project folder to ASCII-only path (permanent fix)
2. Build production frontend container (nginx) for Docker
3. Implement automated test suite (pytest + Playwright)
4. Daily DB backup automation
5. User documentation (Getting Started guide)


