# Environment Setup Tool

Automated `.env` file generator for YouTube Automation System.

## Quick Start

### Windows
```bash
setup_env.bat
```

### Linux/Mac
```bash
python setup_env.py
```

## What It Does

This interactive tool will guide you through configuring:

### 1. **API Keys**
- ✅ **Google Gemini API** (FREE - recommended)
  - Get from: https://makersuite.google.com/app/apikey
  - FREE tier: 60 requests/min, 1500/day
  
- 💰 **OpenAI API** (PAID - optional)
  - Get from: https://platform.openai.com/api-keys
  - Cost: ~$0.40 per video
  
- 💰 **ElevenLabs API** (PAID - optional)
  - Get from: https://elevenlabs.io/app/settings
  - FREE: 10,000 chars/month
  - Paid: $5/month for 30,000 chars

### 2. **Image Generation**
- 🎨 **Stable Diffusion** (FREE - local)
  - Choose from 4 FREE models
  - No API key needed for basic models
  - Optional Hugging Face token for gated models

### 3. **Text-to-Speech**
- 🎙️ **TTS Engine** (FREE options)
  - Auto: Best available (recommended)
  - Piper: High quality, fast
  - Coqui: Natural voices
  - gTTS: Simple, reliable

### 4. **Video Settings**
- 🎥 Duration, resolution, quality
- 📺 YouTube upload defaults
- 📚 Playlist IDs (optional)

## Features

✨ **Interactive Prompts** - Step-by-step guidance  
🔐 **Secure Input** - Hidden password entry for API keys  
💾 **Auto Backup** - Backs up existing .env before overwriting  
✅ **Validation** - Checks required fields  
📝 **Well Documented** - Comments explain each setting  

## Example Session

```
========================================================================
🚀 YOUTUBE AUTOMATION - ENVIRONMENT SETUP
========================================================================

This tool will help you configure your .env file with API keys.
Press Enter to skip optional fields.

----------------------------------------------------------------------
📝 Google Gemini API (FREE - RECOMMENDED)
----------------------------------------------------------------------
✅ 100% FREE tier: 60 requests/min, 1500 requests/day
📝 Get your FREE API key from: https://makersuite.google.com/app/apikey

Enter your Gemini API key: AIzaSy***************

----------------------------------------------------------------------
📝 OpenAI API (PAID - OPTIONAL)
----------------------------------------------------------------------
💰 Cost: ~$0.40 per video (DALL-E 3 + GPT-4)
⚠️  Only needed if you want paid system instead of FREE Gemini
📝 Get API key from: https://platform.openai.com/api-keys

Enter your OpenAI API key (or press Enter to skip): 

[... continues with other settings ...]
```

## Generated .env File

The tool creates a properly formatted `.env` file with:
- All API keys configured
- Sensible defaults for video settings
- Helpful comments for each section
- Ready to use with the automation system

## After Setup

1. **Review** your `.env` file:
   ```bash
   notepad .env
   ```

2. **Test** the automation:
   ```bash
   python run_automation.py --category kids --language en
   ```

3. **Edit** anytime manually:
   - Open `.env` in any text editor
   - Change values as needed
   - No need to run setup again

## Backup

If `.env` already exists, the tool will:
1. Ask if you want to overwrite
2. Create `.env.backup` before overwriting
3. Preserve your old configuration

## Manual Setup

Prefer manual setup? Copy `.env.example` to `.env`:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Then edit `.env` with your favorite text editor.

## Troubleshooting

**"Virtual environment not found"**
- Run `setup.bat` first to create the virtual environment

**"Module not found"**
- Activate virtual environment: `.venv\Scripts\activate`
- Or run: `python -m pip install python-dotenv`

**"Permission denied"**
- Run terminal/command prompt as Administrator
- Or check file permissions on `.env`

## Need Help?

- 📚 Documentation: See `SETUP.md` and `QUICKSTART.md`
- 🐛 Issues: Check `logs/` folder for error messages
- 💬 Support: Open an issue on GitHub

## Security Notes

⚠️ **Never commit `.env` to version control!**

The `.env` file contains sensitive API keys. It's already in `.gitignore` to prevent accidental commits.

✅ Safe to commit:
- `setup_env.py` (this tool)
- `setup_env.bat` (launcher)
- `.env.example` (template without real keys)

❌ Never commit:
- `.env` (contains real API keys)
- `.env.backup` (contains real API keys)
- `config/youtube_token.pickle` (OAuth credentials)
