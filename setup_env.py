"""
Environment Configuration Setup Tool
Generates .env file with required API keys and settings
"""

import os
import shutil
import getpass
from pathlib import Path


class EnvSetup:
    """Interactive .env file generator"""

    def __init__(self):
        self.env_path = Path(".env")
        self.config = {}

    def print_header(self):
        """Print welcome header"""
        print("\n" + "=" * 70)
        print("🚀 YOUTUBE AUTOMATION - ENVIRONMENT SETUP")
        print("=" * 70)
        print("\nThis tool will help you configure your .env file with API keys.")
        print("Press Enter to skip optional fields.\n")

    def print_section(self, title: str):
        """Print section header"""
        print("\n" + "-" * 70)
        print(f"📝 {title}")
        print("-" * 70)

    def get_input(self,
                  prompt: str,
                  default: str = "",
                  required: bool = False,
                  secure: bool = False) -> str:
        """Get user input with validation"""
        while True:
            if secure:
                # For passwords/keys, show masked input
                value = getpass.getpass(f"{prompt}: ")
            else:
                if default:
                    value = input(f"{prompt} [{default}]: ").strip()
                else:
                    value = input(f"{prompt}: ").strip()

            # Use default if provided and input is empty
            if not value and default:
                value = default

            # Check if required field is empty
            if required and not value:
                print("❌ This field is required. Please enter a value.")
                continue

            return value

    def setup_gemini(self):
        """Setup Gemini API (FREE option)"""
        self.print_section("Google Gemini API (FREE - RECOMMENDED)")
        print("✅ 100% FREE tier: 60 requests/min, 1500 requests/day")
        print("📝 Get your FREE API key from: https://makersuite.google.com/app/apikey")
        print()

        api_key = self.get_input(
            "Enter your Gemini API key",
            required=False
        )
        self.config['GEMINI_API_KEY'] = api_key

    def setup_openai(self):
        """Setup OpenAI API (PAID option)"""
        self.print_section("OpenAI API (PAID - OPTIONAL)")
        print("💰 Cost: ~$0.40 per video (DALL-E 3 + GPT-4)")
        print("⚠️  Only needed if you want paid system instead of FREE Gemini")
        print("📝 Get API key from: https://platform.openai.com/api-keys")
        print()

        api_key = self.get_input(
            "Enter your OpenAI API key (or press Enter to skip)",
            required=False
        )
        self.config['OPENAI_API_KEY'] = api_key

    def setup_elevenlabs(self):
        """Setup ElevenLabs API (PAID TTS option)"""
        self.print_section("ElevenLabs API (PAID - OPTIONAL)")
        print("🎙️  Premium voice quality text-to-speech")
        print("💰 FREE tier: 10,000 characters/month")
        print("💰 Paid: $5/month for 30,000 characters")
        print("📝 Get API key from: https://elevenlabs.io/app/settings")
        print("⚠️  Leave empty to use FREE gTTS instead")
        print()

        api_key = self.get_input(
            "Enter your ElevenLabs API key (or press Enter to skip)",
            required=False
        )
        self.config['ELEVENLABS_API_KEY'] = api_key

        if api_key:
            voice_id = self.get_input(
                "Enter voice ID",
                default="21m00Tcm4TlvDq8ikWAM"  # Rachel voice
            )
            self.config['ELEVENLABS_VOICE_ID'] = voice_id
        else:
            self.config['ELEVENLABS_VOICE_ID'] = ""

    def setup_stable_diffusion(self):
        """Setup Stable Diffusion (FREE image generation)"""
        self.print_section("Stable Diffusion (FREE - LOCAL)")
        print("🎨 100% FREE image generation on your computer")
        print("📝 All models are FREE from Hugging Face")
        print()

        print("Available models:")
        print("  1. runwayml/stable-diffusion-v1-5 (Default, fast)")
        print("  2. prompthero/openjourney-v4 (Midjourney-style)")
        print("  3. Linaqruf/anything-v3.0 (Anime style)")
        print("  4. stabilityai/stable-diffusion-xl-base-1.0 (High quality)")
        print()

        model = self.get_input(
            "Enter model choice (1-4)",
            default="1"
        )

        models = {
            "1": "runwayml/stable-diffusion-v1-5",
            "2": "prompthero/openjourney-v4",
            "3": "Linaqruf/anything-v3.0",
            "4": "stabilityai/stable-diffusion-xl-base-1.0"
        }

        self.config['SD_MODEL_ID'] = models.get(model, models["1"])

        hf_token = self.get_input(
            "Enter Hugging Face token (optional, for gated models)",
            required=False
        )
        self.config['HUGGINGFACE_API_KEY'] = hf_token

    def setup_tts(self):
        """Setup TTS engine"""
        self.print_section("Text-to-Speech Engine (FREE)")
        print("🎙️  Choose your FREE voiceover engine:")
        print("  1. auto - Automatically selects best available (RECOMMENDED)")
        print("  2. piper - High quality, fast (must install separately)")
        print("  3. coqui - Very natural voices (pip install TTS)")
        print("  4. gtts - Simple, reliable (always available)")
        print()

        choice = self.get_input(
            "Enter TTS engine choice (1-4)",
            default="1"
        )

        engines = {"1": "auto", "2": "piper", "3": "coqui", "4": "gtts"}
        self.config['TTS_ENGINE'] = engines.get(choice, "auto")

        if choice == "2":
            piper_path = self.get_input(
                "Enter Piper executable path (or press Enter to skip)",
                required=False
            )
            self.config['PIPER_PATH'] = piper_path
        else:
            self.config['PIPER_PATH'] = ""

    def setup_ffmpeg(self):
        """Setup FFmpeg path"""
        self.print_section("FFmpeg Configuration")
        print("🎬 FFmpeg is required for video generation")
        print()

        # Try to detect FFmpeg
        username = os.getenv('USERNAME', 'User')
        winget_path = (
            f"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\WinGet\\"
            f"Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\"
            f"ffmpeg-8.0.1-full_build\\bin\\ffmpeg.exe"
        )
        default_paths = [
            "ffmpeg",  # If in PATH
            "C:\\ProgramData\\chocolatey\\bin\\ffmpeg.exe",
            winget_path
        ]

        detected = None
        for path in default_paths:
            if os.path.exists(path) or path == "ffmpeg":
                detected = path
                break

        if detected:
            print(f"✅ Detected FFmpeg at: {detected}")
            use_detected = self.get_input(
                "Use this path? (y/n)",
                default="y"
            ).lower()

            if use_detected == "y":
                self.config['FFMPEG_PATH'] = detected
                return

        ffmpeg_path = self.get_input(
            "Enter FFmpeg path",
            default="ffmpeg"
        )
        self.config['FFMPEG_PATH'] = ffmpeg_path

    def setup_video_settings(self):
        """Setup video generation settings"""
        self.print_section("Video Generation Settings")
        print("🎥 Configure video output parameters")
        print()

        self.config['VIDEO_DURATION'] = self.get_input(
            "Video duration in seconds",
            default="240"
        )

        self.config['VIDEO_FPS'] = self.get_input(
            "Frame rate (FPS)",
            default="30"
        )

        self.config['VIDEO_WIDTH'] = self.get_input(
            "Video width (pixels)",
            default="1920"
        )

        self.config['VIDEO_HEIGHT'] = self.get_input(
            "Video height (pixels)",
            default="1080"
        )

        self.config['VIDEO_CRF'] = self.get_input(
            "Video quality (CRF: 18-23 = high quality)",
            default="20"
        )

    def setup_youtube(self):
        """Setup YouTube settings"""
        self.print_section("YouTube Upload Settings")
        print("📺 Configure default YouTube upload settings")
        print()

        privacy = self.get_input(
            "Privacy status (public/private/unlisted)",
            default="public"
        )
        self.config['PRIVACY_STATUS'] = privacy

        made_for_kids = self.get_input(
            "Made for kids? (true/false)",
            default="true"
        ).lower()
        self.config['MADE_FOR_KIDS'] = made_for_kids

        print("\n📚 Playlist IDs (optional - press Enter to skip)")
        print("   Run 'python create_playlists.py' to create playlists and get IDs")

        self.config['TECH_PLAYLIST_ID'] = self.get_input(
            "Tech playlist ID",
            required=False
        )

        self.config['KIDS_PLAYLIST_ID'] = self.get_input(
            "Kids playlist ID",
            required=False
        )

        self.config['SCIENCE_PLAYLIST_ID'] = self.get_input(
            "Science playlist ID",
            required=False
        )

    def generate_env_file(self):
        """Generate .env file from config"""
        lines = [
            "# ============================================================================",
            "# YOUTUBE AUTOMATION CONFIGURATION",
            "# Generated by setup_env.py",
            "# ============================================================================",
            "",
            "# ----------------------------------------------------------------------------",
            "# Google Gemini API (FREE)",
            "# ----------------------------------------------------------------------------",
            "# Get FREE API key from: https://makersuite.google.com/app/apikey",
            f"GEMINI_API_KEY={self.config.get('GEMINI_API_KEY', '')}",
            "",
            "# ----------------------------------------------------------------------------",
            "# OpenAI API (PAID - OPTIONAL)",
            "# ----------------------------------------------------------------------------",
            "# Only needed if you want to use paid system instead of FREE Gemini",
            f"OPENAI_API_KEY={self.config.get('OPENAI_API_KEY', '')}",
            "",
            "# ----------------------------------------------------------------------------",
            "# Stable Diffusion Configuration (FREE)",
            "# ----------------------------------------------------------------------------",
            f"SD_MODEL_ID={self.config.get('SD_MODEL_ID', 'runwayml/stable-diffusion-v1-5')}",
            f"HUGGINGFACE_API_KEY={self.config.get('HUGGINGFACE_API_KEY', '')}",
            "",
            "# ----------------------------------------------------------------------------",
            "# Text-to-Speech Configuration (FREE)",
            "# ----------------------------------------------------------------------------",
            f"TTS_ENGINE={self.config.get('TTS_ENGINE', 'auto')}",
            f"PIPER_PATH={self.config.get('PIPER_PATH', '')}",
            "",
            "# ----------------------------------------------------------------------------",
            "# ElevenLabs API (PAID - OPTIONAL)",
            "# ----------------------------------------------------------------------------",
            f"ELEVENLABS_API_KEY={self.config.get('ELEVENLABS_API_KEY', '')}",
            f"ELEVENLABS_VOICE_ID={self.config.get('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')}",
            "",
            "# ----------------------------------------------------------------------------",
            "# FFmpeg Configuration",
            "# ----------------------------------------------------------------------------",
            f"FFMPEG_PATH={self.config.get('FFMPEG_PATH', 'ffmpeg')}",
            "",
            "# ----------------------------------------------------------------------------",
            "# Video Generation Settings",
            "# ----------------------------------------------------------------------------",
            f"VIDEO_DURATION={self.config.get('VIDEO_DURATION', '240')}",
            f"VIDEO_FPS={self.config.get('VIDEO_FPS', '30')}",
            f"VIDEO_WIDTH={self.config.get('VIDEO_WIDTH', '1920')}",
            f"VIDEO_HEIGHT={self.config.get('VIDEO_HEIGHT', '1080')}",
            f"VIDEO_CRF={self.config.get('VIDEO_CRF', '20')}",
            "",
            "# ----------------------------------------------------------------------------",
            "# YouTube Upload Settings",
            "# ----------------------------------------------------------------------------",
            f"PRIVACY_STATUS={self.config.get('PRIVACY_STATUS', 'public')}",
            f"MADE_FOR_KIDS={self.config.get('MADE_FOR_KIDS', 'true')}",
            "",
            "# Playlist IDs (optional)",
            f"TECH_PLAYLIST_ID={self.config.get('TECH_PLAYLIST_ID', '')}",
            f"KIDS_PLAYLIST_ID={self.config.get('KIDS_PLAYLIST_ID', '')}",
            f"SCIENCE_PLAYLIST_ID={self.config.get('SCIENCE_PLAYLIST_ID', '')}",
            ""
        ]

        with open(self.env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def run(self):
        """Run interactive setup"""
        self.print_header()

        # Check if .env already exists
        if self.env_path.exists():
            print("⚠️  Warning: .env file already exists!")
            overwrite = self.get_input(
                "Do you want to overwrite it? (y/n)",
                default="n"
            ).lower()

            if overwrite != "y":
                print("\n❌ Setup cancelled. Your existing .env file is unchanged.")
                return

            # Backup existing .env
            backup_path = Path(".env.backup")
            shutil.copy2(self.env_path, backup_path)
            print(f"✅ Backed up existing .env to {backup_path}")

        # Run setup sections
        try:
            self.setup_gemini()
            self.setup_openai()
            self.setup_elevenlabs()
            self.setup_stable_diffusion()
            self.setup_tts()
            self.setup_ffmpeg()
            self.setup_video_settings()
            self.setup_youtube()

            # Generate .env file
            self.print_section("Summary")
            print("\n📝 Generating .env file...")
            self.generate_env_file()

            print("\n" + "=" * 70)
            print("✅ SUCCESS! .env file created successfully!")
            print("=" * 70)
            print(f"\n📁 Location: {self.env_path.absolute()}")
            print("\n🚀 Next steps:")
            print("   1. Review your .env file")
            print("   2. Run: python run_automation.py --category kids --language en")
            print("   3. Check the logs/ folder for automation progress")
            print("\n💡 Tip: You can edit .env file manually anytime to change settings")
            print("=" * 70 + "\n")

        except KeyboardInterrupt:
            print("\n\n❌ Setup cancelled by user.")
        except (OSError, IOError, ValueError) as e:
            # Catch file I/O and validation errors
            print(f"\n\n❌ Error during setup: {e}")


def main():
    """Main entry point"""
    setup = EnvSetup()
    setup.run()


if __name__ == "__main__":
    main()
