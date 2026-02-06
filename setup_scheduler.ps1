# PowerShell script to create Windows Task Scheduler task for YouTube Automation
# Run this script as Administrator

$TaskName = "YouTube Kids Video Automation"
$PythonExe = "D:\Projects\YoutubeAutomate\.venv\Scripts\python.exe"
$ScriptPath = "D:\Projects\YoutubeAutomate"
$ScriptFile = "run_automation.py"
$Arguments = "--test-mode"
$StartTime = "02:00AM"

Write-Host "Creating Task Scheduler task for YouTube Automation..." -ForegroundColor Cyan
Write-Host ""

# Create the action
$Action = New-ScheduledTaskAction -Execute $PythonExe `
    -Argument "$ScriptFile $Arguments" `
    -WorkingDirectory $ScriptPath

# Create the trigger (daily at 2 AM)
$Trigger = New-ScheduledTaskTrigger -Daily -At $StartTime

# Create settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -WakeToRun `
    -RestartInterval (New-TimeSpan -Minutes 60) `
    -RestartCount 3

# Create principal (run as current user with highest privileges)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType S4U `
    -RunLevel Highest

# Check if task already exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($ExistingTask) {
    Write-Host "Task already exists. Updating..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Register the task
Register-ScheduledTask -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Automatically generates and uploads educational kids videos to YouTube daily"

Write-Host ""
Write-Host "✓ Task created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Task Details:" -ForegroundColor Cyan
Write-Host "  Name: $TaskName"
Write-Host "  Schedule: Daily at $StartTime"
Write-Host "  Python: $PythonExe"
Write-Host "  Script: $ScriptPath\$ScriptFile"
Write-Host "  Arguments: $Arguments"
Write-Host ""
Write-Host "To test the task immediately, run:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
Write-Host ""
Write-Host "To view the task:" -ForegroundColor Yellow
Write-Host "  Get-ScheduledTask -TaskName '$TaskName' | Format-List *" -ForegroundColor White
Write-Host ""
Write-Host "To view task history:" -ForegroundColor Yellow
Write-Host "  Get-ScheduledTaskInfo -TaskName '$TaskName'" -ForegroundColor White
Write-Host ""
