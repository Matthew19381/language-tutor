# ADR-003: Ochrona konta — Alpha Decay i Circuit Breaker

**Data:** 2026-03-24
**Status:** Zaakceptowane (do implementacji)
**Projekt:** AutoLogic / analytics/risk_engine.py

---

## Kontekst

Strategia po czasie może przestać działać (alpha decay) z powodu:
1. Crowding — zbyt wiele algorytmów handluje tym samym sygnałem
2. Regime change — zmiana charakteru rynku
3. Structural change — zmiana regulacji, płynności, spreadu
4. Overfitting unmasked — strategia nigdy nie miała edge

## Decyzja

Implementacja 4-poziomowego circuit breakera + AlphaDecayMonitor.

### Circuit Breaker (4 poziomy)
| Poziom | Warunek | Akcja |
|--------|---------|-------|
| 1 | SL per trade (1–2% konta) | Automatyczny SL w MT5 |
| 2 | Dzienna strata ≥ 3–5% | Stop trading do następnego dnia |
| 3 | Tygodniowa strata ≥ 6–8% | Stop + ręczny review |
| 4 | DD od peak ≥ 15–20% | Pełne wyłączenie + re-walidacja |

### AlphaDecayMonitor (sygnały ostrzegawcze)
- Rolling win rate (20 transakcji) spada > 20% od historycznego → alarm
- Rolling avg R spada poniżej 0 przez 30 dni → pause
- Equity spada poniżej MA(20) własnej krzywej → stop
- Profit Factor przez 30 dni < 1.0 → re-walidacja

### Equity Curve Kill Switch
- Handluj tylko gdy equity > MA(20) własnej krzywej kapitału
- Gdy equity spada poniżej MA(20) → wyłącz handel, czekaj na powrót

### Procedura po uruchomieniu circuit breakera
1. Zamknij wszystkie pozycje natychmiast
2. Zapisz raport: czas, powód, equity, ostatnie N transakcji
3. Przepuść ostatnie 3M danych live przez validate_ga.py
4. Ręczna decyzja: kontynuuj / restart GA / zmień strategię
5. Manual reset wymagany (nie automatyczny)

## Rekomendowane parametry startowe (konserwatywne)
- Risk per trade: 1% konta
- Daily loss limit: 3%
- Weekly loss limit: 6%
- Monthly loss limit: 10%
- Peak-to-trough DD: 15%
- Consecutive losses: 5 z rzędu → redukcja size o 50%
