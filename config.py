"""
Configuration file for YouTube Automation System

This file contains all configuration settings for the automated video generation system.
Sensitive values (API keys) should be loaded from environment variables.

To set environment variables on Windows:
    setx OPENAI_API_KEY "your-key-here"
    setx ELEVENLABS_API_KEY "your-key-here"

Or use a .env file (see .env.example)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# PROJECT PATHS
# ============================================================================

# Base directory of the project
BASE_DIR = Path(__file__).parent.absolute()

# Asset directories
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
MUSIC_DIR = ASSETS_DIR / "music"
FONTS_DIR = ASSETS_DIR / "fonts"

# Output directories
OUTPUT_DIR = BASE_DIR / "output"
VIDEOS_DIR = OUTPUT_DIR / "videos"
THUMBNAILS_DIR = OUTPUT_DIR / "thumbnails"

# Other directories
PROMPTS_DIR = BASE_DIR / "prompts"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"


# ============================================================================
# API KEYS AND CREDENTIALS
# ============================================================================

# OpenAI API Key for content generation
# Get your key from: https://platform.openai.com/api-keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")

# ElevenLabs API Key for high-quality text-to-speech (optional)
# Get your key from: https://elevenlabs.io/
# Leave empty to use free gTTS instead
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# Pexels API Key for stock images (optional but recommended)
# Get your key from: https://www.pexels.com/api/
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# YouTube OAuth 2.0 Client Secrets file path
# Download from Google Cloud Console after setting up YouTube Data API
YOUTUBE_CLIENT_SECRETS = str(CONFIG_DIR / "client_secrets.json")
YOUTUBE_CLIENT_SECRETS_FILE = YOUTUBE_CLIENT_SECRETS  # Alias for compatibility

# YouTube OAuth token storage (automatically generated after first auth)
YOUTUBE_OAUTH_TOKEN = str(CONFIG_DIR / "oauth_token.pickle")


# ============================================================================
# AI/CONTENT GENERATION SETTINGS
# ============================================================================

# OpenAI model to use for content generation
# Options: "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"
# gpt-4 is more creative but more expensive
# gpt-3.5-turbo is faster and cheaper
AI_MODEL = "gpt-4"

# Temperature for AI responses (0.0 - 2.0)
# Higher = more creative/random, Lower = more focused/deterministic
AI_TEMPERATURE = 0.7

# Maximum tokens for AI responses
AI_MAX_TOKENS = 2000

# Language for content generation and text-to-speech
CONTENT_LANGUAGE = "en"

# Target audience
TARGET_AUDIENCE = "general"  # general, teens, adults, children

# Video style
VIDEO_STYLE = "educational"  # educational, entertainment, listicle, documentary


# ============================================================================
# VIDEO GENERATION SETTINGS
# ============================================================================

# Minimum video duration in seconds (3 minutes)
VIDEO_MIN_DURATION = 180

# Maximum video duration in seconds (15 minutes)
VIDEO_MAX_DURATION = 900

# Target video duration in seconds (5 minutes default)
VIDEO_TARGET_DURATION = 300

# Video resolution (width x height)
VIDEO_RESOLUTION = "1920x1080"  # 1080p HD

# Frames per second
VIDEO_FPS = 30

# Video codec for encoding
VIDEO_CODEC = "libx264"

# Audio codec for encoding
AUDIO_CODEC = "aac"

# Video bitrate (quality)
VIDEO_BITRATE = "5000k"  # 5 Mbps for high quality

# Audio bitrate
AUDIO_BITRATE = "192k"

# Background music volume (0.0 - 1.0)
# 0.2 = 20% volume so it doesn't overpower narration
BACKGROUND_MUSIC_VOLUME = 0.2


# ============================================================================
# FFMPEG SETTINGS
# ============================================================================

# Path to FFmpeg executable
# Update this to match your FFmpeg installation
# Windows default locations to try:
#   - C:\ffmpeg\bin\ffmpeg.exe
#   - C:\Program Files\ffmpeg\bin\ffmpeg.exe
FFMPEG_PATH = os.getenv("FFMPEG_PATH", r"C:\ffmpeg\bin\ffmpeg.exe")

# FFmpeg encoding preset
# Options: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
# Faster = quicker encoding but larger file size
# Slower = longer encoding but better compression
FFMPEG_PRESET = "medium"

# Constant Rate Factor (CRF) for video quality (0-51)
# Lower = better quality but larger file
# 18-28 is usually good range, 23 is default
FFMPEG_CRF = 23


# ============================================================================
# YOUTUBE UPLOAD SETTINGS
# ============================================================================

# Default privacy status for uploaded videos
# Options: "private", "unlisted", "public"
# Recommended: Start with "private" for testing
YOUTUBE_PRIVACY_STATUS = "private"

# Video category ID
# Common categories:
#   1: Film & Animation
#   10: Music
#   15: Pets & Animals
#   17: Sports
#   19: Travel & Events
#   20: Gaming
#   22: People & Blogs
#   23: Comedy
#   24: Entertainment
#   25: News & Politics
#   26: Howto & Style
#   27: Education
#   28: Science & Technology
YOUTUBE_CATEGORY_ID = "27"  # Education

# Whether video is made for kids (COPPA compliance)
# True: Video is made for kids (disables comments, notifications, personalized ads)
# False: Video is not made for kids
YOUTUBE_MADE_FOR_KIDS = False

# Default tags to add to all videos
YOUTUBE_DEFAULT_TAGS = [
    "educational",
    "informative",
    "automated content",
    "AI generated",
]

# Maximum number of tags (YouTube limit is 500 characters total)
YOUTUBE_MAX_TAGS = 15


# ============================================================================
# TEXT-TO-SPEECH SETTINGS
# ============================================================================

# Whether to use ElevenLabs for TTS (requires API key)
# If False or no API key, will use free gTTS
USE_ELEVENLABS = bool(ELEVENLABS_API_KEY and ELEVENLABS_API_KEY != "")

# ElevenLabs voice ID (if using ElevenLabs)
# Get voice IDs from: https://elevenlabs.io/voice-library
# Default voice: "21m00Tcm4TlvDq8ikWAM" (Rachel)
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# ElevenLabs model
ELEVENLABS_MODEL = "eleven_monolingual_v1"

# gTTS (Google Text-to-Speech) settings
GTTS_LANGUAGE = "en"  # Language code
GTTS_SLOW = False     # Speak slowly


# ============================================================================
# CONTENT TOPIC SETTINGS
# ============================================================================

# List of topic categories to choose from
# AI will select and generate content based on these themes
TOPIC_CATEGORIES = [
    "interesting facts",
    "life hacks",
    "technology trends",
    "science discoveries",
    "history mysteries",
    "productivity tips",
    "health and wellness",
    "psychology insights",
    "space exploration",
    "animal facts",
    "cooking tips",
    "travel destinations",
]

# Days to look back when avoiding duplicate topics
TOPIC_HISTORY_DAYS = 30

# Topic history file location
TOPIC_HISTORY_FILE = str(LOGS_DIR / "topic_history.json")


# ============================================================================
# IMAGE/ASSET GENERATION SETTINGS
# ============================================================================

# Number of images to download per scene
IMAGES_PER_SCENE = 1

# Image orientation preference for searches
IMAGE_ORIENTATION = "landscape"  # landscape, portrait, square

# Image download timeout in seconds
IMAGE_DOWNLOAD_TIMEOUT = 30

# Whether to use placeholder images if download fails
USE_PLACEHOLDER_ON_FAILURE = True


# ============================================================================
# THUMBNAIL GENERATION SETTINGS
# ============================================================================

# Thumbnail dimensions (YouTube recommended: 1280x720)
THUMBNAIL_WIDTH = 1280
THUMBNAIL_HEIGHT = 720

# Thumbnail quality (1-100)
THUMBNAIL_QUALITY = 95

# Thumbnail text font size
THUMBNAIL_FONT_SIZE = 80

# Thumbnail text max width (characters before wrapping)
THUMBNAIL_TEXT_MAX_WIDTH = 20


# ============================================================================
# LOGGING SETTINGS
# ============================================================================

# Log file path (will include date in filename)
LOG_FILE_PATH = str(LOGS_DIR / "youtube_automation_{date}.log")

# Logging level
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# Maximum log file size in bytes (10 MB)
LOG_MAX_SIZE = 10 * 1024 * 1024

# Number of backup log files to keep
LOG_BACKUP_COUNT = 5

# Whether to log to console in addition to file
LOG_TO_CONSOLE = True

# Whether to use colored console logging
LOG_USE_COLORS = True


# ============================================================================
# SCHEDULING SETTINGS
# ============================================================================

# Maximum number of videos to generate per day
MAX_VIDEOS_PER_DAY = 1

# Preferred time to run (24-hour format, used for reference only)
# Actual scheduling is done via Windows Task Scheduler
PREFERRED_RUN_TIME = "02:00"


# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """
    Validate configuration settings and check for common issues.

    Raises:
        ValueError: If critical configuration is missing or invalid
        FileNotFoundError: If required files/directories don't exist
    """
    errors = []

    # Check API keys
    if OPENAI_API_KEY == "YOUR_OPENAI_API_KEY_HERE" or not OPENAI_API_KEY:
        errors.append("OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")

    # Check FFmpeg
    if not Path(FFMPEG_PATH).exists():
        errors.append(f"FFmpeg not found at: {FFMPEG_PATH}")

    # Check YouTube credentials file
    if not Path(YOUTUBE_CLIENT_SECRETS).exists():
        errors.append(f"YouTube client secrets not found at: {YOUTUBE_CLIENT_SECRETS}")

    # Check video duration settings
    if VIDEO_MIN_DURATION >= VIDEO_MAX_DURATION:
        errors.append("VIDEO_MIN_DURATION must be less than VIDEO_MAX_DURATION")

    if VIDEO_TARGET_DURATION < VIDEO_MIN_DURATION or VIDEO_TARGET_DURATION > VIDEO_MAX_DURATION:
        errors.append("VIDEO_TARGET_DURATION must be between VIDEO_MIN_DURATION and VIDEO_MAX_DURATION")

    # Ensure directories exist
    for directory in [ASSETS_DIR, OUTPUT_DIR, LOGS_DIR, IMAGES_DIR, MUSIC_DIR,
                      VIDEOS_DIR, THUMBNAILS_DIR, PROMPTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    if errors:
        raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    return True


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_video_resolution_tuple():
    """
    Get video resolution as tuple of integers (width, height).

    Returns:
        tuple: (width, height)
    """
    width, height = VIDEO_RESOLUTION.split('x')
    return (int(width), int(height))


def get_ffmpeg_command_base():
    """
    Get base FFmpeg command with common options.

    Returns:
        list: Base FFmpeg command arguments
    """
    return [
        FFMPEG_PATH,
        '-y',  # Overwrite output files
        '-loglevel', 'error',  # Only show errors
    ]


# ============================================================================
# CONFIGURATION SUMMARY
# ============================================================================

def print_config_summary():
    """Print a summary of current configuration (for debugging)."""
    print("=" * 80)
    print("YouTube Automation Configuration Summary")
    print("=" * 80)
    print(f"AI Model: {AI_MODEL}")
    print(f"Video Duration: {VIDEO_MIN_DURATION}-{VIDEO_MAX_DURATION}s (target: {VIDEO_TARGET_DURATION}s)")
    print(f"Video Resolution: {VIDEO_RESOLUTION} @ {VIDEO_FPS} FPS")
    print(f"FFmpeg Path: {FFMPEG_PATH}")
    print(f"YouTube Privacy: {YOUTUBE_PRIVACY_STATUS}")
    print(f"Made for Kids: {YOUTUBE_MADE_FOR_KIDS}")
    print(f"TTS Provider: {'ElevenLabs' if USE_ELEVENLABS else 'gTTS (Google)'}")
    print(f"OpenAI Key Set: {'Yes' if OPENAI_API_KEY and OPENAI_API_KEY != 'YOUR_OPENAI_API_KEY_HERE' else 'No'}")
    print(f"Pexels Key Set: {'Yes' if PEXELS_API_KEY else 'No'}")
    print(f"Log Level: {LOG_LEVEL}")
    print(f"Max Videos/Day: {MAX_VIDEOS_PER_DAY}")
    print("=" * 80)


if __name__ == "__main__":
    """Run validation and print config when executed directly."""
    try:
        validate_config()
        print("✓ Configuration validation passed!")
        print()
        print_config_summary()
    except (ValueError, FileNotFoundError) as e:
        print("✗ Configuration validation failed!")
        print()
        print(str(e))
        exit(1)
