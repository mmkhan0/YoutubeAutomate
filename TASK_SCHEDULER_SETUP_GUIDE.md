# Windows Task Scheduler Setup Guide

## 🚀 Quick Start - Choose Your Method

### ✅ METHOD 1: Automatic Setup (Easiest)

1. **Right-click PowerShell** → Select **"Run as Administrator"**
2. Run these commands:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   cd D:\Projects\YoutubeAutomate
   .\setup_scheduler.ps1
   ```
3. Done! Your task is created and ready to run.

---

### 📋 METHOD 2: Manual Setup (Step-by-Step)

## Step 1: Open Task Scheduler

1. Press `Windows + R`
2. Type: `taskschd.msc`
3. Press `Enter`

## Step 2: Create Basic Task

1. Click **"Create Basic Task"** in the right panel
2. **Name**: `YouTube Kids Video Automation`
3. **Description**: `Generates and uploads educational videos for kids`
4. Click **"Next"**

## Step 3: Set Trigger (When to Run)

1. Select: **"Daily"**
2. Click **"Next"**
3. **Start date**: Today's date
4. **Start time**: `09:00 AM` (or your preferred time)
5. **Recur every**: `1 days`
6. Click **"Next"**

## Step 4: Set Action

1. Select: **"Start a program"**
2. Click **"Next"**

## Step 5: Configure Program (IMPORTANT!)

### Option A: Using CMD (Recommended)

**Program/script:**
```
C:\Windows\System32\cmd.exe
```

**Add arguments:**
```
/c "D:\Projects\YoutubeAutomate\run_scheduled.bat"
```

**Start in:**
```
D:\Projects\YoutubeAutomate
```

### Option B: Direct Batch File

**Program/script:**
```
D:\Projects\YoutubeAutomate\run_scheduled.bat
```

**Add arguments:**
```
(Leave empty)
```

**Start in:**
```
D:\Projects\YoutubeAutomate
```

Click **"Next"**

## Step 6: Review and Finish

1. ☑️ Check **"Open the Properties dialog when I click Finish"**
2. Click **"Finish"**

## Step 7: Advanced Settings (CRITICAL!)

A Properties dialog will open. Configure these tabs:

### General Tab
- ☑️ **Run whether user is logged on or not**
- ☑️ **Run with highest privileges**
- ☑️ **Hidden** (optional - hides window when running)

### Triggers Tab
- Double-click your trigger to edit
- ☑️ **Enabled**
- Set your preferred schedule time

### Conditions Tab
- ☐ **Start the task only if the computer is on AC power** (UNCHECK THIS)
- ☑️ **Wake the computer to run this task**
- ☑️ **Start only if the following network connection is available: Any connection**

### Settings Tab
- ☑️ **Allow task to be run on demand**
- ☑️ **Run task as soon as possible after a scheduled start is missed**
- ☐ **Stop the task if it runs longer than** (UNCHECK - videos take time!)
- **If the running task does not end when requested**: Leave running
- **If the task is already running**: Do not start a new instance

Click **"OK"** and enter your Windows password when prompted.

---

## 🧪 Step 8: Test the Task

1. In Task Scheduler, find **"YouTube Kids Video Automation"**
2. Right-click on the task
3. Click **"Run"**
4. Watch the **Status** column - it should say "Running"
5. Wait 5-15 minutes for video generation to complete

## ✅ Step 9: Verify It Worked

### Check Logs
```
D:\Projects\YoutubeAutomate\logs\scheduler_runs.log
```

### Check Output
```
D:\Projects\YoutubeAutomate\output\videos\
```

### In Task Scheduler
- Click the **"History"** tab to see run details
- **Last Run Time** should show recent timestamp
- **Last Run Result** should show: `(0x0)` - Success

---

## 🔧 Troubleshooting

### ❌ Issue 1: Task runs but nothing happens

**Symptoms:**
- Task shows as "Completed" but no video generated
- No logs created

**Solutions:**
1. Verify **"Start in"** directory is set correctly:
   ```
   D:\Projects\YoutubeAutomate
   ```
2. Check batch file exists:
   ```
   D:\Projects\YoutubeAutomate\run_scheduled.bat
   ```
3. Verify task is set to **"Run with highest privileges"**
4. Test batch file manually first:
   ```powershell
   cd D:\Projects\YoutubeAutomate
   .\run_scheduled.bat
   ```

### ❌ Issue 2: Task says "Running" but never completes

**Symptoms:**
- Task status stuck on "Running" for hours
- Task gets killed after 3 days

**Solutions:**
1. In **Settings** tab, **UNCHECK** "Stop the task if it runs longer than"
2. Video generation takes 5-15 minutes normally - be patient
3. Check logs to see what step it's on
4. Ensure OpenAI/Gemini API keys are valid

### ❌ Issue 3: Access denied or task won't save

**Symptoms:**
- "Access is denied" error when saving
- Can't enable "Run whether user is logged on or not"

**Solutions:**
1. **Close Task Scheduler completely**
2. Right-click **Task Scheduler** → **"Run as Administrator"**
3. Try creating the task again
4. Enter your Windows password when prompted
5. Make sure you have administrator rights on your account

### ❌ Issue 4: Python/Virtual environment errors

**Symptoms:**
- Errors about Python not found
- Module import errors
- Virtual environment activation failed

**Solutions:**
1. Test batch file manually:
   ```powershell
   cd D:\Projects\YoutubeAutomate
   .\run_scheduled.bat
   ```
2. If manual test works, the Task Scheduler setup is wrong
3. Verify **"Start in"** directory is correct
4. Check `.venv` folder exists in `D:\Projects\YoutubeAutomate`

### ❌ Issue 5: Task never runs at scheduled time

**Symptoms:**
- Task shows up but never executes
- "Next Run Time" stays the same

**Solutions:**
1. Ensure **computer is on** at scheduled time (not sleep/hibernate)
2. Enable **"Wake the computer to run this task"** in Conditions tab
3. Enable **"Run task as soon as possible after missed start"** in Settings
4. Check trigger is **enabled** in Triggers tab
5. Verify trigger time is in the future, not past

### ❌ Issue 6: Task runs but YouTube upload fails

**Symptoms:**
- Video generates successfully
- Upload step fails or hangs

**Solutions:**
1. Check YouTube credentials in `config/youtube_token.pickle`
2. Re-authenticate YouTube:
   ```powershell
   python run_automation.py --test-mode
   ```
   Complete the OAuth flow manually
3. Verify internet connection is stable
4. Check YouTube API quota hasn't been exceeded

---

## 📊 Recommended Schedules

### Conservative (1 video/day)
- **Time**: 09:00 AM
- **Reason**: Safe for channel growth, YouTube-friendly

### Moderate (3 videos/day)
- **Times**: 09:00 AM, 02:00 PM, 08:00 PM
- **Reason**: Good engagement spread across day

### Aggressive (5 videos/day)
- **Times**: 08:00 AM, 11:00 AM, 02:00 PM, 05:00 PM, 08:00 PM
- **Reason**: Maximum content output (be careful with YouTube limits)

---

## 🔍 Monitoring Your Task

### View Task Details
```powershell
Get-ScheduledTask -TaskName "YouTube Kids Video Automation" | Format-List *
```

### View Last Run Info
```powershell
Get-ScheduledTaskInfo -TaskName "YouTube Kids Video Automation"
```

### View Task History
1. Open Task Scheduler
2. Select your task
3. Click **"History"** tab (enable Actions → Enable All Task History if greyed out)
4. Look for:
   - **Event ID 100**: Task started
   - **Event ID 102**: Task completed
   - **Event ID 103**: Task failed

### Check Logs
```powershell
Get-Content "D:\Projects\YoutubeAutomate\logs\scheduler_runs.log" -Tail 50
```

---

## 🛡️ Security Notes

1. **Credentials Storage**: Your YouTube credentials are stored in:
   ```
   D:\Projects\YoutubeAutomate\config\youtube_token.pickle
   ```
   Keep this file secure!

2. **API Keys**: Your API keys are in `.env` file:
   ```
   D:\Projects\YoutubeAutomate\.env
   ```
   Never share this file!

3. **Run as Administrator**: Task needs admin rights to:
   - Access virtual environment
   - Write to output folders
   - Access network for API calls

---

## 📝 Quick Copy-Paste Values

### For Task Scheduler Setup

**Task Name:**
```
YouTube Kids Video Automation
```

**Program/script:**
```
C:\Windows\System32\cmd.exe
```

**Add arguments:**
```
/c "D:\Projects\YoutubeAutomate\run_scheduled.bat"
```

**Start in:**
```
D:\Projects\YoutubeAutomate
```

---

## ✅ Final Checklist

Before considering your setup complete, verify:

- [ ] Task created in Task Scheduler
- [ ] Task set to "Run whether user is logged on or not"
- [ ] Task set to "Run with highest privileges"
- [ ] "Stop task if runs longer than" is UNCHECKED
- [ ] "Start in" directory is correct
- [ ] Batch file exists and is accessible
- [ ] Task test run completed successfully
- [ ] Video was generated in output folder
- [ ] Logs show successful completion
- [ ] YouTube video was uploaded (if auto_upload enabled)
- [ ] Scheduled time is correct and in future

---

## 🆘 Still Having Issues?

1. **Test manually first:**
   ```powershell
   cd D:\Projects\YoutubeAutomate
   .\run_scheduled.bat
   ```
   
2. **Check these files exist:**
   - `D:\Projects\YoutubeAutomate\run_scheduled.bat`
   - `D:\Projects\YoutubeAutomate\.venv\Scripts\python.exe`
   - `D:\Projects\YoutubeAutomate\run_automation.py`

3. **Verify permissions:**
   - You have write access to `D:\Projects\YoutubeAutomate`
   - Task Scheduler opened as Administrator
   - Windows Firewall allows Python network access

4. **Check specific errors:**
   - Open PowerShell as Administrator
   - Run: `Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" -MaxEvents 20`
   - Look for error messages related to your task

---

## 🎉 Success!

Once everything is working:
- Your videos will generate automatically at scheduled times
- Videos upload to YouTube with scheduled publishing (15 min delay)
- Thumbnails, music, and playlists are automatically created
- SEO optimization is applied
- Logs track every run

Sit back and let the automation work for you! 🚀
