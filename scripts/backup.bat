@echo off
REM LinguaAI Daily Backup Script
REM Run via Windows Task Scheduler for automated daily backups

cd /d "%~dp0.."
echo [%date% %time%] Starting LinguaAI backup...

python -m backend.services.backup_service

if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] Backup completed successfully.
) else (
    echo [%date% %time%] Backup FAILED with error code %ERRORLEVEL%.
    exit /b 1)
