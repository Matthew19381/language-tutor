# ADR-001: Utrzymanie edge-tts z retry zamiast zmiany providera

**Data:** 2026-03-26
**Status:** Zaakceptowane
**Projekt:** Language Tutor

---

## Kontekst

edge-tts zwracał sporadyczny błąd `403 Invalid response status` od serwera Bing Speech.
Wcześniej próbowano gtts (błąd: `No module named 'gtts'`). Błąd 403 jest nieregularny — w tej samej sesji jedna próba failuje, następna przechodzi z kodem 200.

## Decyzja

Pozostać przy edge-tts (v7.0.2) i dodać mechanizm retry (3 próby, backoff 0.5s/1s/2s).

### Szczegóły implementacji
- `backend/services/audio_service.py`: `generate_audio()` — pętla `for attempt in range(3)`
- Sleep: `asyncio.sleep(0.5 * (2 ** attempt))` między próbami
- Logowanie: WARNING na każdą nieudaną próbę, ERROR po 3 failach

## Rozważane alternatywy

| Opcja | Zalety | Wady |
|-------|--------|------|
| edge-tts + retry (wybrana) | Bez zależności, wysoka jakość głosu Neural | Zależność od serwisu Bing (może być blokowany) |
| gTTS (Google) | Stabilny, szeroka obsługa języków | Niższa jakość, wymaga osobnej instalacji |
| pyttsx3 | Offline, zero API calls | Niska jakość, wymaga głosów systemowych |

## Konsekwencje

### Pozytywne
- Brak nowych zależności
- Wysoka jakość głosów Neural (de-DE-KatjaNeural, es-ES-ElviraNeural itd.)
- Intermittent 403 rozwiązany przez retry

### Negatywne / Kompromisy
- Jeśli Bing zablokuje IP trwale — trzeba zmienić provider na gTTS
- Retry dodaje maks. 3.5s latencji przy ciągłych failach
