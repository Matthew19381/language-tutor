@echo off
REM Run this script once from the LinguaAI\ directory to register
REM Windows Task Scheduler tasks for Discord notifications.
REM
REM Usage: cd LinguaAI && backend\setup_scheduler.bat

set SCRIPT_DIR=%~dp0
set PYTHON=python
set NOTIFIER=%SCRIPT_DIR%..\backend\notifier.py

echo Creating LinguaAI-Morning task (daily at 08:00)...
schtasks /create /tn "LinguaAI-Morning" /tr "%PYTHON% \"%NOTIFIER%\"" /sc daily /st 08:00 /f
if %ERRORLEVEL% EQU 0 (
    echo   [OK] LinguaAI-Morning created
) else (
    echo   [FAIL] Could not create LinguaAI-Morning
)

echo Creating LinguaAI-Evening task (daily at 18:00)...
schtasks /create /tn "LinguaAI-Evening" /tr "%PYTHON% \"%NOTIFIER%\"" /sc daily /st 18:00 /f
if %ERRORLEVEL% EQU 0 (
    echo   [OK] LinguaAI-Evening created
) else (
    echo   [FAIL] Could not create LinguaAI-Evening
)

echo.
echo Done. To verify:
echo   schtasks /query /tn "LinguaAI-Morning"
echo   schtasks /query /tn "LinguaAI-Evening"
echo.
echo To remove tasks:
echo   schtasks /delete /tn "LinguaAI-Morning" /f
echo   schtasks /delete /tn "LinguaAI-Evening" /f
pause
