# Database Backup Instructions

## Manual backup

```bash
cd backend/scripts
python backup_db.py
```

## Automated daily backup

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task → "LinguaAI DB Backup"
3. Trigger: Daily at 3:00 AM
4. Action: Start a program
   - Program: `C:\Projects\LinguaAI\backend\scripts\backup_db.bat`
   - Start in: `C:\Projects\LinguaAI\backend\scripts\`

### Linux/Mac (cron)

```bash
# Edit crontab
crontab -e

# Add daily backup at 3:00 AM
0 3 * * * cd /path/to/LinguaAI/backend/scripts && python backup_db.py >> backup.log 2>&1
```

## Backup location

Backups are stored in: `backend/backups/`

- Format: `lingua_ai_YYYY-MM-DD_HH-MM-SS.db`
- Retention: Last 7 backups are kept automatically
