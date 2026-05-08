@echo off
cd /d "%~dp0"
python backup_db.py
if errorlevel 1 (
    echo Backup failed!
    exit /b 1
) else (
    echo Backup completed successfully.
)
