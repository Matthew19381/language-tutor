@echo off
REM Run this script once from the language-tutor\ directory to register
REM Windows Task Scheduler tasks for Discord notifications.
REM
REM Usage: cd language-tutor && backend\setup_scheduler.bat

set SCRIPT_DIR=%~dp0
set PYTHON=python
set NOTIFIER=%SCRIPT_DIR%..\backend\notifier.py

echo Creating LangTutor-Morning task (daily at 08:00)...
schtasks /create /tn "LangTutor-Morning" /tr "%PYTHON% \"%NOTIFIER%\"" /sc daily /st 08:00 /f
if %ERRORLEVEL% EQU 0 (
    echo   [OK] LangTutor-Morning created
) else (
    echo   [FAIL] Could not create LangTutor-Morning
)

echo Creating LangTutor-Evening task (daily at 18:00)...
schtasks /create /tn "LangTutor-Evening" /tr "%PYTHON% \"%NOTIFIER%\"" /sc daily /st 18:00 /f
if %ERRORLEVEL% EQU 0 (
    echo   [OK] LangTutor-Evening created
) else (
    echo   [FAIL] Could not create LangTutor-Evening
)

echo.
echo Done. To verify:
echo   schtasks /query /tn "LangTutor-Morning"
echo   schtasks /query /tn "LangTutor-Evening"
echo.
echo To remove tasks:
echo   schtasks /delete /tn "LangTutor-Morning" /f
echo   schtasks /delete /tn "LangTutor-Evening" /f
pause
