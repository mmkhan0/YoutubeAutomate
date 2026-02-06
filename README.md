# YouTube Automation System

A complete Python-based system for automatically generating and uploading YouTube videos using AI, designed to run on Windows via Task Scheduler.

## Features

- 🤖 **AI-Powered Content Generation**: Uses OpenAI GPT to select topics and write scripts
- 🎬 **Automated Video Creation**: Combines images, voiceover, and music using FFmpeg
- 📺 **YouTube Upload**: Automatically uploads videos with thumbnails via YouTube Data API
- 📅 **Task Scheduler Integration**: Runs automatically on schedule via Windows Task Scheduler
- 📊 **Comprehensive Logging**: Tracks all operations for monitoring and debugging
- 🎨 **Custom Thumbnails**: Generates attractive thumbnails automatically
- 🔊 **Text-to-Speech**: Converts scripts to natural voiceovers
- 🖼️ **Image Asset Management**: Downloads relevant images from Pexels API

## Project Structure

```
YoutubeAutomate/
├── main.py                      # Main entry point
├── run_automation.bat           # Batch script for Task Scheduler
├── setup.bat                    # Setup script
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore file
├── .env.example                 # Environment variables template
│
├── config/                      # Configuration files
│   ├── config.yaml              # Main configuration (not in git)
│   └── config.example.yaml      # Configuration template
│
├── src/                         # Source code modules
│   ├── __init__.py
│   ├── config_loader.py         # Configuration management
│   ├── logger_setup.py          # Logging configuration
│   ├── topic_selector.py        # AI topic selection
│   ├── script_generator.py      # AI script generation
│   ├── asset_generator.py       # Image/audio asset generation
│   ├── video_creator.py         # FFmpeg video compilation
│   ├── thumbnail_generator.py   # Thumbnail creation
│   ├── youtube_uploader.py      # YouTube API integration
│   └── utils.py                 # Utility functions
│
├── assets/                      # Asset storage
│   ├── images/                  # Downloaded/stored images
│   ├── music/                   # Background music files
│   └── fonts/                   # Fonts for thumbnails
│
├── output/                      # Generated content
│   ├── videos/                  # Compiled video files
│   └── thumbnails/              # Generated thumbnails
│
├── prompts/                     # Stored prompts and scripts
│   └── README.md
│
└── logs/                        # Application logs
    └── README.md
```

## Prerequisites

1. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
2. **FFmpeg** - [Download FFmpeg](https://ffmpeg.org/download.html)
3. **API Keys**:
   - OpenAI API Key - [Get API Key](https://platform.openai.com/)
   - YouTube Data API - [Google Cloud Console](https://console.cloud.google.com/)
   - Pexels API (optional) - [Get API Key](https://www.pexels.com/api/)

## Installation

### 1. Clone or Download the Project

```bash
cd d:\Projects\YoutubeAutomate
```

### 2. Run Setup Script

```bash
setup.bat
```

This will:
- Create a Python virtual environment
- Install all required dependencies
- Guide you through next steps

### 3. Configure the Application

#### A. Copy Configuration Template

```bash
copy config\config.example.yaml config\config.yaml
```

#### B. Edit `config\config.yaml` with your settings:

```yaml
api_keys:
  openai_api_key: "sk-your-actual-key-here"
  youtube_client_secrets: "config/client_secrets.json"
  pexels_api_key: "your-pexels-key-here"

paths:
  ffmpeg_path: "C:\\ffmpeg\\bin\\ffmpeg.exe"  # Update to your path
```

#### C. Set up YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop app)
5. Download the JSON file
6. Save it as `config/client_secrets.json`

### 4. Install FFmpeg

1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to a location (e.g., `C:\ffmpeg`)
3. Update the `ffmpeg_path` in `config\config.yaml`

### 5. Add Background Music

Place royalty-free MP3 files in `assets/music/` directory.

**Recommended Sources**:
- [YouTube Audio Library](https://www.youtube.com/audiolibrary)
- [Free Music Archive](https://freemusicarchive.org)

## Usage

### Manual Execution

```bash
# Activate virtual environment
venv\Scripts\activate

# Run the automation
python main.py
```

Or simply double-click `run_automation.bat`

### Windows Task Scheduler Setup

1. Open **Task Scheduler** (taskschd.msc)
2. Click **Create Basic Task**
3. Name: "YouTube Automation"
4. Trigger: Daily at 2:00 AM (or your preferred time)
5. Action: **Start a program**
   - Program: `d:\Projects\YoutubeAutomate\run_automation.bat`
   - Start in: `d:\Projects\YoutubeAutomate`
6. Finish the wizard
7. Right-click the task → **Properties**
8. Under **General** tab:
   - Check "Run whether user is logged on or not"
   - Check "Run with highest privileges"
9. Under **Settings** tab:
   - Uncheck "Stop task if it runs longer than"
   - Check "If the task fails, restart every: 1 hour"

## Configuration Options

### Video Settings

```yaml
video:
  target_duration_seconds: 180  # 3 minutes
  max_duration_seconds: 900     # 15 minutes
  resolution: "1920x1080"
  fps: 30
```

### Content Topics

Edit the topics list in `config.yaml`:

```yaml
content:
  topics:
    - "technology trends"
    - "science facts"
    - "productivity tips"
    # Add your own topics
```

### YouTube Settings

```yaml
youtube:
  privacy_status: "private"  # private, unlisted, or public
  category_id: "22"          # People & Blogs
  default_tags:
    - "educational"
    - "informative"
```

## Monitoring & Logs

Logs are stored in `logs/youtube_automation_YYYY-MM-DD.log`

Check logs for:
- Execution status
- Errors and warnings
- Video upload results
- API usage

## Troubleshooting

### Common Issues

**1. FFmpeg not found**
- Verify FFmpeg is installed
- Check `ffmpeg_path` in config.yaml
- Test: `ffmpeg -version` in command prompt

**2. OpenAI API Error**
- Verify API key is valid
- Check account has credits
- Review rate limits

**3. YouTube Upload Failed**
- Ensure client_secrets.json is correct
- Check OAuth token is valid (delete oauth_token.pickle to re-authenticate)
- Verify YouTube Data API is enabled

**4. Missing Dependencies**
- Run `pip install -r requirements.txt` again
- Ensure virtual environment is activated

**5. Image Download Fails**
- Check Pexels API key
- Verify internet connection
- System will continue with placeholder images

## Customization

### Change Video Style

Edit prompts in `src/script_generator.py` to customize:
- Narration style
- Scene structure
- Content format

### Use Different TTS

Replace gTTS in `src/asset_generator.py` with:
- ElevenLabs (higher quality, paid)
- Azure TTS
- Amazon Polly

### Custom Thumbnails

Modify `src/thumbnail_generator.py` to change:
- Colors and gradients
- Text styling
- Layout

## API Costs (Estimated per video)

- **OpenAI GPT-4**: ~$0.10-0.30 per video
- **Pexels**: Free (5000 requests/month)
- **YouTube API**: Free (quota-based)
- **gTTS**: Free

For high-quality voice with ElevenLabs: ~$0.30-0.50 per video

## Safety & Best Practices

1. **Start with Private Videos**: Set `privacy_status: private` initially
2. **Review Before Publishing**: Check videos before making public
3. **Copyright Compliance**: Only use royalty-free music and images
4. **API Rate Limits**: Monitor API usage to avoid rate limiting
5. **Backup Configuration**: Keep backups of config files (without API keys)
6. **Monitor Logs**: Regularly check logs for errors

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review configuration in `config/config.yaml`
3. Verify all API keys and credentials are correct

## Version

Version 1.0.0 - February 2026
