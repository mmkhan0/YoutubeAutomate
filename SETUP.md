# Setup Guide for YouTube Automation System

This guide walks you through the complete setup process for the YouTube automation system on Windows.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Python Setup](#python-setup)
3. [FFmpeg Installation](#ffmpeg-installation)
4. [API Credentials Setup](#api-credentials-setup)
5. [Project Configuration](#project-configuration)
6. [Task Scheduler Setup](#task-scheduler-setup)
7. [Testing](#testing)

---

## System Requirements

- **Operating System**: Windows 10/11
- **Python**: 3.8 or higher
- **RAM**: 4 GB minimum (8 GB recommended)
- **Storage**: 5 GB free space minimum
- **Internet**: Stable connection for API calls and uploads

---

## Python Setup

### 1. Install Python

1. Download Python from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```cmd
   python --version
   ```

### 2. Set Up Virtual Environment

```cmd
cd d:\Projects\YoutubeAutomate
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

---

## FFmpeg Installation

### Method 1: Manual Installation

1. Download FFmpeg from [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - Click "Windows builds from gyan.dev"
   - Download "ffmpeg-release-essentials.zip"

2. Extract the archive to `C:\ffmpeg`

3. Verify the structure:
   ```
   C:\ffmpeg\
   └── bin\
       ├── ffmpeg.exe
       ├── ffplay.exe
       └── ffprobe.exe
   ```

4. Test FFmpeg:
   ```cmd
   C:\ffmpeg\bin\ffmpeg.exe -version
   ```

### Method 2: Using Chocolatey (if installed)

```cmd
choco install ffmpeg
```

---

## API Credentials Setup

### OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy the key (it starts with `sk-`)
6. **Save it immediately** - you won't see it again

### Pexels API Key (Optional but Recommended)

1. Go to [pexels.com/api](https://www.pexels.com/api/)
2. Sign up for a free account
3. Generate API key
4. Free tier: 200 requests/hour, 20,000/month

### YouTube Data API Setup

This is the most complex setup. Follow carefully:

#### Step 1: Create Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name: "YouTube Automation"
4. Click "Create"

#### Step 2: Enable YouTube Data API v3

1. In the Cloud Console, go to "APIs & Services" → "Library"
2. Search for "YouTube Data API v3"
3. Click on it and click "Enable"

#### Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Select "External" (unless you have Google Workspace)
3. Fill in:
   - App name: "YouTube Automation"
   - User support email: your email
   - Developer contact: your email
4. Click "Save and Continue"
5. Click "Add or Remove Scopes"
   - Search and add: `https://www.googleapis.com/auth/youtube.upload`
6. Click "Save and Continue"
7. Add your email as a test user
8. Click "Save and Continue"

#### Step 4: Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: **Desktop app**
4. Name: "YouTube Automation Desktop"
5. Click "Create"
6. Click "Download JSON"
7. Save the file as `client_secrets.json` in the `config/` directory

---

## Project Configuration

### 1. Create Configuration File

```cmd
cd d:\Projects\YoutubeAutomate
copy config\config.example.yaml config\config.yaml
```

### 2. Edit Configuration

Open `config\config.yaml` in a text editor and update:

```yaml
api_keys:
  openai_api_key: "sk-your-actual-openai-key-here"
  youtube_client_secrets: "config/client_secrets.json"
  pexels_api_key: "your-actual-pexels-key"

paths:
  ffmpeg_path: "C:\\ffmpeg\\bin\\ffmpeg.exe"  # Use double backslashes

video:
  target_duration_seconds: 180  # 3 minutes
  resolution: "1920x1080"
  fps: 30

youtube:
  privacy_status: "private"  # Start with private for testing
  category_id: "22"  # People & Blogs
```

### 3. Add Background Music

1. Download royalty-free music from:
   - [YouTube Audio Library](https://studio.youtube.com/channel/UCT2s7z6UjAwgWj4p7EJl2FA/music)
   - [Free Music Archive](https://freemusicarchive.org/)

2. Save MP3 files to: `assets\music\`

**Recommended**: Download 3-5 different tracks for variety

---

## Task Scheduler Setup

### Create Scheduled Task

1. **Open Task Scheduler**
   - Press `Win + R`
   - Type `taskschd.msc`
   - Press Enter

2. **Create Basic Task**
   - Click "Create Basic Task..." (right sidebar)
   - Name: `YouTube Video Automation`
   - Description: `Automatically generates and uploads YouTube videos`
   - Click "Next"

3. **Set Trigger**
   - Choose: "Daily"
   - Click "Next"
   - Start date: Today's date
   - Start time: `02:00:00` (2 AM)
   - Recur every: `1` days
   - Click "Next"

4. **Set Action**
   - Choose: "Start a program"
   - Click "Next"
   - Program/script: `d:\Projects\YoutubeAutomate\run_automation.bat`
   - Start in: `d:\Projects\YoutubeAutomate`
   - Click "Next"

5. **Finish**
   - Check "Open the Properties dialog..."
   - Click "Finish"

### Configure Advanced Settings

In the Properties dialog that opens:

**General Tab:**
- ✅ Run whether user is logged on or not
- ✅ Run with highest privileges
- Configure for: Windows 10

**Triggers Tab:**
- Double-click the trigger
- ✅ Enabled
- Advanced settings:
  - ✅ Stop task if it runs longer than: `3 hours`

**Actions Tab:**
- Verify the action is correct

**Conditions Tab:**
- ✅ Start only if the computer is on AC power (optional)
- ✅ Wake the computer to run this task

**Settings Tab:**
- ✅ Allow task to be run on demand
- ✅ Run task as soon as possible after a scheduled start is missed
- ✅ If the task fails, restart every: `1 hour`
- ✅ Attempt to restart up to: `3 times`
- ❌ Stop the task if it runs longer than (uncheck or set to 3 hours)

Click "OK" and enter your Windows password if prompted.

---

## Testing

### Test 1: Manual Python Execution

```cmd
cd d:\Projects\YoutubeAutomate
venv\Scripts\activate
python main.py
```

**Expected outcome:**
- Console shows progress messages
- Log file created in `logs/`
- Video created in `output/videos/`
- Video uploaded to YouTube (check your channel)

### Test 2: Batch File Execution

```cmd
cd d:\Projects\YoutubeAutomate
run_automation.bat
```

**Expected outcome:** Same as Test 1

### Test 3: Task Scheduler Execution

1. Open Task Scheduler
2. Find "YouTube Video Automation"
3. Right-click → "Run"
4. Monitor the task status
5. Check logs after completion

### Test 4: YouTube OAuth First Run

The first time the script runs, it will:
1. Open your default web browser
2. Ask you to log in to Google
3. Ask for permission to upload videos
4. Save the authentication token

**Important**: This must happen while you're present the first time. After that, it runs automatically.

---

## Verification Checklist

After setup, verify:

- [ ] Python 3.8+ installed and in PATH
- [ ] Virtual environment created and dependencies installed
- [ ] FFmpeg installed and working
- [ ] OpenAI API key configured and valid
- [ ] YouTube OAuth credentials (client_secrets.json) in place
- [ ] Pexels API key configured (optional)
- [ ] config.yaml created and filled out
- [ ] Background music files added to assets/music/
- [ ] First OAuth authentication completed successfully
- [ ] Manual test run successful
- [ ] Task Scheduler task created and tested
- [ ] Log files being generated properly

---

## Troubleshooting

### Issue: "Python not found"

**Solution:**
- Reinstall Python with "Add to PATH" checked
- Or manually add Python to PATH:
  1. Search for "Environment Variables"
  2. Edit "Path" variable
  3. Add Python installation directory

### Issue: "FFmpeg not found"

**Solution:**
- Verify FFmpeg is at the path specified in config.yaml
- Test: `C:\ffmpeg\bin\ffmpeg.exe -version`
- Check for typos in the path (remember double backslashes)

### Issue: YouTube OAuth fails

**Solution:**
- Check that YouTube Data API v3 is enabled
- Verify client_secrets.json is in the config/ directory
- Delete `config/oauth_token.pickle` and try again
- Make sure your email is added as a test user

### Issue: Task Scheduler task fails

**Solution:**
- Check that paths are absolute, not relative
- Verify "Start in" directory is set correctly
- Try running with "Run with highest privileges"
- Check logs for error details

### Issue: OpenAI API errors

**Solution:**
- Verify API key is correct (starts with sk-)
- Check account has available credits
- Review rate limits at platform.openai.com

---

## Next Steps

Once everything is working:

1. **Monitor First Few Runs**: Check videos before publishing
2. **Adjust Topics**: Edit topics list in config.yaml
3. **Customize Prompts**: Modify prompts in script_generator.py
4. **Switch to Public**: Change `privacy_status` to "public" when ready
5. **Add More Music**: Expand music library for variety
6. **Review Logs**: Regularly check logs/ directory

---

## Support Resources

- **FFmpeg Documentation**: [ffmpeg.org/documentation.html](https://ffmpeg.org/documentation.html)
- **YouTube API Docs**: [developers.google.com/youtube/v3](https://developers.google.com/youtube/v3)
- **OpenAI API Docs**: [platform.openai.com/docs](https://platform.openai.com/docs)
- **Python Documentation**: [docs.python.org](https://docs.python.org/)

---

**Setup Complete!** Your YouTube automation system is ready to run.
