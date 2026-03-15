# Language Tutor - PowerShell Launcher
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Language Tutor - AI-Powered Learning App" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "[WARNING] backend\.env not found!" -ForegroundColor Yellow
    Write-Host "Please create backend\.env from backend\.env.example"
    Write-Host "and add your GEMINI_API_KEY before starting."
    Write-Host ""
    Read-Host "Press Enter to continue anyway..."
}

$rootDir = $PWD.Path

Write-Host "Starting Language Tutor Backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "Set-Location '$rootDir'; " + `
    "Write-Host 'Installing Python dependencies...' -ForegroundColor Cyan; " + `
    "pip install -r backend\requirements.txt; " + `
    "Write-Host ''; " + `
    "Write-Host 'Starting backend on http://localhost:8000' -ForegroundColor Green; " + `
    "uvicorn backend.main:app --reload --port 8000"

Start-Sleep -Seconds 2

Write-Host "Starting Language Tutor Frontend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "Set-Location '$rootDir\frontend'; " + `
    "Write-Host 'Installing Node dependencies...' -ForegroundColor Cyan; " + `
    "npm install; " + `
    "Write-Host ''; " + `
    "Write-Host 'Starting frontend on http://localhost:5173' -ForegroundColor Green; " + `
    "npm run dev"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Services starting up..." -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Both windows are opening. Wait for them to finish"
Write-Host "installing dependencies before opening the browser."
Write-Host ""
Read-Host "Press Enter to exit this window"
