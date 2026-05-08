# Przewodnik Użytkownika LinguaAI

## Wstęp

LinguaAI to nowoczesna platforma do nauki języków obcych wspomagana przez sztuczną inteligencję. Dzięki zaawansowanym algorytmom AI, metodzie spaced repetition oraz personalizowanym lekcjom, nauka staje się skuteczniejsza i bardziej angażująca.

## Pierwsze Kroki

### 1. Rejestracja i Test Poziomujący

Po uruchomieniu aplikacji pierwszym krokiem jest **Test Poziomujący CEFR**, który składa się z 20 pytań. Test ocenia Twój poziom znajomości języka w skali CEFR (A1-C2).

```
Krok 1: Wejdź na stronę główną
Krok 2: Kliknij "Rozpocznij Test"
Krok 3: Odpowiedz na 20 pytań wielokrotnego wyboru
Krok 4: Otrzymaj wynik i przypisany poziom (A1, A2, B1, B2, C1, C2)
Krok 5: System wygeneruje Twój osobisty plan nauki
```

**Wskazówka**: Nie stresuj się testem. Jeśli wynik nie odpowiada Twoim oczekiwaniom, możesz go powtórzyć lub ręcznie zmienić poziom w ustawieniach.

### 2. Interfejs Aplikacji

Główny interfejs składa się z:
- **Paska nawigacyjnego** (NavBar) - dostęp do wszystkich sekcji
- **Strony głównej** - podsumowanie dzisiejszych zadań i postępów
- **Layoutu** - wyświetla powiadomienia o nowych osiągnięciach (toasty)

---

## Codzienna Nauka

### Lekcje Dzienne

Każdego dnia otrzymujesz nową lekcję dopasowaną do Twojego poziomu i zainteresowań.

**Struktura lekcji:**
1. **Słownictwo** - nowe słówka z tłumaczeniami i przykładami
2. **Gramatyka** - wyjaśnienie zasad z przykładami
3. **Comprehensible Input (i+1)** - tekst na poziomie nieco wyższym niż Twój obecny, ze wyróżnionymi nowymi słowami
4. **Interleaved Review** - powtórka materiału z ostatnich 7 dni
5. **Output Forcing** - ćwiczenie wypowiedzi (ukrycie tekstu i próba przypomnienia)

**Punktacja**: +25 XP za każdą ukończoną lekcję

### Odsłuchiwanie Audio

Każdy fragment lekcji może być odsłuchany:
- Kliknij przycisk **Play** obok tekstu
- Wybierz głos (domyślnie: en-US-JennyNeural)
- Audio jest generowane w czasie rzeczywistym przez edge-tts

### Eksport do PDF

Możesz pobrać lekcję jako plik PDF:
1. Otwórz ukończoną lekcję
2. Kliknij przycisk "Eksportuj PDF"
3. Plik zostanie wygenerowany z tabelą słówek i treścią lekcji

---

## Fiszki (Spaced Repetition)

System powtórek oparty na metodzie **Spaced Repetition** (powtórki w odstępach czasu).

### Jak to działa?
- Algorytm ocenia, kiedy powinieneś powtórzyć daną fiszkę
- Im lepiej znasz słówko, tym rzadziej będzie się ono pojawiać
- Im więcej błędów, tym częściej fiszka wraca do powtórki

### Korzystanie z fiszek:
1. Wejdź w zakładkę **Fiszki**
2. System pokaże fiszki gotowe do powtórki na dzisiaj
3. Kliknij na fiszkę, aby zobaczyć przód (słowo)
4. Spróbuj przypomnieć sobie tłumaczenie
5. Kliknij, aby odkryć tył (tłumaczenie)
6. Oceń jakość zapamiętania (0-5):
   - **0-2**: Słabo, fiszka wróci szybko
   - **3-4**: Dobrze, standardowy interwał
   - **5**: Idealnie, dłuższy interwał

**Punktacja**: +2 XP za każdą powtórkę

### Eksport do Anki

Możesz wyeksportować swoje fiszki do formatu Anki (.apkg):
1. Wejdź w zakładkę Fiszki
2. Kliknij "Eksportuj do Anki"
3. Plik zostanie pobrany i można go zaimportować w aplikacji Anki

---

## Rozmowy z AI

Ćwicz konwersację z wirtualnym partnerem opartym na Google Gemini 2.0 Flash.

### Rozpoczęcie rozmowy:
1. Wejdź w zakładkę **Rozmowa**
2. Wybierz temat (Podróże, Biznes, Codzienne życie, itp.)
3. Kliknij "Rozpocznij"
4. AI przywita Cię i zada pierwsze pytanie

### Funkcje podczas rozmowy:
- **Korekty gramatyczne** - AI wskazuje błędy i podaje poprawne formy
- **Sugestie słownictwa** - propozycje lepszych słów
- **Analiza wypowiedzi** - ocena po rozmowie (gramatyka, słownictwo, płynność)

### Tłumacz i Analiza Tekstu
- **Tłumacz**: Wpisz tekst, otrzymaj tłumaczenie w czasie rzeczywistym
- **Analiza tekstu**: Wklej swoją wypowiedź, otrzymaj listę błędów i wyjaśnienia

---

## Testy

### Test Dzienny
- 10 pytań opartych na dzisiejszej lekcji
- Punktacja: `wynik × 0.5` XP (maksymalnie 50 XP)
- Dostępny po ukończeniu lekcji

### Test Tygodniowy
- 20-30 pytań z materiału z całego tygodnia
- Więcej XP do zdobycia
- Dostępny w każdą niedzielę

**Wskazówka**: Nie spiesz się podczas testów. Czas jest mierzony, ale dokładność jest ważniejsza!

---

## System XP i Poziomy

### Poziomy (1-50)

System poziomów oparty na krzywej kwadratowej:
```
Poziom n wymaga: (n-1)² × 20 XP całkowitej ilości XP
```

| Poziom | Wymagane XP | | Poziom | Wymagane XP |
|--------|-------------|-|--------|-------------|
| 1      | 0           | | 10     | 1620        |
| 2      | 20          | | 20     | 7220        |
| 5      | 320         | | 30     | 16820       |
| 10     | 1620        | | 50     | 48020       |

### Zdobywanie XP

| Akcja | XP | |
|--------|----|-|
| Ukończenie lekcji | +25 | |
| Test dzienny (maks.) | +50 | |
| Test tygodniowy | do +100 | |
| Powtórka fiszki | +2 | |
| Rozmowa z AI (10 wiadomości) | +15 | |

### Osiągnięcia (Achievements)

System osiągnięć motywuje do regularnej nauki:
- **Fast Learner** - Ukończ 10 lekcji
- **Test Master** - Zdobądź 90%+ w 5 testach
- **Streak Champion** - Ucz się przez 7 dni z rzędu
- **Level Up!** - Osiągnij kolejny poziom

Powiadomienia o nowych osiągnięciach pojawiają się automatycznie jako toasty (znikają po 4 sekundach).

---

## Quick Mode (Szybki Tryb)

Nie masz dużo czasu? Użyj **Quick Mode**!

### Jak to działa?
1. Wejdź w zakładkę **Quick Mode**
2. System wygeneruje 15-minutowy plan aktywności:
   - 5 min: Szybka powtórka fiszek
   - 7 min: Krótka lekcja (i+1 text)
   - 3 min: Szybki test (5 pytań)

Idealne dla zabieganych osób, które chcą utrzymać ciągłość nauki.

---

## Czytanie Wiadomości (i+1)

Sekcja **News** dostarcza aktualnych wiadomości uproszczonych pod Twój poziom CEFR.

### Funkcje:
- Pobieranie z RSS (BBC, CNN, itp.)
- Uproszczenie tekstu przez AI (metoda i+1)
- Wyróżnienie nowych słówek
- Możliwość odsłuchania całego artykułu

---

## Trener Wymowy

Ulepsz swoją wymowę dzięki **faster-whisper** (Speech-to-Text).

### Jak to działa?
1. Wejdź w zakładkę **Wymowa**
2. Wybierz tekst referencyjny lub wpisz własny
3. Nagraj swoją wypowiedź (użyj mikrofonu)
4. Otrzymaj transkrypcję i ocenę:
   - **Ocena słowa po słowie** (0-100%)
   - **Wyróżnienie fonemów**
   - **Ogólny feedback** i wskazówki

**Wskazówka**: Nagrywaj w cichym otoczeniu dla lepszej jakości transkrypcji.

---

## YouTube Learning

Ucz się angielskiego poprzez filmy na YouTube.

### Funkcje:
- Wyszukiwanie filmów edukacyjnych
- Filtrowanie po poziomie CEFR
- Dostęp do transkrypcji
- Odsłuchiwanie wybranych fragmentów

---

## Google Drive Backup

Zabezpiecz swoje postępy poprzez kopię zapasową na Google Drive.

### Konfiguracja:
1. Wejdź w **Ustawienia**
2. Kliknij "Połącz z Google Drive"
3. Autoryzuj aplikację
4. Wybierz automatyczny backup (codziennie/co tydzień)

---

## Wskazówki i Najlepsze Praktyki

### Regularność
- Ucz się codziennie, nawet przez 15 minut (Quick Mode)
- Utrzymuj serię dni (streak) dla bonusowych XP

### Techniki Nauki
- **Output Forcing**: Zawsze próbuj samodzielnie ułożyć zdanie przed sprawdzeniem
- **Comprehensible Input**: Czytaj teksty i+1 - nie za łatwe, nie za trudne
- **Spaced Repetition**: Nie ignoruj powtórek fiszek - to klucz do długotrwałego zapamiętywania

### Wykorzystanie AI
- Rozmawiaj z AI jak z prawdziwym partnerem - nie bój się popełniać błędów
- Analizuj korekty gramatyczne - ucz się na błędach
- Używaj funkcji tłumacza z umiarem - najpierw spróbuj domyśleć się znaczenia

### Google Drive Backup
- Okresowo wykonuj kopię zapasową
- Sprawdzaj, czy synchronizacja działa poprawnie

---

## Rozwiązywanie Problemów

| Problem | Rozwiązanie |
|---------|--------------|
| Nie mogę odtworzyć audio | Sprawdź, czy przeglądarka wspiera Web Audio API |
| Transkrypcja wymowy nie działa | Sprawdź dostęp do mikrofonu w przeglądarce |
| Test nie chce się wysłać | Odśwież stronę, sprawdź połączenie z internetem |
| Brak nowych osiągnięć | Sprawdź w zakładce Statystyki / Osiągnięcia |

W razie problemów skontaktuj się z supportem lub sprawdź sekcję FAQ na stronie projektu.
