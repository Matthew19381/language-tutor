# LinguaAI - PowerShell Launcher
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  LinguaAI - AI-Powered Learning App" -ForegroundColor Cyan
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

Write-Host "Starting LinguaAI Backend..." -ForegroundColor Green
$backendCmd = "Set-Location '$rootDir'; Write-Host 'Starting backend on http://localhost:8000' -ForegroundColor Green; py -3.11 -m pip install -r backend\requirements.txt; py -3.11 -m uvicorn backend.main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

Start-Sleep -Seconds 2

Write-Host "Starting LinguaAI Frontend..." -ForegroundColor Green
$frontendCmd = "Set-Location '$rootDir\frontend'; Write-Host 'Starting frontend on http://localhost:5173' -ForegroundColor Green; npm install; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Services starting up..." -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Both windows are opening. Wait a moment before opening the browser."
Write-Host ""
Read-Host "Press Enter to exit this window"
