# Register-LinguaAI-Backup.ps1
# Registers a Windows Task Scheduler job to run daily backups of LinguaAI.db
#
# Usage (run as Administrator):
#   powershell -ExecutionPolicy Bypass -File scripts\register-backup-task.ps1
#
# Options:
#   -Time "02:00"    Backup time (default: 2:00 AM)
#   -Remove          Remove the scheduled task

param(
    [string]$Time = "02:00",
    [switch]$Remove
)

$TaskName = "LinguaAI-DailyBackup"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$BackupScript = Join-Path $ProjectRoot "scripts\backup.bat"

if ($Remove) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Scheduled task '$TaskName' removed." -ForegroundColor Yellow
    return
}

if (-not (Test-Path $BackupScript)) {
    Write-Error "Backup script not found: $BackupScript"
    exit 1
}

# Create the scheduled task
$Action = New-ScheduledTaskAction -Execute $BackupScript -WorkingDirectory $ProjectRoot
$Trigger = New-ScheduledTaskTrigger -Daily -At $Time
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Description "LinguaAI daily database backup (retention: 7 days)" `
        -Force

    Write-Host "Scheduled task '$TaskName' registered successfully." -ForegroundColor Green
    Write-Host "  Time:     $Time daily" -ForegroundColor Cyan
    Write-Host "  Script:   $BackupScript" -ForegroundColor Cyan
    Write-Host "  Backups:  $ProjectRoot\backups\" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To remove: powershell -File scripts\register-backup-task.ps1 -Remove" -ForegroundColor Gray
}
catch {
    Write-Error "Failed to register scheduled task: $_"
    exit 1
}
