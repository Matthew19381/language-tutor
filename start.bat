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
start cmd /k "echo Installing Python dependencies... && pip install -r backend\requirements.txt && echo. && echo Starting backend on http://localhost:8000 && uvicorn backend.main:app --reload --port 8000"

cd frontend
echo Starting Language Tutor Frontend...
start cmd /k "echo Installing Node dependencies... && npm install && echo. && echo Starting frontend on http://localhost:5173 && npm run dev"

echo.
echo ============================================
echo   Services starting up...
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo ============================================
echo.
echo Both windows are opening. Wait for them to finish
echo installing dependencies before opening the browser.
echo.
pause
