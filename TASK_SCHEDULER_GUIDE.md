# Windows Task Scheduler Setup Guide

Complete step-by-step instructions for scheduling your YouTube automation system to run automatically using Windows Task Scheduler.

---

## Prerequisites

Before scheduling, ensure:

- ✅ Automation runs successfully manually: `python run_automation.py`
- ✅ YouTube OAuth completed (browser authorization done once)
- ✅ Virtual environment created (optional but recommended)
- ✅ All API keys configured in `.env` file

---

## Step-by-Step Setup

### Step 1: Open Task Scheduler

**Method 1 - Run Dialog:**
1. Press `Win + R`
2. Type: `taskschd.msc`
3. Press Enter

**Method 2 - Start Menu:**
1. Click Start
2. Type: "Task Scheduler"
3. Click on "Task Scheduler" app

### Step 2: Create New Task

1. In Task Scheduler, click **"Create Basic Task..."** in the right panel
   - Or: **Action** menu → **Create Basic Task...**

### Step 3: Name and Description

1. **Name**: `YouTube Kids Video Automation`
2. **Description**: 
   ```
   Automatically generates and uploads educational kids videos to YouTube.
   Runs daily to create 3-15 minute educational content for children.
   ```
3. Click **Next**

### Step 4: Set Trigger (When to Run)

1. Select: **Daily**
2. Click **Next**

3. Configure Daily Schedule:
   - **Start**: Today's date
   - **Start time**: `02:00:00` (2:00 AM recommended)
   - **Recur every**: `1` days
   
4. Click **Next**

**Why 2:00 AM?**
- Low internet traffic (faster uploads)
- Less API usage competition
- Won't interfere with daytime work
- Computer typically idle

### Step 5: Set Action (What to Run)

1. Select: **Start a program**
2. Click **Next**

3. Configure the Program/Script:

   **Program/script:**
   ```
   d:\Projects\YoutubeAutomate\run_automation.bat
   ```
   
   **Start in (optional):**
   ```
   d:\Projects\YoutubeAutomate
   ```
   
   **Add arguments (optional):** Leave blank

4. Click **Next**

### Step 6: Review and Finish

1. Review all settings
2. Check: **"Open the Properties dialog for this task when I click Finish"**
3. Click **Finish**

---

## Advanced Configuration (Properties Dialog)

The Properties dialog should open automatically. If not, right-click the task and select **Properties**.

### General Tab

Configure these settings:

1. **Security options:**
   - ✅ Select: **"Run whether user is logged on or not"**
   - ✅ Check: **"Run with highest privileges"**
   
2. **Configure for:** `Windows 10` (or your Windows version)

3. Click **OK** - You'll be prompted for your Windows password

### Triggers Tab

1. Double-click your trigger to edit

2. **Advanced settings:**
   - ✅ **Enabled**
   - ❌ **Stop task if it runs longer than:** Uncheck (or set to 3 hours)
   - ✅ **Repeat task every:** Leave unchecked (daily is enough)

3. **Expiration:** Leave unchecked (no expiration)

4. Click **OK**

### Actions Tab

Verify the action is correct:

**Action:** Start a program
**Details:** `d:\Projects\YoutubeAutomate\run_automation.bat`

**Alternative Setup (Direct Python):**

If you prefer calling Python directly without batch file:

1. Click **Edit**
2. **Program/script:**
   ```
   C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\python.exe
   ```
   *(Adjust path to your Python installation)*
   
3. **Add arguments:**
   ```
   run_automation.py
   ```
   
4. **Start in:**
   ```
   d:\Projects\YoutubeAutomate
   ```

**Finding Your Python Path:**
```powershell
# In PowerShell:
(Get-Command python).Path

# Or in Command Prompt:
where python
```

### Conditions Tab

Configure power and network settings:

1. **Power:**
   - ✅ **Start the task only if the computer is on AC power** (optional)
   - ❌ **Stop if the computer switches to battery power** (uncheck)
   - ✅ **Wake the computer to run this task** (important!)

2. **Network:**
   - ✅ **Start only if the following network connection is available:**
   - Select: **Any connection**

### Settings Tab

Configure execution and error recovery:

1. **General:**
   - ✅ **Allow task to be run on demand**
   - ✅ **Run task as soon as possible after a scheduled start is missed**
   - ✅ **If the task fails, restart every:** `1 hour`
   - ✅ **Attempt to restart up to:** `3 times`
   - ❌ **Stop the task if it runs longer than:** Uncheck or set to `3 hours`
   - ✅ **If the running task does not end when requested, force it to stop**

2. **If the task is already running:**
   - Select: **Do not start a new instance**

3. Click **OK**

---

## Verification and Testing

### Test the Scheduled Task

1. In Task Scheduler, find your task in the list
2. Right-click the task
3. Select **Run**
4. Watch the status in the Task Scheduler window
5. Check logs: `d:\Projects\YoutubeAutomate\logs\`

### Monitor Task Execution

**View Last Run Result:**
1. Select the task in Task Scheduler
2. Check the details pane at the bottom:
   - **Last Run Time**
   - **Last Run Result** (0x0 = success)
   - **Next Run Time**

**View Task History:**
1. Select the task
2. Click **History** tab at the bottom
3. Review all executions and events

**Check Automation Logs:**
```powershell
cd d:\Projects\YoutubeAutomate\logs
dir *.log /o-d
type automation_*.log
```

---

## Troubleshooting

### Task Doesn't Run

**Check Task Status:**
- Status should be "Ready"
- If "Disabled", right-click → Enable

**Verify Trigger:**
- Trigger should be enabled
- Check date/time is in the future
- Verify recurrence pattern

**Check Last Run Result:**
- `0x0` = Success
- `0x1` = Incorrect function or general error
- `0x41301` = Task is currently running
- `0x41303` = Task hasn't run yet

### Task Runs But Fails

**Check Windows Event Logs:**
1. Open Event Viewer (`eventvwr.msc`)
2. Navigate to: Windows Logs → Application
3. Look for Task Scheduler errors

**Check Automation Logs:**
```powershell
# View most recent log
cd d:\Projects\YoutubeAutomate\logs
Get-ChildItem *.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content
```

**Common Issues:**

1. **Python not found:**
   - Use full Python path in action
   - Or ensure Python is in system PATH

2. **Working directory wrong:**
   - Set "Start in" to project directory
   - Use absolute paths in script

3. **API keys not found:**
   - Environment variables may not load
   - Use `.env` file instead
   - Or set system-wide environment variables

4. **FFmpeg not found:**
   - Check `FFMPEG_PATH` in `.env`
   - Ensure FFmpeg is installed
   - Use absolute path

### Authentication Issues

**OAuth Token Expired:**

If YouTube upload fails with authentication error:

1. Delete the token file:
   ```powershell
   del d:\Projects\YoutubeAutomate\config\youtube_token.pickle
   ```

2. Run manually once to re-authenticate:
   ```powershell
   cd d:\Projects\YoutubeAutomate
   python run_automation.py
   ```

3. Browser will open for re-authorization
4. After success, scheduled task will work again

---

## Best Practices

### Scheduling Recommendations

**Frequency:**
- **Daily**: Most common (1 video per day)
- **Every other day**: More sustainable
- **Weekly**: For manual review workflow

**Time of Day:**
- **2:00 AM - 4:00 AM**: Optimal (low traffic, computer idle)
- **Avoid 9:00 AM - 5:00 PM**: Interferes with work
- **Avoid midnight**: System maintenance may run

**Days:**
- **Weekdays only**: More consistent audience
- **Weekends**: Lower competition on YouTube
- **Skip holidays**: Use calendar exceptions

### Multiple Videos Per Day

To schedule multiple runs:

1. Create separate tasks:
   - "YouTube Automation - Morning" (6:00 AM)
   - "YouTube Automation - Evening" (8:00 PM)

2. Or use "Repeat task every" in trigger:
   - Daily trigger
   - Repeat every: 12 hours
   - Duration: 1 day

### Quota Management

YouTube API has daily quotas:

- **Default quota**: 10,000 units per day
- **Video upload**: ~1,600 units
- **Limit**: ~6 uploads per day (realistic)

**Recommendation**: 1-2 videos per day maximum

### Monitoring Setup

**Enable Email Notifications (Optional):**

1. Task Properties → Actions
2. Add action: **Send an e-mail** (requires SMTP setup)
3. Configure:
   - To: your email
   - Subject: YouTube Automation Status
   - Text: Check logs for details

**Or use PowerShell script for notifications:**

Create `notify.ps1`:
```powershell
$lastLog = Get-ChildItem "d:\Projects\YoutubeAutomate\logs\*.log" | 
           Sort-Object LastWriteTime -Descending | 
           Select-Object -First 1

if ($lastLog) {
    $content = Get-Content $lastLog.FullName -Tail 20
    # Send notification (email, Discord, Slack, etc.)
}
```

---

## Maintenance

### Weekly Checks

1. **Review logs:** Check for errors or warnings
2. **Check YouTube:** Verify uploads are successful
3. **Monitor API usage:** Check OpenAI and ElevenLabs credits
4. **Review videos:** Ensure quality is maintained

### Monthly Maintenance

1. **Clean old files:**
   ```powershell
   # Delete videos older than 30 days
   Get-ChildItem "d:\Projects\YoutubeAutomate\output\videos\*.mp4" |
   Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} |
   Remove-Item
   ```

2. **Archive logs:**
   ```powershell
   # ZIP old logs
   Compress-Archive -Path "d:\Projects\YoutubeAutomate\logs\*.log" `
                    -DestinationPath "logs_archive_$(Get-Date -Format 'yyyy-MM').zip"
   ```

3. **Update dependencies:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

### Backup Strategy

**What to backup:**
- ✅ `config/client_secrets.json`
- ✅ `config/youtube_token.pickle`
- ✅ `.env` file
- ✅ Custom music files in `assets/music/`
- ✅ Logs (archive monthly)

**What NOT to backup:**
- ❌ Output videos (too large)
- ❌ Generated images (regenerate if needed)
- ❌ Voiceover files (regenerate if needed)

---

## Security Considerations

### File Permissions

Ensure proper permissions:
```powershell
# Set folder permissions (restrict access)
icacls "d:\Projects\YoutubeAutomate\config" /inheritance:r /grant:r "$env:USERNAME:(OI)(CI)F"
```

### API Key Protection

- ✅ Store API keys in `.env` file (not in code)
- ✅ Add `.env` to `.gitignore`
- ✅ Use Windows Credential Manager for sensitive data
- ❌ Never commit API keys to version control

### Task Account

**Running as your user account:**
- Pros: Easy setup, uses your credentials
- Cons: Requires you to stay logged in (unless "Run whether user is logged on or not" is set)

**Running as SYSTEM:**
- Pros: Runs without user login
- Cons: May have permission issues, OAuth may not work

**Recommendation:** Run as your user account with "Run whether user is logged on or not"

---

## Advanced Scheduling

### Conditional Execution

Create a wrapper script to run only on specific conditions:

**check_and_run.ps1:**
```powershell
# Only run if it's a weekday
$dayOfWeek = (Get-Date).DayOfWeek
if ($dayOfWeek -ne 'Saturday' -and $dayOfWeek -ne 'Sunday') {
    cd d:\Projects\YoutubeAutomate
    python run_automation.py
} else {
    Write-Host "Skipping: Weekend"
}
```

Schedule this script instead of the batch file.

### Dynamic Scheduling

Adjust duration based on time of day:

**smart_run.ps1:**
```powershell
$hour = (Get-Date).Hour

# Longer videos at night when more time available
if ($hour -ge 22 -or $hour -le 6) {
    $env:VIDEO_DURATION = "600"  # 10 minutes
} else {
    $env:VIDEO_DURATION = "240"  # 4 minutes
}

cd d:\Projects\YoutubeAutomate
python run_automation.py
```

---

## Summary Checklist

Before going live with scheduled automation:

- [ ] Manual run successful
- [ ] API keys configured
- [ ] YouTube OAuth completed
- [ ] FFmpeg installed and configured
- [ ] Task created in Task Scheduler
- [ ] "Run whether user is logged on or not" enabled
- [ ] "Wake computer to run this task" enabled
- [ ] Error recovery configured (restart 3 times)
- [ ] Test run via Task Scheduler successful
- [ ] Logs reviewed and working
- [ ] Computer stays on or auto-wakes
- [ ] Backup of config files created

---

## Getting Help

If you encounter issues:

1. **Check logs:** `logs/automation_*.log`
2. **Check Task Scheduler history**
3. **Run manually** to isolate problem
4. **Review error messages** in logs
5. **Verify all prerequisites** are met

**Common Commands:**
```powershell
# View recent logs
cd d:\Projects\YoutubeAutomate\logs
Get-ChildItem *.log | Sort-Object LastWriteTime -Descending | Select-Object -First 5

# Test Python path
python --version
(Get-Command python).Path

# Test FFmpeg
ffmpeg -version

# List scheduled tasks
schtasks /query /tn "YouTube Kids Video Automation" /v /fo list

# Run task manually
schtasks /run /tn "YouTube Kids Video Automation"
```

---

**Your automation is ready to run on schedule!** 🚀

Monitor the first few runs to ensure everything works smoothly, then let it run automatically every day!
