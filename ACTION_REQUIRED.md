# Quick Setup Checklist - Action Required

Based on the test results, here's what you need to do to get your automation running:

---

## ✅ COMPLETED (No Action Needed)
- [x] Python 3.13.7 installed
- [x] Virtual environment configured
- [x] All Python packages installed
- [x] All modules import successfully
- [x] Directory structure created
- [x] Configuration files present

---

## ⚠️ ACTION REQUIRED

### 1. Install FFmpeg (CRITICAL for video creation)

**Option A - Using Chocolatey (Recommended):**
```powershell
# Install Chocolatey if you don't have it:
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install FFmpeg:
choco install ffmpeg
```

**Option B - Manual Installation:**
1. Download: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
2. Extract to `C:\ffmpeg`
3. Add to PATH or update FFMPEG_PATH in `.env`:
   ```
   FFMPEG_PATH=C:\ffmpeg\bin\ffmpeg.exe
   ```

**Verify Installation:**
```powershell
ffmpeg -version
```

---

### 2. Configure OpenAI API Key (REQUIRED)

**Get Your API Key:**
1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

**Update .env file:**
```powershell
# Edit d:\Projects\YoutubeAutomate\.env
OPENAI_API_KEY=sk-your-actual-key-here
```

**Note:** You need API credits. Check balance at: https://platform.openai.com/usage

---

### 3. Configure YouTube OAuth (REQUIRED for uploads)

**Step 1 - Get Client Secrets:**
1. Go to: https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `client_secret_*.json`

**Step 2 - Save File:**
```powershell
# Rename and move to:
d:\Projects\YoutubeAutomate\config\client_secrets.json
```

**Detailed Instructions:** See [SETUP.md](SETUP.md) Section 3

---

### 4. Configure ElevenLabs API (OPTIONAL - Better Voice Quality)

**If you skip this, the system will use free gTTS (Google Text-to-Speech)**

**To use ElevenLabs:**
1. Sign up: https://elevenlabs.io/
2. Get API key from: https://elevenlabs.io/app/settings/api-keys
3. Update `.env`:
   ```
   ELEVENLABS_API_KEY=your_elevenlabs_key_here
   ```

---

## 🧪 TEST AGAIN

After completing the steps above, run the test again:

```powershell
python test_system.py
```

---

## 🚀 RUN THE AUTOMATION

Once all tests pass (or at least FFmpeg + OpenAI are configured):

**Dry Run (Test without uploading):**
```powershell
# Comment out upload step in run_automation.py temporarily
python run_automation.py
```

**Full Run:**
```powershell
python run_automation.py
```

**First Run Notes:**
- Browser will open for YouTube OAuth (one-time setup)
- Takes 5-15 minutes depending on video length
- Check `logs/automation_*.log` for progress

---

## 📊 Current Test Results Summary

```
✅ All modules imported successfully (8/8)
✅ Directory structure complete (10/10)
⚠️  OpenAI API key is placeholder - REPLACE WITH REAL KEY
⚠️  FFmpeg not installed - INSTALL REQUIRED
⚠️  YouTube OAuth not configured - REQUIRED FOR UPLOADS
⚠️  ElevenLabs optional - Will use gTTS fallback
```

---

## 🆘 Quick Troubleshooting

**"ModuleNotFoundError":**
```powershell
python -m pip install -r requirements.txt --upgrade
```

**"FFmpeg not found":**
```powershell
# Check if installed:
where ffmpeg

# If not found, install using steps above
```

**"OpenAI API Error":**
- Verify key starts with `sk-`
- Check you have credits: https://platform.openai.com/usage
- Reload environment: restart terminal or reload .env

**"YouTube OAuth Error":**
- Verify client_secrets.json exists in config/
- Check file is valid JSON
- Run manually first for browser authorization

---

## 📁 File Locations

```
d:\Projects\YoutubeAutomate\
├── .env                          ← Edit API keys here
├── config\
│   └── client_secrets.json       ← Add YouTube OAuth file here
├── test_system.py                ← Run this to test
├── run_automation.py             ← Run this to create videos
└── logs\                         ← Check for errors
```

---

## 💡 Next Steps Priority

1. **CRITICAL**: Install FFmpeg
2. **CRITICAL**: Add real OpenAI API key to `.env`
3. **REQUIRED**: Add YouTube `client_secrets.json` for uploads
4. **OPTIONAL**: Add ElevenLabs API key for better voice
5. **TEST**: Run `python test_system.py` again
6. **RUN**: Execute `python run_automation.py`

---

## 💰 Cost Estimates

**Per Video (4 minutes):**
- OpenAI GPT-4: ~$0.20 (topic + script + metadata)
- DALL-E 3: ~$0.04-$0.08 (2-3 images)
- ElevenLabs: ~$0.10 (2000 characters) or **FREE with gTTS**
- **Total: $0.30-$0.40 per video** (or $0.20-$0.30 with free gTTS)

**Daily Cost (1 video/day):**
- ~$9-12/month
- ~$100-144/year

---

**Need help?** Check [SETUP.md](SETUP.md) for detailed instructions or [QUICKSTART.md](QUICKSTART.md) for a quick guide.
