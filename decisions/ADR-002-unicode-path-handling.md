# ADR-002: Unicode Path Handling Strategy

**Data:** 2026-04-06  
**Status:** Zaakceptowane (tymczasowe, z planem revertu)  
**Projekt:** LinguaAI

---

## Kontekst

Aplikacja LinguaAI jest rozwijana na Windows z ścieżką projektu zawierającą polskie znaki:
```
G:\Mój dysk\NowaNadzieja\Praca\ClaudeCode\03_Projects\LinguaAI\
```

Podczas `npm install` w folderze `frontend` występuje błąd:
```
npm ERR! EPERM: operation not permitted, mkdir 'G:\Mój dysk\...\frontend\node_modules\eslint'
```

To znany limitation npm/Node.js na Windows — biblioteki C++ (node-gyp, graceful-fs) nie radzą sobie poprawnie z Unicode ścieżkami w operacjach na systemie plików.

## Decyzja

**Tymczasowe rozwiązanie**: Split deployment

- **Backend** (Python/FastAPI) uruchamiany z oryginalnej ścieżki `G:\...` — Python nie ma problemu z Unicode
- **Frontend** (React/Vite) uruchamiany z `C:\LinguaAI\frontend` (ścieżka ASCII) — tam `npm install` i `npm run dev` działają
- `node_modules` istnieje tylko w `C:\LinguaAI\frontend\node_modules`
- Kod źródłowy frontendu (src, public, index.html) pozostaje na G:\ (kopia na C:\ dla dev)

### Port allocation

- LinguaAI Backend: `8001` (bo `8000` zajęte przez ForgeBody)
- LinguaAI Frontend: `5173` (domyślnie Vite)
- LinguaAI Ollama: `11436` (bo `11435` zajęte przez ForgeBody)
- Backend API URL w frontendzie: `VITE_API_URL=http://localhost:8001`

## Alternatywy rozważone

| Opcja | Zalety | Wady | Powód odrzucenia |
|-------|--------|------|------------------|
| **Rename folder na ASCII** | Jeden source of truth, wszystko na G:\ | Wymaga zmiany ścieżek w dokumentacji, skryptach, możliwy break w istniejących linkach | **NIE ODRZUCONA — to permanent fix** |
| **WSL2** | Linux env, npm działa z UTF-8 | Wymaga migracji do Linux, dodatkowa warstwa, learning curve | Zbyt ciężki dla tymczasowego fixa |
| **Docker + volumes** | Izolacja, przenośność | Docker Desktop na Windows też ma problemy z Unicode mount | Nie działa (testowane) |
| **Split (wybrana)** | Minimalne zmiany, działa od razu | Dwa miejsca (G:\ i C:\) — source of truth jest rozdzielony | Tylko tymczasowo, pending rename |

## Konsekwencje

### Pozytywne
- Aplikacja działa natychmiast bez zmiany istniejących plików źródłowych na G:\
- Backend (Python) nie wymaga przenoszenia (bardzo duże pliki, DB, audio exports)
- Frontend developer experience: `npm run dev` działa (z C:\)

### Negatywne / Kompromisy
- **Source of truth rozdzielony**:
  - Backend + DB + frontend `src/` = G:\
  - Frontend `node_modules` + cache = C:\
- Ryzyko desynchronizacji (zmiany w G:\ src bez aktualizacji C:\? — current setup: C:\ ma pełną kopię `src/`)
- Docker production build niedostępne (frontend build wymaga `node_modules` na tej samej ścieżce co `src`)
- Zespołowym developerom trzeba instrukcji: " Edytuj src na G:\, ale uruchamiaj z C:\"

## Permanent fix plan

1. Wybierz nową ścieżkę ASCII na G:\ (np. `G:\Projects\LinguaAI` lub `G:\LinguaAI`)
2. Przenieś cały folder `03_Projects\LinguaAI` do nowej lokalizacji
3. Zaktualizuj:
   - `start.bat`, `start.ps1`
   - `docker-compose.yml` (volumes, ports)
   - `vite.config.js` (proxy target jeśli hardcoded)
   - Backend config (jeśli ma relative paths — ale używa `./` więc应该 OK)
4. Usuń stary folder (lub zostaw jako backup)
5. Przetestuj: `npm install` w nowym `frontend/` powinno działać bez EPERM

## Evidence

```bash
# Próba npm install na G:\ (polskie znaki) — FAIL
cd "G:\Mój dysk\...\LinguaAI\frontend"
npm install
# → EPERM: mkdir ...\node_modules\eslint

# Sukces po przeniesieniu do C:\
cd "C:\LinguaAI\frontend"  # (skopiowane)
npm install
# → added 355 packages in 45s

# Backend działa z G:\ (Python Unicode OK)
cd "G:\Mój dysk\...\LinguaAI\backend"
OLLAMA_BASE_URL=http://localhost:11434/v1 python -m uvicorn main:app --port 8001
# → Uvicorn running on http://0.0.0.0:8001
```

## Related

- **npm issue #6686** (Windows Unicode paths): https://github.com/npm/cli/issues/6686
- **Node.js Unicode on Windows**: Node uses UTF-8 internally but many native modules still use ANSI APIs
- Docker Desktop Windows: WSL2 backend doesn't support mounting Windows paths with non-ASCII characters reliably

---

**Next:** Execute permanent rename within 7 days to eliminate split deployment.

[result-id: adr-002]
