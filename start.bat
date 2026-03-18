@echo off
echo ============================================
echo   Language Tutor - AI-Powered Learning App
echo ============================================
echo.

REM Check if .env exists
if not exist "backend\.env" (
    echo [WARNING] backend\.env not found!
    echo Please create backend\.env from backend\.env.example
    echo and add your GEMINI_API_KEY before starting.
    echo.
    pause
)

echo Starting Language Tutor Backend...
start cmd /k "title LinguaAI - Backend && py -3.11 -m uvicorn backend.main:app --reload --port 8000"

cd frontend
echo Starting Language Tutor Frontend...
start cmd /k "title LinguaAI - Frontend && npm run dev"

echo.
echo ============================================
echo   Uruchamianie...
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo ============================================
echo.
echo Za chwile otworz przegladarke na http://localhost:5173
echo.
timeout /t 3 /nobreak >nul
start http://localhost:5173
exit
