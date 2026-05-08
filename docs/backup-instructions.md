# Instrukcje Backupu LinguaAI

Kompletny przewodnik tworzenia kopii zapasowych bazy danych i plików projektu.

## Spis treści

- [Przegląd](#przegląd)
- [Automatyczny backup do Google Drive](#automatyczny-backup-do-google-drive)
- [Manualny backup bazy danych](#manualny-backup-bazy-danych)
- [Przywracanie bazy danych](#przywracanie-bazy-danych)
- [Backup plików audio i eksportów](#backup-plików-audio-i-eksportów)

---

## Przegląd

LinguaAI przechowuje dane w bazie SQLite (`lingua_ai.db`). Dodatkowo generowane są pliki audio w `backend/audio/` i eksporty w `backend/exports/`.

| Co backupować | Lokalizacja | Częstotliwość |
|--------------|--------------|---------------|
| Baza danych | `backend/lingua_ai.db` | Codziennie |
| Pliki audio | `backend/audio/` | Opcjonalnie |
| Eksporty PDF/Anki | `backend/exports/` | Opcjonalnie |
| Plik .env | `backend/.env` | Po zmianie |

---

## Automatyczny backup do Google Drive

### Konfiguracja

1. Włącz Google Drive Backup w ustawieniach użytkownika (endpoint w przygotowaniu)
2. Autoryzacja OAuth2 przez `GET /api/settings/gdrive/auth`
3. Codzienny backup o 2:00 w nocy (automatyczny zapis bazy do Google Drive)

### Endpointy Google Drive

| Metoda | Endpoint | Opis |
|--------|----------|-------|
| GET | `/api/settings/gdrive/status` | Status autoryzacji Google Drive |
| GET | `/api/settings/gdrive/auth` | URL do autoryzacji OAuth2 |
| GET | `/api/settings/gdrive/callback` | Callback po autoryzacji |

### Jak to działa

1. Baza SQLite jest kopiowana do pliku tymczasowego
2. Plik jest wysyłany do folderu `LinguaAI_Backups` na Google Drive
3. Nazwa pliku: `lingua_ai_backup_YYYY-MM-DD.db`
4. Stare backupy (starsze niż 30 dni) są automatycznie usuwane

---

## Manualny backup bazy danych

### Metoda 1: Kopia pliku SQLite

```bash
# Windows CMD
copy backend\lingua_ai.db backups\lingua_ai_backup_%date:~6,4%_%date:~3,2%_%date:~0,2%.db

# Linux/Mac
cp backend/lingua_ai.db backups/lingua_ai_backup_$(date +%Y-%m-%d).db
```

### Metoda 2: Eksport do SQL dump

```bash
# Eksport struktury i danych
sqlite3 backend/lingua_ai.db .dump > backups/lingua_ai_$(date +%Y%m%d).sql
```

### Metoda 3: Python script

```python
import shutil
from datetime import datetime

src = "backend/lingua_ai.db"
dst = f"backups/lingua_ai_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
shutil.copy2(src, dst)
print(f"Backup created: {dst}")
```

---

## Przywracanie bazy danych

### Z pliku .db

```bash
# Zatrzymaj backend
# Windows
copy backups\lingua_ai_backup_2026-05-08.db backend\lingua_ai.db

# Linux/Mac
cp backups/lingua_ai_backup_2026-05-08.db backend/lingua_ai.db
```

### Z pliku .sql

```bash
# Ostrzeżenie: to nadpisze istniejącą bazę!
sqlite3 backend/lingua_ai.db < backups/lingua_ai_20260508.sql
```

### Weryfikacja po przywróceniu

```bash
# Sprawdź czy baza działa
python -c "from backend.database import engine; from sqlalchemy import text; print(engine.connect().execute(text('SELECT 1')).scalar())"
```

---

## Backup plików audio i eksportów

### Archiwizacja plików audio

```bash
# Spakuj pliki audio
# Windows
tar -czf backups/audio_archive_$(date +%Y%m%d).tar.gz backend/audio/

# Linux/Mac
tar -czf backups/audio_archive_$(date +%Y%m%d).tar.gz backend/audio/
```

### Archiwizacja eksportów

```bash
# Skopiuj wygenerowane PDF-y i pliki Anki
tar -czf backups/exports_$(date +%Y%m%d).tar.gz backend/exports/
```

---

## Harmonogram backupów

| Typ backupu | Częstotliwość | Metoda |
|-------------|---------------|--------|
| Baza danych (SQLite) | Codziennie o 2:00 | Automatyczny (Google Drive) lub manualny |
| Pliki audio | Raz w tygodniu | Manualny (tar.gz) |
| Eksporty | Raz w miesiącu | Manualny |
| Plik .env | Po każdej zmianie | Manualny (kopia) |

---

## Rozwiązywanie problemów

### Błąd: "Database is locked"

Baza SQLite może być zablokowana przez działający backend. Rozwiązanie:

```bash
# Zatrzymaj backend przed backupem
# Wykonaj kopię
# Uruchom backend
```

### Błąd: Google Drive auth failed

1. Sprawdź czy `GOOGLE_CLIENT_ID` i `GOOGLE_CLIENT_SECRET` są ustawione w `.env`
2. Wyczyść cookies i spróbuj autoryzacji ponownie
3. Sprawdź logi backendu: `tail -f logs/lingua-ai.log`

### Błąd: Backup file corrupted

1. Zweryfikuj integralność: `sqlite3 backup.db "PRAGMA integrity_check;"`
2. Jeśli uszkodzona — przywróć starszy backup
3. Sprawdź dysk pod kątem błędów

---

## Bezpieczeństwo

- Plik `.env` zawiera wrażliwe klucze API — **nigdy nie wrzucaj go do repo Git**
- Backupy na Google Drive są prywatne (folder użytkownika)
- Rozważ szyfrowanie backupów dla dodatkowej ochrony:
  ```bash
  gpg -c backups/lingua_ai_backup_2026-05-08.db  # Szyfrowanie
  gpg backups/lingua_ai_backup_2026-05-08.db.gpg      # Deszyfrowanie
  ```

---

## Checklista przed wdrożeniem

- [ ] Skonfiguruj Google Drive OAuth2 (client ID, client secret)
- [ ] Przetestuj backup manualny
- [ ] Przetestuj przywracanie z backupu
- [ ] Ustaw cron/automatyczny backup
- [ ] Zweryfikuj uprawnienia do zapisu w katalogu `backups/`
- [ ] Sprawdź czy backup nie zawiera wrażliwych danych (klucze API)
