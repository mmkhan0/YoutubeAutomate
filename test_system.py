"""
Test script for YouTube Automation System
Tests each module independently to verify functionality
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def test_imports():
    """Test if all required modules can be imported"""
    print_header("Testing Module Imports")

    modules = [
        ("config", "Configuration module"),
        ("src.kids_topic_selector", "Topic Selector"),
        ("src.kids_script_generator", "Script Generator"),
        ("src.kids_image_generator", "Image Generator"),
        ("src.kids_voiceover_generator", "Voiceover Generator"),
        ("src.kids_video_creator", "Video Creator"),
        ("src.youtube_metadata_generator", "Metadata Generator"),
        ("src.youtube_uploader", "YouTube Uploader"),
    ]

    results = {"passed": 0, "failed": 0}

    for module_name, description in modules:
        try:
            __import__(module_name)
            print_success(f"{description}: Imported successfully")
            results["passed"] += 1
        except ImportError as e:
            print_error(f"{description}: Import failed - {str(e)}")
            results["failed"] += 1
        except Exception as e:
            print_error(f"{description}: Unexpected error - {str(e)}")
            results["failed"] += 1

    return results

def test_dependencies():
    """Test if all required packages are installed"""
    print_header("Testing Package Dependencies")

    packages = [
        ("openai", "OpenAI API"),
        ("google.oauth2", "Google Auth"),
        ("googleapiclient", "Google API Client"),
        ("elevenlabs", "ElevenLabs TTS"),
        ("gtts", "Google TTS (fallback)"),
        ("PIL", "Pillow (Image Processing)"),
        ("requests", "Requests (HTTP)"),
        ("dotenv", "Python-dotenv (Environment Variables)"),
    ]

    results = {"passed": 0, "failed": 0}

    for package, description in packages:
        try:
            __import__(package)
            print_success(f"{description}: Installed")
            results["passed"] += 1
        except ImportError:
            print_error(f"{description}: Not installed")
            results["failed"] += 1

    return results

def test_configuration():
    """Test configuration loading"""
    print_header("Testing Configuration")

    results = {"passed": 0, "failed": 0, "warnings": 0}

    try:
        import config
        print_success("Configuration module loaded")
        results["passed"] += 1

        # Check critical config values
        checks = [
            ("OPENAI_API_KEY", config.OPENAI_API_KEY),
            ("ELEVENLABS_API_KEY", config.ELEVENLABS_API_KEY),
            ("FFMPEG_PATH", config.FFMPEG_PATH),
            ("OUTPUT_DIR", config.OUTPUT_DIR),
            ("LOGS_DIR", config.LOGS_DIR),
        ]

        for name, value in checks:
            if value and "placeholder" not in str(value).lower():
                if name.endswith("_DIR") or name.endswith("_PATH"):
                    if os.path.exists(value) if name.endswith("_DIR") else True:
                        print_success(f"{name}: Configured")
                        results["passed"] += 1
                    else:
                        print_warning(f"{name}: Path does not exist - {value}")
                        results["warnings"] += 1
                else:
                    print_success(f"{name}: Configured")
                    results["passed"] += 1
            else:
                print_warning(f"{name}: Not configured or contains placeholder")
                results["warnings"] += 1

        # Test validation function
        try:
            is_valid, message = config.validate_config()
            if is_valid:
                print_success(f"Configuration validation: {message}")
                results["passed"] += 1
            else:
                print_warning(f"Configuration validation: {message}")
                results["warnings"] += 1
        except Exception as e:
            print_error(f"Configuration validation failed: {str(e)}")
            results["failed"] += 1

    except Exception as e:
        print_error(f"Failed to load configuration: {str(e)}")
        results["failed"] += 1

    return results

def test_directory_structure():
    """Test if required directories exist"""
    print_header("Testing Directory Structure")

    results = {"passed": 0, "failed": 0}

    required_dirs = [
        "src",
        "config",
        "assets",
        "assets/music",
        "output",
        "output/videos",
        "output/images",
        "output/audio",
        "logs",
        "prompts",
    ]

    for dir_path in required_dirs:
        full_path = os.path.join(os.getcwd(), dir_path)
        if os.path.exists(full_path):
            print_success(f"Directory exists: {dir_path}")
            results["passed"] += 1
        else:
            print_warning(f"Directory missing: {dir_path} (will be created automatically)")
            results["failed"] += 1

    return results

def test_ffmpeg():
    """Test FFmpeg installation"""
    print_header("Testing FFmpeg")

    results = {"passed": 0, "failed": 0}

    import subprocess
    import config

    # Try configured FFmpeg path
    try:
        if config.FFMPEG_PATH and os.path.exists(config.FFMPEG_PATH):
            result = subprocess.run(
                [config.FFMPEG_PATH, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print_success(f"FFmpeg found at configured path: {version_line}")
                results["passed"] += 1
                return results
        else:
            print_warning(f"Configured FFmpeg path does not exist: {config.FFMPEG_PATH}")
    except Exception as e:
        print_warning(f"FFmpeg test at configured path failed: {str(e)}")

    # Try system FFmpeg
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print_success(f"FFmpeg found in system PATH: {version_line}")
            results["passed"] += 1
            return results
    except FileNotFoundError:
        print_error("FFmpeg not found in system PATH")
    except Exception as e:
        print_error(f"FFmpeg test failed: {str(e)}")

    results["failed"] += 1
    print_error("FFmpeg is not installed or not accessible")
    print_info("Download FFmpeg from: https://ffmpeg.org/download.html")

    return results

def test_api_connections():
    """Test API connections (without making actual calls)"""
    print_header("Testing API Configuration")

    results = {"passed": 0, "failed": 0, "warnings": 0}

    import config

    # OpenAI
    if config.OPENAI_API_KEY and "placeholder" not in config.OPENAI_API_KEY.lower():
        if config.OPENAI_API_KEY.startswith("sk-"):
            print_success("OpenAI API key format is valid")
            results["passed"] += 1
        else:
            print_warning("OpenAI API key format may be invalid (should start with 'sk-')")
            results["warnings"] += 1
    else:
        print_warning("OpenAI API key not configured")
        results["warnings"] += 1

    # ElevenLabs
    if config.ELEVENLABS_API_KEY and "placeholder" not in config.ELEVENLABS_API_KEY.lower():
        print_success("ElevenLabs API key is configured")
        results["passed"] += 1
    else:
        print_info("ElevenLabs API key not configured (will use gTTS fallback)")

    # YouTube OAuth
    client_secrets = Path("config/client_secrets.json")
    if client_secrets.exists():
        print_success("YouTube client_secrets.json file exists")
        results["passed"] += 1
    else:
        print_warning("YouTube client_secrets.json not found")
        print_info("Required for YouTube uploads. See SETUP.md for instructions.")
        results["warnings"] += 1

    return results

def test_module_instantiation():
    """Test if modules can be instantiated"""
    print_header("Testing Module Instantiation")

    results = {"passed": 0, "failed": 0}

    # Test Topic Selector
    try:
        from src.kids_topic_selector import KidsTopicSelector
        selector = KidsTopicSelector()
        print_success("Topic Selector: Instantiated successfully")
        results["passed"] += 1
    except Exception as e:
        print_error(f"Topic Selector: Failed to instantiate - {str(e)}")
        results["failed"] += 1

    # Test Script Generator
    try:
        from src.kids_script_generator import KidsScriptGenerator
        generator = KidsScriptGenerator()
        print_success("Script Generator: Instantiated successfully")
        results["passed"] += 1
    except Exception as e:
        print_error(f"Script Generator: Failed to instantiate - {str(e)}")
        results["failed"] += 1

    # Test Image Generator
    try:
        from src.kids_image_generator import KidsImageGenerator
        img_gen = KidsImageGenerator()
        print_success("Image Generator: Instantiated successfully")
        results["passed"] += 1
    except Exception as e:
        print_error(f"Image Generator: Failed to instantiate - {str(e)}")
        results["failed"] += 1

    # Test Voiceover Generator
    try:
        from src.kids_voiceover_generator import KidsVoiceoverGenerator
        vo_gen = KidsVoiceoverGenerator()
        print_success("Voiceover Generator: Instantiated successfully")
        results["passed"] += 1
    except Exception as e:
        print_error(f"Voiceover Generator: Failed to instantiate - {str(e)}")
        results["failed"] += 1

    # Test Video Creator
    try:
        from src.kids_video_creator import KidsVideoCreator
        video_creator = KidsVideoCreator()
        print_success("Video Creator: Instantiated successfully")
        results["passed"] += 1
    except Exception as e:
        print_error(f"Video Creator: Failed to instantiate - {str(e)}")
        results["failed"] += 1

    # Test Metadata Generator
    try:
        from src.youtube_metadata_generator import YouTubeMetadataGenerator
        meta_gen = YouTubeMetadataGenerator()
        print_success("Metadata Generator: Instantiated successfully")
        results["passed"] += 1
    except Exception as e:
        print_error(f"Metadata Generator: Failed to instantiate - {str(e)}")
        results["failed"] += 1

    # Test YouTube Uploader
    try:
        from src.youtube_uploader import YouTubeUploader
        uploader = YouTubeUploader()
        print_success("YouTube Uploader: Instantiated successfully")
        results["passed"] += 1
    except Exception as e:
        print_error(f"YouTube Uploader: Failed to instantiate - {str(e)}")
        results["failed"] += 1

    return results

def print_summary(all_results):
    """Print test summary"""
    print_header("Test Summary")

    total_passed = sum(r.get("passed", 0) for r in all_results.values())
    total_failed = sum(r.get("failed", 0) for r in all_results.values())
    total_warnings = sum(r.get("warnings", 0) for r in all_results.values())
    total_tests = total_passed + total_failed + total_warnings

    print(f"Total Tests: {total_tests}")
    print_success(f"Passed: {total_passed}")
    if total_warnings > 0:
        print_warning(f"Warnings: {total_warnings}")
    if total_failed > 0:
        print_error(f"Failed: {total_failed}")

    print(f"\n{Colors.BOLD}Test Categories:{Colors.END}")
    for category, results in all_results.items():
        passed = results.get("passed", 0)
        failed = results.get("failed", 0)
        warnings = results.get("warnings", 0)
        total = passed + failed + warnings

        status = Colors.GREEN if failed == 0 else Colors.RED
        print(f"  {status}{category}: {passed}/{total} passed{Colors.END}")

    # Overall status
    print()
    if total_failed == 0 and total_warnings == 0:
        print_success("All tests passed! Your automation system is ready to use.")
        print_info("Next step: Configure your API keys in .env file and run: python run_automation.py")
    elif total_failed == 0:
        print_warning(f"All critical tests passed with {total_warnings} warnings.")
        print_info("Review warnings above and configure missing components.")
    else:
        print_error(f"Some tests failed. Please fix the issues above before running the automation.")

    print()

def main():
    """Run all tests"""
    print_header("YouTube Automation System - Test Suite")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Working directory: {os.getcwd()}")
    print_info(f"Python version: {sys.version.split()[0]}")

    all_results = {}

    # Run all tests
    all_results["Dependencies"] = test_dependencies()
    all_results["Imports"] = test_imports()
    all_results["Configuration"] = test_configuration()
    all_results["Directory Structure"] = test_directory_structure()
    all_results["FFmpeg"] = test_ffmpeg()
    all_results["API Configuration"] = test_api_connections()
    all_results["Module Instantiation"] = test_module_instantiation()

    # Print summary
    print_summary(all_results)

    # Return exit code
    total_failed = sum(r.get("failed", 0) for r in all_results.values())
    return 0 if total_failed == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
