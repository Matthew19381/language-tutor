@echo off
echo ============================================
echo   LinguaAI - AI-Powered Learning App
echo ============================================
echo.

REM Check if .env exists (root or backend/)
if exist ".env" (
    echo Found .env at project root.
) else if exist "backend\.env" (
    echo Found .env in backend/.
) else (
    echo [WARNING] .env not found!
    echo Please copy .env.example to .env and add your API keys.
    echo.
    pause
)

echo Starting LinguaAI Backend...
start cmd /k "title LinguaAI - Backend && py -3.11 -m uvicorn backend.main:app --reload --port 8001"

cd frontend
echo Starting LinguaAI Frontend...
start cmd /k "title LinguaAI - Frontend && npm run dev"

echo.
echo ============================================
echo   Uruchamianie...
echo   Backend:  http://localhost:8001
echo   Frontend: http://localhost:5173
echo ============================================
echo.
echo Za chwile otworz przegladarke na http://localhost:5173
echo.
timeout /t 3 /nobreak >nul
start http://localhost:5173
exit
