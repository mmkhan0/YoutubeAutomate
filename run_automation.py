"""
YouTube Kids Video Automation - Main Orchestration Script

This script orchestrates the complete automated video generation and upload pipeline:
1. Select kid-friendly topic
2. Generate structured script
3. Generate AI images
4. Generate voiceover
5. Create video with FFmpeg
6. Generate YouTube metadata
7. Upload to YouTube

Designed to run via Windows Task Scheduler.
"""

import sys
import os
import logging
import shutil
import time
import traceback
import functools
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List

# Fix Windows console encoding for emoji/unicode in log messages
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import all modules
from src.kids_topic_selector import KidsTopicSelector
from src.early_learning_selector import EarlyLearningTopicSelector
from src.kids_script_generator import KidsScriptGenerator
from src.kids_image_generator import KidsImageGenerator
from src.kids_voiceover_generator import KidsVoiceoverGenerator
from src.kids_video_creator import KidsVideoCreator
from src.youtube_metadata_generator import YouTubeMetadataGenerator
from src.seo_optimizer import YouTubeSEOOptimizer, optimize_youtube_seo
from src.youtube_uploader import YouTubeUploader
from src.background_music_mixer import BackgroundMusicMixer
from src.playlist_manager import PlaylistManager


# ============================================================================
# RETRY DECORATOR AND UTILITY FUNCTIONS
# ============================================================================

def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    logger: Optional[logging.Logger] = None
):
    """
    Decorator to retry a function on failure with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
        logger: Logger for retry messages
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _logger = logger or logging.getLogger(func.__module__)
            last_exception = None

            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_retries:
                        wait_time = delay * (backoff ** (attempt - 1))
                        _logger.warning(
                            f"⚠️  {func.__name__} failed (attempt {attempt}/{max_retries}): {str(e)[:100]}"
                        )
                        _logger.info(f"🔄 Retrying in {wait_time:.1f} seconds...")
                        time.sleep(wait_time)
                    else:
                        _logger.error(
                            f"❌ {func.__name__} failed after {max_retries} attempts"
                        )
                        _logger.error(f"Final error: {str(e)}")
                        if _logger.level <= logging.DEBUG:
                            _logger.debug(f"Stack trace: {traceback.format_exc()}")

            raise last_exception
        return wrapper
    return decorator


class YouTubeAutomationOrchestrator:
    """
    Main orchestrator for automated YouTube video generation and upload.

    Manages the complete pipeline from topic selection to YouTube upload,
    with comprehensive logging and error handling.
    """

    def __init__(self, config_file: Optional[str] = None, test_mode: bool = False, use_videos: bool = False, category: str = 'auto', language: str = 'en'):
        """
        Initialize the orchestrator.

        Args:
            config_file: Optional path to configuration file
            test_mode: If True, use pre-written test data instead of API calls
            use_videos: If True, use real video clips from Pexels (requires PEXELS_API_KEY)
            category: Video category ('tech', 'kids', 'science', or 'auto')
            language: Video language code (e.g., 'en', 'hi', 'es')
        """
        self.test_mode = test_mode
        self.use_videos = use_videos
        self.category = category
        self.language = language
        self.project_root = Path(__file__).parent
        self.config = self._load_config(config_file)
        self.logger = None
        self.session_data = {
            'start_time': datetime.now(),
            'topic': None,
            'script': None,
            'images': [],
            'videos': [],  # For real video clips
            'voiceover_path': None,
            'video_path': None,
            'metadata': None,
            'upload_result': None
        }

    def _load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from environment or config file.

        Args:
            config_file: Optional config file path

        Returns:
            dict: Configuration dictionary
        """
        # Load automation config if exists
        automation_config = {}
        automation_config_path = self.project_root / 'automation_config.json'
        if automation_config_path.exists():
            try:
                import json
                with open(automation_config_path, 'r', encoding='utf-8') as f:
                    automation_config = json.load(f)
                # Logger not initialized yet during config load
            except Exception as e:
                print(f"Warning: Could not load automation_config.json: {e}")

        # Load from environment variables
        config = {
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'elevenlabs_api_key': os.getenv('ELEVENLABS_API_KEY'),
            'pexels_api_key': os.getenv('PEXELS_API_KEY'),
            'ffmpeg_path': os.getenv('FFMPEG_PATH', 'ffmpeg'),
            'client_secrets_file': str(self.project_root / 'config' / 'client_secrets.json'),
            'target_duration': automation_config.get('video', {}).get('target_duration_seconds', int(os.getenv('VIDEO_DURATION', '240'))),
            'privacy_status': automation_config.get('youtube', {}).get('privacy_status', os.getenv('PRIVACY_STATUS', 'private')),
            'made_for_kids': automation_config.get('youtube', {}).get('made_for_kids', os.getenv('MADE_FOR_KIDS', 'true').lower() == 'true'),
            'coppa_compliant': automation_config.get('youtube', {}).get('coppa_compliant', True),
            'no_manual_confirmation': automation_config.get('youtube', {}).get('no_manual_confirmation', True),
            'use_early_learning_only': automation_config.get('content', {}).get('mode') == 'early_learning_only',
            'tech_playlist_id': os.getenv('TECH_PLAYLIST_ID', ''),
            'kids_playlist_id': os.getenv('KIDS_PLAYLIST_ID', ''),
            'science_playlist_id': os.getenv('SCIENCE_PLAYLIST_ID', ''),
            'automation_config': automation_config  # Store full config
        }

        # Validate critical config
        if not config['openai_api_key']:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        return config

    def _setup_logging(self) -> None:
        """Set up logging to file and console."""
        logs_dir = self.project_root / 'logs'
        logs_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = logs_dir / f'automation_{timestamp}.log'

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger('YouTubeAutomation')
        self.logger.info("=" * 80)
        self.logger.info("YouTube Kids Video Automation Started")
        self.logger.info(f"Session: {timestamp}")
        self.logger.info(f"Log file: {log_file}")
        self.logger.info("=" * 80)

    def _cleanup_previous_data(self, keep_last_n_videos: int = 3) -> None:
        """
        Clean up previous video generation data to save disk space.

        Deletes:
        - All audio files (old voiceovers)
        - All images (old DALL-E generations)
        - All temporary video clips
        - Old videos (keeps only the last N)

        Args:
            keep_last_n_videos: Number of most recent videos to keep (default: 3)
        """
        try:
            self.logger.info("-" * 80)
            self.logger.info("CLEANUP: Removing Previous Video Data")
            self.logger.info("-" * 80)

            output_dir = self.project_root / 'output'
            deleted_count = {'audio': 0, 'images': 0, 'clips': 0, 'videos': 0}
            freed_space = 0

            # 1. Clean audio files
            audio_dir = output_dir / 'audio'
            if audio_dir.exists():
                for audio_file in audio_dir.glob('*.mp3'):
                    try:
                        size = audio_file.stat().st_size
                        audio_file.unlink()
                        deleted_count['audio'] += 1
                        freed_space += size
                    except Exception as e:
                        self.logger.warning(f"Could not delete {audio_file.name}: {e}")

            # 2. Clean image files
            images_dir = output_dir / 'images'
            if images_dir.exists():
                for item in images_dir.iterdir():
                    try:
                        if item.is_dir():
                            # Calculate size before deletion
                            for img_file in item.rglob('*'):
                                if img_file.is_file():
                                    freed_space += img_file.stat().st_size
                                    deleted_count['images'] += 1
                            shutil.rmtree(item)
                        elif item.is_file():
                            size = item.stat().st_size
                            item.unlink()
                            deleted_count['images'] += 1
                            freed_space += size
                    except Exception as e:
                        self.logger.warning(f"Could not delete {item.name}: {e}")

            # 3. Clean temporary video clips
            clips_dir = output_dir / 'videos' / 'clips'
            if clips_dir.exists():
                for clip_file in clips_dir.glob('*.mp4'):
                    try:
                        size = clip_file.stat().st_size
                        clip_file.unlink()
                        deleted_count['clips'] += 1
                        freed_space += size
                    except Exception as e:
                        self.logger.warning(f"Could not delete {clip_file.name}: {e}")

            # 4. Clean old videos (keep only the last N)
            videos_dir = output_dir / 'videos'
            if videos_dir.exists():
                # Get all video files sorted by modification time (newest first)
                video_files = sorted(
                    [f for f in videos_dir.glob('*.mp4') if f.is_file()],
                    key=lambda x: x.stat().st_mtime,
                    reverse=True
                )

                # Delete old videos (keep the newest N)
                if len(video_files) > keep_last_n_videos:
                    for old_video in video_files[keep_last_n_videos:]:
                        try:
                            size = old_video.stat().st_size
                            old_video.unlink()
                            deleted_count['videos'] += 1
                            freed_space += size
                            self.logger.info(f"  Deleted old video: {old_video.name}")
                        except Exception as e:
                            self.logger.warning(f"Could not delete {old_video.name}: {e}")

            # Log cleanup summary
            freed_mb = freed_space / (1024 * 1024)
            self.logger.info(f"✓ Cleanup complete:")
            self.logger.info(f"  • Audio files:  {deleted_count['audio']} deleted")
            self.logger.info(f"  • Image files:  {deleted_count['images']} deleted")
            self.logger.info(f"  • Video clips:  {deleted_count['clips']} deleted")
            self.logger.info(f"  • Old videos:   {deleted_count['videos']} deleted")
            self.logger.info(f"  • Space freed:  {freed_mb:.2f} MB")

            if keep_last_n_videos > 0:
                remaining_videos = len([f for f in videos_dir.glob('*.mp4') if f.is_file()]) if videos_dir.exists() else 0
                self.logger.info(f"  • Videos kept:  {remaining_videos} most recent")

        except Exception as e:
            self.logger.warning(f"Cleanup encountered an error (non-critical): {e}")
            self.logger.info("Continuing with video generation...")

    def run(self) -> bool:
        """
        Execute the complete automation pipeline.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Set up logging
            self._setup_logging()

            # Clean up previous data to save space
            self._cleanup_previous_data(keep_last_n_videos=3)

            # Execute pipeline steps
            self.logger.info("Starting automation pipeline...")

            # Step 1: Select Topic
            if not self._step_select_topic():
                return False

            # Step 2: Generate Script
            if not self._step_generate_script():
                return False

            # Step 3: Generate Images
            if not self._step_generate_images():
                return False

            # Step 4: Generate Voiceover
            if not self._step_generate_voiceover():
                return False

            # Step 5: Create Video
            if not self._step_create_video():
                return False

            # Step 6: Generate Metadata
            if not self._step_generate_metadata():
                return False

            # Step 7: Upload to YouTube
            if not self._step_upload_to_youtube():
                return False

            # Success!
            self._log_success()
            return True

        except KeyboardInterrupt:
            self.logger.warning("Automation interrupted by user")
            return False

        except Exception as e:
            self.logger.error(f"CRITICAL ERROR: {e}", exc_info=True)
            self._log_failure(str(e))
            return False

    def _step_select_topic(self) -> bool:
        """
        Step 1: Select a kid-friendly video topic.
        Uses EarlyLearningTopicSelector for controlled early learning content.

        Returns:
            bool: True if successful
        """
        self.logger.info("-" * 80)
        self.logger.info("STEP 1: Selecting Video Topic")
        self.logger.info("-" * 80)

        try:
            if self.test_mode:
                import test_data
                topic = test_data.get_test_topic()
                self.logger.info(f"[TEST MODE] Using test topic: {topic}")
            else:
                # Check if early learning mode is enabled
                use_early_learning = self.config.get('use_early_learning_only', False)

                if use_early_learning or self.category == 'kids':
                    # Use controlled early learning selector (ages 2-6)
                    self.logger.info("📚 Using EARLY LEARNING topic selector (ages 2-6)")
                    selector = EarlyLearningTopicSelector(
                        data_dir=str(self.project_root / 'data')
                    )
                    topic_data = selector.select_topic(language=self.language)
                    topic = topic_data['topic']

                    # Log additional info
                    self.logger.info(f"   📊 Category: {topic_data['category']}")
                    self.logger.info(f"   👶 Age Group: {topic_data['age_group']}")
                    self.logger.info(f"   🌍 Language: {topic_data['language']}")

                    # Store full topic data
                    self.session_data['topic_data'] = topic_data
                else:
                    # Use general topic selector
                    self.logger.info(f"Using general topic selector (category: {self.category})")
                    selector = KidsTopicSelector(
                        api_key=self.config['openai_api_key'],
                        temperature=0.8,
                        category=self.category
                    )
                    topic = selector.select_topic()

            self.session_data['topic'] = topic

            self.logger.info(f"✓ Topic selected: {topic}")
            self.logger.info(f"   Category: {self.category}")
            self.logger.info(f"   Language: {self.language}")
            return True

        except Exception as e:
            self.logger.error(f"✗ Topic selection failed: {type(e).__name__}: {e}")
            self.logger.debug(f"Stack trace: {traceback.format_exc()}")
            return False

    def _step_generate_script(self) -> bool:
        """
        Step 2: Generate structured video script.

        Returns:
            bool: True if successful
        """
        self.logger.info("-" * 80)
        self.logger.info("STEP 2: Generating Video Script")
        self.logger.info("-" * 80)

        try:
            if self.test_mode:
                import test_data
                from dataclasses import dataclass
                from typing import List

                test_script_data = test_data.get_test_script(self.session_data['topic'])
                self.logger.info(f"[TEST MODE] Using pre-written test script")

                # Convert test data to VideoScript object (simplified)
                @dataclass
                class TestScriptSection:
                    section_number: int
                    title: str
                    duration_seconds: int
                    narration: str
                    visual_suggestions: List[str]

                @dataclass
                class TestVideoScript:
                    topic: str
                    target_duration_seconds: int
                    total_sections: int
                    intro: TestScriptSection
                    body_sections: List[TestScriptSection]
                    outro: TestScriptSection
                    full_narration: str
                    estimated_word_count: int

                    def to_dict(self):
                        return {
                            'topic': self.topic,
                            'sections': [self.intro] + self.body_sections + [self.outro]
                        }

                # Build sections
                sections = []
                intro = None
                body_sections = []
                outro = None
                full_narration = []

                for idx, section_data in enumerate(test_script_data['sections'], 1):
                    section = TestScriptSection(
                        section_number=idx,
                        title=section_data['type'].title(),
                        duration_seconds=section_data['duration'],
                        narration=section_data['narration'],
                        visual_suggestions=[section_data['image_description']]
                    )

                    full_narration.append(section_data['narration'])

                    if section_data['type'] == 'intro':
                        intro = section
                    elif section_data['type'] == 'outro':
                        outro = section
                    else:
                        body_sections.append(section)

                script = TestVideoScript(
                    topic=test_script_data['topic'],
                    target_duration_seconds=test_script_data['total_duration'],
                    total_sections=len(test_script_data['sections']),
                    intro=intro,
                    body_sections=body_sections,
                    outro=outro,
                    full_narration=' '.join(full_narration),
                    estimated_word_count=len(' '.join(full_narration).split())
                )
            else:
                generator = KidsScriptGenerator(
                    api_key=self.config['openai_api_key'],
                    min_duration=180,
                    max_duration=900,
                    language=self.language
                )

                script = generator.generate_script(
                    topic=self.session_data['topic'],
                    target_duration=self.config['target_duration']
                )

            self.session_data['script'] = script

            self.logger.info(f"✓ Script generated successfully")
            self.logger.info(f"   Sections: {script.total_sections}")
            self.logger.info(f"   Words: {script.estimated_word_count}")
            self.logger.info(f"   Target duration: {script.target_duration_seconds}s ({script.target_duration_seconds/60:.1f} min)")
            self.logger.info(f"   Estimated cost: ~$0.01 (script generation)")

            return True

        except Exception as e:
            self.logger.error(f"✗ Script generation failed: {type(e).__name__}: {e}")
            self.logger.debug(f"Stack trace: {traceback.format_exc()}")
            return False

    def _step_generate_images(self) -> bool:
        """
        Step 3: Generate AI images for video OR fetch real video clips.

        Returns:
            bool: True if successful
        """
        self.logger.info("-" * 80)
        if self.use_videos:
            self.logger.info("STEP 3: Fetching Real Video Clips (Pexels)")
        else:
            self.logger.info("STEP 3: Generating Images")
        self.logger.info("-" * 80)

        try:
            # If using real videos, fetch from Pexels
            if self.use_videos:
                return self._fetch_pexels_videos()

            # Otherwise, continue with images...
            # In test mode or without API key, use placeholder images
            if self.test_mode or not self.config['openai_api_key']:
                if self.test_mode:
                    self.logger.info("[TEST MODE] Using placeholder images")
                else:
                    self.logger.warning("OpenAI API key not available, using placeholders")

                # Use fallback placeholder images
                from PIL import Image, ImageDraw, ImageFont
                images_dir = self.project_root / 'output' / 'images' / 'fallback'
                images_dir.mkdir(parents=True, exist_ok=True)

                # Create colorful placeholder images
                num_sections = self.session_data['script'].total_sections
                colors = [
                    (255, 100, 100),  # Red
                    (100, 180, 255),  # Blue
                    (100, 220, 100),  # Green
                    (255, 200, 100),  # Orange
                    (200, 100, 255),  # Purple
                    (255, 220, 100),  # Yellow
                    (100, 200, 200),  # Cyan
                    (255, 150, 200),  # Pink
                ]

                images = []
                for i in range(num_sections):
                    color = colors[i % len(colors)]
                    img = Image.new('RGB', (1920, 1080), color=color)
                    draw = ImageDraw.Draw(img)

                    # Try to use a nice font, fallback to default
                    try:
                        font = ImageFont.truetype("arial.ttf", 80)
                    except:
                        font = ImageFont.load_default()

                    text = f"Scene {i+1}\n{self.session_data['topic']}"

                    # Get text bounding box for centering
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]

                    position = ((1920 - text_width) // 2, (1080 - text_height) // 2)
                    draw.text(position, text, fill=(255, 255, 255), font=font)

                    img_path = images_dir / f"placeholder_{i+1}.png"
                    img.save(img_path)
                    images.append(str(img_path))
                    self.logger.info(f"Created placeholder image {i+1}: {img_path.name}")

                self.session_data['images'] = images
                self.logger.info(f"✓ Created {len(images)} placeholder images")
                return True

            # Use API to generate images
            generator = KidsImageGenerator(
                api_key=self.config['openai_api_key'],
                seconds_per_image=30
            )

            script_dict = self.session_data['script'].to_dict()
            images = generator.generate_images_from_script(script_dict)

            self.session_data['images'] = images

            self.logger.info(f"✓ Successfully generated {len(images)} images")
            self.logger.info(f"   Est. cost: ~${len(images) * 0.04:.2f} (DALL-E 3)")
            self.logger.info(f"   Images saved to: output/images/")

            return True

        except Exception as e:
            self.logger.error(f"✗ Image generation failed: {type(e).__name__}: {e}")
            self.logger.debug(f"Stack trace: {traceback.format_exc()}")
            self.logger.warning("Attempting to continue with placeholder images...")

            # Try to create minimal placeholders as fallback
            try:
                from PIL import Image
                images_dir = self.project_root / 'output' / 'images' / 'fallback'
                images_dir.mkdir(parents=True, exist_ok=True)

                # Create at least 5 images
                images = []
                for i in range(5):
                    img = Image.new('RGB', (1920, 1080), color=(80 + i*30, 120, 180))
                    img_path = images_dir / f"placeholder_{i+1}.png"
                    img.save(img_path)
                    images.append(str(img_path))

                self.session_data['images'] = images
                self.logger.info(f"✓ Created {len(images)} fallback images")
                return True

            except Exception as fallback_error:
                self.logger.error(f"✗ Fallback image creation also failed: {fallback_error}")
                return False

    def _fetch_pexels_videos(self) -> bool:
        """
        Fetch real video clips from Pexels for animated content.

        Returns:
            bool: True if successful
        """
        try:
            # Check for Pexels API key
            if not self.config.get('pexels_api_key'):
                self.logger.error("✗ PEXELS_API_KEY not set in .env file")
                self.logger.info("Get your FREE API key from: https://www.pexels.com/api/")
                return False

            # Import Pexels fetcher
            from src.pexels_video_fetcher import PexelsVideoFetcher

            fetcher = PexelsVideoFetcher(
                api_key=self.config['pexels_api_key']
            )

            # Get script sections to create search queries
            script = self.session_data['script']

            # Build list of all sections (intro + body + outro)
            sections = []
            if hasattr(script, 'intro') and script.intro:
                sections.append(script.intro)
            if hasattr(script, 'body_sections') and script.body_sections:
                sections.extend(script.body_sections)
            if hasattr(script, 'outro') and script.outro:
                sections.append(script.outro)

            if not sections:
                self.logger.error("✗ No script sections found")
                return False

            self.logger.info(f"Fetching {len(sections)} video clips from Pexels...")

            videos = []
            for i, section in enumerate(sections):
                # Extract search query from section
                # Use title or first visual suggestion
                query = None

                if hasattr(section, 'title') and section.title:
                    query = section.title
                elif hasattr(section, 'visual_suggestions') and section.visual_suggestions:
                    query = section.visual_suggestions[0]
                else:
                    # Fallback to narration keywords
                    query = self.session_data['topic']

                self.logger.info(f"Searching for: '{query}'")

                # Search for videos
                results = fetcher.search_videos(query, per_page=1)

                if not results:
                    self.logger.warning(f"No videos found for '{query}', trying topic...")
                    # Fallback to main topic
                    results = fetcher.search_videos(self.session_data['topic'], per_page=1)

                if results:
                    # Download first result
                    video_data = results[0]
                    filename = f"section_{i+1:03d}.mp4"

                    video_path = fetcher.download_video(video_data, filename, quality='hd')

                    if video_path:
                        videos.append(video_path)
                        self.logger.info(f"✓ Downloaded video {i+1}/{len(sections)}")
                    else:
                        self.logger.warning(f"Failed to download video for section {i+1}")
                else:
                    self.logger.warning(f"No videos available for section {i+1}")

                # Rate limiting
                import time
                time.sleep(0.5)

            if not videos:
                self.logger.error("✗ No videos were downloaded")
                return False

            # Store videos in session data
            self.session_data['videos'] = videos
            self.session_data['images'] = []  # Clear images since we're using videos

            self.logger.info(f"✓ Downloaded {len(videos)} video clips from Pexels")
            return True

        except Exception as e:
            self.logger.error(f"✗ Pexels video fetching failed: {e}", exc_info=True)
            return False

    def _compile_video_clips(self) -> bool:
        """
        Compile video clips with voiceover audio.

        Returns:
            bool: True if successful
        """
        try:
            import subprocess

            videos = self.session_data['videos']
            voiceover = self.session_data['voiceover_path']

            if not videos:
                self.logger.error("✗ No video clips to compile")
                return False

            self.logger.info(f"Compiling {len(videos)} video clips...")

            # Get voiceover duration
            ffmpeg_dir = Path(self.config['ffmpeg_path']).parent
            ffprobe_path = str(ffmpeg_dir / 'ffprobe.exe')

            duration_cmd = [
                ffprobe_path,
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'json',
                voiceover
            ]

            result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
            import json
            duration_data = json.loads(result.stdout)
            total_duration = float(duration_data['format']['duration'])

            self.logger.info(f"Target duration: {total_duration:.2f} seconds")

            # Calculate duration per clip
            duration_per_clip = total_duration / len(videos)

            self.logger.info(f"Duration per clip: {duration_per_clip:.2f} seconds")

            # Create a file list for concatenation
            output_dir = self.project_root / 'output' / 'videos'
            output_dir.mkdir(parents=True, exist_ok=True)

            # Output filename
            output_filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            output_path = output_dir / output_filename

            # Build complex filter to handle each video clip with proper duration
            filter_parts = []

            # First, loop and trim each video to the exact duration needed
            for i, video in enumerate(videos):
                # Smart cropping and scaling for proper framing (no black bars)
                # 1. Scale to cover the output size (some parts may be cropped)
                # 2. Crop to exact 16:9 aspect ratio centered
                # 3. Apply slight zoom and position for better composition
                filter_parts.append(
                    f"[{i}:v]loop=loop=-1:size=32767:start=0,trim=duration={duration_per_clip},"
                    f"setpts=PTS-STARTPTS,"
                    f"scale=1920:1080:force_original_aspect_ratio=increase,"
                    f"crop=1920:1080,"
                    f"setsar=1,fps=30,"
                    f"eq=contrast=1.05:brightness=0.02:saturation=1.1[v{i}]"
                )

            # Then concatenate all processed clips
            video_inputs = ''.join(f'[v{i}]' for i in range(len(videos)))
            filter_parts.append(f"{video_inputs}concat=n={len(videos)}:v=1:a=0[outv]")

            filter_complex = ';'.join(filter_parts)

            # FFmpeg command
            cmd = [
                self.config['ffmpeg_path'],
                '-y'
            ]

            # Add all video inputs
            for video in videos:
                cmd.extend(['-i', video])

            # Add audio input
            cmd.extend(['-i', voiceover])

            # Add filter complex with better quality settings
            cmd.extend([
                '-filter_complex', filter_complex,
                '-map', '[outv]',
                '-map', f'{len(videos)}:a',
                '-c:v', 'libx264',
                '-preset', 'slow',  # Better quality
                '-crf', '20',  # Higher quality (lower = better)
                '-profile:v', 'high',
                '-level', '4.0',
                '-pix_fmt', 'yuv420p',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-shortest',
                str(output_path)
            ])

            self.logger.info("Running FFmpeg to compile video...")

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            self.session_data['video_path'] = str(output_path)

            file_size = output_path.stat().st_size / (1024 * 1024)
            self.logger.info(f"✓ Video compiled: {output_filename} ({file_size:.2f} MB)")

            return True

        except Exception as e:
            self.logger.error(f"✗ Video compilation failed: {e}", exc_info=True)
            return False

    def _step_generate_voiceover(self) -> bool:
        """
        Step 4: Generate voiceover audio.

        Returns:
            bool: True if successful
        """
        self.logger.info("-" * 80)
        self.logger.info("STEP 4: Generating Voiceover")
        self.logger.info("-" * 80)

        try:
            # Check if ElevenLabs API key is available
            if not self.config.get('elevenlabs_api_key'):
                self.logger.warning("ElevenLabs API key not set")
                self.logger.info("Using gTTS (Google Text-to-Speech) as fallback")

                # Use gTTS as fallback
                from gtts import gTTS

                output_dir = self.project_root / 'output'
                output_dir.mkdir(exist_ok=True)

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                audio_path = output_dir / f'voiceover_{timestamp}.mp3'

                narration = self.session_data['script'].full_narration

                # Use language parameter for TTS
                language_code = self.language if self.language in ['en', 'hi', 'es', 'fr', 'de', 'pt', 'ar', 'ja', 'ko', 'zh'] else 'en'

                tts = gTTS(text=narration, lang=language_code, slow=False)
                tts.save(str(audio_path))

                self.session_data['voiceover_path'] = str(audio_path)
                self.logger.info(f"✓ Voiceover generated with gTTS ({language_code}): {audio_path.name}")

                return True

            # Use ElevenLabs for better quality
            audio_dir = self.project_root / 'output' / 'audio'
            generator = KidsVoiceoverGenerator(
                api_key=self.config['elevenlabs_api_key'],
                output_dir=str(audio_dir),
                speed=0.85
            )

            narration = self.session_data['script'].full_narration

            voiceover_path = generator.generate_voiceover(
                text=narration,
                output_filename=f"voiceover_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            )

            self.session_data['voiceover_path'] = voiceover_path

            self.logger.info(f"✓ Voiceover generated: {Path(voiceover_path).name}")

            return True

        except Exception as e:
            self.logger.error(f"✗ Voiceover generation failed: {e}")
            return False

    def _extract_section_durations(self) -> Optional[List[float]]:
        """
        Extract section durations from script to sync images with narration.
        Handles cases where multiple images are generated per section by
        distributing section duration equally among images from that section.

        Returns:
            List[float]: List of durations (in seconds) for each image,
                        or None if extraction fails (will use equal distribution)
        """
        try:
            script = self.session_data.get('script')
            images = self.session_data.get('images', [])
            
            if not script or not images:
                self.logger.warning("No script or images found, using equal distribution")
                return None

            # Extract section durations
            section_durations = []

            # Add intro duration
            if hasattr(script, 'intro') and script.intro:
                section_durations.append(float(script.intro.duration_seconds))

            # Add body section durations
            if hasattr(script, 'body_sections') and script.body_sections:
                for section in script.body_sections:
                    section_durations.append(float(section.duration_seconds))

            # Add outro duration
            if hasattr(script, 'outro') and script.outro:
                section_durations.append(float(section.outro.duration_seconds))

            num_sections = len(section_durations)
            num_images = len(images)

            # Case 1: Exact match (1 image per section)
            if num_sections == num_images:
                self.logger.info(f"✓ Perfect match: {num_sections} sections = {num_images} images")
                return section_durations

            # Case 2: More images than sections (multiple images per section)
            if num_images > num_sections:
                self.logger.info(
                    f"Distributing {num_sections} section durations across {num_images} images..."
                )
                
                # Calculate how many images per section (approximately)
                images_per_section = num_images / num_sections
                
                # Distribute section durations proportionally to images
                image_durations = []
                images_assigned = 0
                
                for i, section_dur in enumerate(section_durations):
                    # Calculate how many images for this section
                    if i == num_sections - 1:
                        # Last section gets all remaining images
                        section_images = num_images - images_assigned
                    else:
                        # Round to nearest integer
                        section_images = round((i + 1) * images_per_section) - images_assigned
                        section_images = max(1, section_images)  # At least 1 image per section
                    
                    # Distribute section duration with NATURAL VARIATION (±20%)
                    # Makes timing feel organic, not robotic
                    import random
                    dur_per_image = section_dur / section_images
                    
                    for img_idx in range(section_images):
                        # Add random variation (80%-120% of base duration)
                        variation = random.uniform(0.8, 1.2)
                        varied_duration = dur_per_image * variation
                        image_durations.append(varied_duration)
                    
                    images_assigned += section_images
                    self.logger.info(
                        f"  Section {i+1}: {section_dur:.1f}s → {section_images} images "
                        f"({dur_per_image:.1f}s each)"
                    )

                return image_durations

            # Case 3: Fewer images than sections (shouldn't happen, but handle it)
            else:
                self.logger.warning(
                    f"Unexpected: {num_images} images < {num_sections} sections. "
                    f"Using equal distribution."
                )
                return None

        except Exception as e:
            self.logger.warning(f"Failed to extract section durations: {e}. Using equal distribution.")
            return None

    def _step_create_video(self) -> bool:
        """
        Step 5: Create video from images/videos and audio.

        Returns:
            bool: True if successful
        """
        self.logger.info("-" * 80)
        if self.use_videos:
            self.logger.info("STEP 5: Compiling Video from Clips")
        else:
            self.logger.info("STEP 5: Creating Video")
        self.logger.info("-" * 80)

        try:
            # If using real videos, compile them differently
            if self.use_videos and self.session_data.get('videos'):
                return self._compile_video_clips()

            # Otherwise use images...
            creator = KidsVideoCreator(
                ffmpeg_path=self.config['ffmpeg_path']
            )

            # Mix voiceover with background music using new mixer
            try:
                mixer = BackgroundMusicMixer(
                    music_dir=str(self.project_root / 'assets' / 'music'),
                    ffmpeg_path=self.config['ffmpeg_path']
                )

                # Get category from topic_data if available
                topic_data = self.session_data.get('topic_data', {})
                category = topic_data.get('category_key', 'default')

                # Create mixed audio with background music
                mixed_audio_path = self.project_root / 'output' / 'audio' / f"mixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
                mixed_audio = mixer.mix_audio_with_music(
                    voiceover_path=self.session_data['voiceover_path'],
                    output_path=str(mixed_audio_path),
                    category=category,
                    ducking_enabled=True
                )
                self.logger.info(f"✅ Mixed audio with background music (category: {category})")
                voiceover_to_use = mixed_audio
            except Exception as e:
                self.logger.warning(f"⚠️ Background music mixing failed: {e}. Using original voiceover.")
                voiceover_to_use = self.session_data['voiceover_path']

            # Extract section durations from script for proper image sync
            image_durations = self._extract_section_durations()

            video_path = creator.create_video(
                images=self.session_data['images'],
                voiceover_path=voiceover_to_use,
                background_music=None,  # Already in audio
                output_filename=f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                title=self.session_data['topic'],
                image_durations=image_durations
            )

            self.session_data['video_path'] = video_path

            file_size = Path(video_path).stat().st_size / (1024 * 1024)
            self.logger.info(f"✓ Video created: {Path(video_path).name} ({file_size:.2f} MB)")

            return True

        except Exception as e:
            self.logger.error(f"✗ Video creation failed: {e}")
            return False

    def _step_generate_metadata(self) -> bool:
        """
        Step 6: Generate YouTube metadata with advanced SEO optimization.

        Returns:
            bool: True if successful
        """
        start_time = time.time()
        self.logger.info("\n" + "="*70)
        self.logger.info("🎯 STEP 6: Generating YouTube Metadata with SEO Optimization")
        self.logger.info("="*70)

        try:
            if self.test_mode:
                import test_data
                from src.youtube_metadata_generator import YouTubeMetadata

                test_meta = test_data.get_test_metadata(self.session_data['topic'])
                self.logger.info(f"[TEST MODE] Using pre-written test metadata")

                metadata = YouTubeMetadata(
                    title=test_meta['title'],
                    description=test_meta['description'],
                    tags=test_meta['tags']
                )
                self.session_data['metadata'] = metadata
                self.logger.info(f"✓ Test metadata loaded")
                return True

            # Step 1: Generate base metadata
            self.logger.info("📝 Generating base metadata...")
            generator = YouTubeMetadataGenerator(
                api_key=self.config['openai_api_key']
            )

            script_dict = self.session_data['script'].to_dict()
            base_metadata = generator.generate_metadata(
                topic=self.session_data['topic'],
                script=script_dict
            )

            self.logger.info("✓ Base metadata generated")

            # Step 2: Advanced SEO optimization
            self.logger.info("\n🚀 Running advanced SEO optimization...")

            # Research keywords
            self.logger.info("🔍 Researching keywords and trends...")
            seo_optimizer = YouTubeSEOOptimizer(
                api_key=self.config['openai_api_key']
            )

            keywords = seo_optimizer.research_keywords(
                topic=self.session_data['topic'],
                category=self.category,
                language=self.language
            )

            self.logger.info("✓ Keyword research complete")
            self.logger.info(f"   • Primary keywords: {', '.join(keywords.primary_keywords[:3])}")
            self.logger.info(f"   • Long-tail keywords: {len(keywords.long_tail_keywords)}")
            self.logger.info(f"   • Trending keywords: {', '.join(keywords.trending_keywords[:3])}")

            # Optimize title with A/B testing
            self.logger.info("\n📊 Optimizing title (generating 5 variants)...")
            best_title, title_variants, title_scores = seo_optimizer.optimize_title(
                topic=self.session_data['topic'],
                keywords=keywords,
                generate_variants=5
            )

            self.logger.info("✓ Title optimization complete")
            self.logger.info(f"   🏆 Best title (score: {title_scores.get(best_title, 0)}/100):")
            self.logger.info(f"      {best_title}")

            # Show other variants
            if len(title_variants) > 1:
                self.logger.info("   📋 Other variants:")
                for i, variant in enumerate(title_variants[1:4], 2):
                    score = title_scores.get(variant, 0)
                    self.logger.info(f"      #{i} (score: {score}): {variant[:60]}..." if len(variant) > 60 else f"      #{i} (score: {score}): {variant}")

            # Update metadata with optimized title
            base_metadata.title = best_title

            # Enhance metadata with keywords
            self.logger.info("\n✨ Enhancing tags and hashtags with research data...")
            enhanced_dict = seo_optimizer.enhance_metadata_with_keywords(
                metadata=base_metadata.to_dict(),
                keywords=keywords
            )

            # Update metadata
            base_metadata.tags = enhanced_dict['tags']
            base_metadata.hashtags = enhanced_dict['hashtags']
            base_metadata.description = enhanced_dict.get('description', base_metadata.description)

            self.logger.info("✓ Metadata enhanced")
            self.logger.info(f"   • Tags: {len(base_metadata.tags)}")
            self.logger.info(f"   • Hashtags: {len(base_metadata.hashtags)}")

            # Score SEO quality
            self.logger.info("\n📊 Analyzing SEO quality...")
            seo_score = seo_optimizer.score_seo_quality(
                title=base_metadata.title,
                description=base_metadata.description,
                tags=base_metadata.tags,
                hashtags=base_metadata.hashtags,
                keywords=keywords
            )

            # Display SEO score
            score_color = "🟢" if seo_score.overall_score >= 80 else "🟡" if seo_score.overall_score >= 60 else "🔴"
            self.logger.info("\n" + "="*70)
            self.logger.info(f"{score_color} SEO QUALITY SCORE: {seo_score.overall_score}/100")
            self.logger.info("="*70)
            self.logger.info(f"   Title:            {seo_score.title_score}/100")
            self.logger.info(f"   Description:      {seo_score.description_score}/100")
            self.logger.info(f"   Tags:             {seo_score.tags_score}/100")
            self.logger.info(f"   Hashtags:         {seo_score.hashtags_score}/100")
            self.logger.info(f"   Keyword Density:  {seo_score.keyword_density_score}/100")

            # Display strengths
            if seo_score.strengths:
                self.logger.info("\n✅ STRENGTHS:")
                for strength in seo_score.strengths[:5]:
                    self.logger.info(f"   • {strength}")

            # Display recommendations
            if seo_score.recommendations:
                self.logger.info("\n💡 RECOMMENDATIONS:")
                for rec in seo_score.recommendations[:5]:
                    self.logger.info(f"   • {rec}")

            self.logger.info("\n" + "="*70)

            # Store metadata and SEO data
            self.session_data['metadata'] = base_metadata
            self.session_data['seo_score'] = seo_score
            self.session_data['keywords'] = keywords
            self.session_data['title_variants'] = title_variants

            elapsed = time.time() - start_time

            self.logger.info(f"\n✓ Metadata generation complete in {elapsed:.1f}s")
            self.logger.info(f"   Title length: {len(base_metadata.title)} chars")
            self.logger.info(f"   Description: {len(base_metadata.description)} chars")
            self.logger.info(f"   Tags: {len(base_metadata.tags)}")
            self.logger.info(f"   Hashtags: {len(base_metadata.hashtags)}")

            return True

        except Exception as e:
            elapsed = time.time() - start_time
            self.logger.error(f"✗ Metadata generation failed after {elapsed:.1f}s: {type(e).__name__}: {e}")
            self.logger.debug(f"Stack trace: {traceback.format_exc()}")
            return False

    def _detect_playlist(self) -> Optional[str]:
        """
        Smart playlist detection using new PlaylistManager.
        Auto-creates category playlists and organizes videos.

        Returns:
            str: Playlist ID, or None if no playlist configured
        """
        try:
            # Initialize playlist manager
            manager = PlaylistManager(
                credentials_path=str(self.project_root / 'config' / 'youtube_token.pickle')
            )

            # Get category from topic_data
            topic_data = self.session_data.get('topic_data', {})
            category = topic_data.get('category_key', 'default')

            # Get or create playlist for this category
            playlist_id = manager.get_or_create_playlist(category, privacy_status="public")

            if playlist_id:
                self.logger.info(f"📚 Smart Playlist: {category} → {playlist_id}")
                # Store for later use in upload step
                self.session_data['smart_playlist_id'] = playlist_id
                self.session_data['smart_playlist_category'] = category
                return playlist_id
            else:
                self.logger.warning(f"⚠️ Could not create playlist for category: {category}")

        except Exception as e:
            self.logger.warning(f"⚠️ Smart playlist failed: {e}. Using legacy detection.")

        # Fallback to legacy keyword-based detection
        topic = self.session_data.get('topic', '').lower()

        # Kids keywords (for early learning content)
        kids_keywords = [
            'animal', 'color', 'count', 'shape', 'learn', 'abc', 'alphabet',
            'number', 'baby', 'nursery', 'fruit', 'vegetable', 'logic',
            'body', 'habit', 'emotion', 'math', 'rhyme', 'memory', 'puzzle'
        ]

        if any(keyword in topic for keyword in kids_keywords):
            playlist_id = self.config.get('kids_playlist_id', '')
            if playlist_id:
                self.logger.info(f"📁 Legacy: Kids topic → Kids playlist")
                return playlist_id

        self.logger.info(f"📁 No playlist configured")
        return None

    def _step_upload_to_youtube(self) -> bool:
        """
        Step 7: Upload video to YouTube.

        Returns:
            bool: True if successful
        """
        self.logger.info("-" * 80)
        self.logger.info("STEP 7: Uploading to YouTube")
        self.logger.info("-" * 80)

        try:
            uploader = YouTubeUploader(
                client_secrets_file=self.config['client_secrets_file']
            )

            # Authenticate (will use cached credentials if available)
            uploader.authenticate()

            metadata = self.session_data['metadata']

            # Calculate scheduled publish time if enabled
            publish_at = None
            if self.config.get('scheduled_publishing', False):
                delay_minutes = self.config.get('publish_delay_minutes', 15)
                publish_datetime = datetime.utcnow() + timedelta(minutes=delay_minutes)
                publish_at = publish_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
                self.logger.info(f"🕐 Scheduled publishing: Video will go live at {publish_at} UTC")

            # Detect appropriate playlist
            playlist_id = self._detect_playlist()

            result = uploader.upload_video(
                video_path=self.session_data['video_path'],
                title=metadata.title,
                description=metadata.get_description_with_hashtags(),
                tags=metadata.tags,
                thumbnail_path=None,  # Could generate thumbnail here
                privacy_status=self.config['privacy_status'],
                made_for_kids=self.config['made_for_kids'],
                playlist_id=playlist_id,
                publish_at=publish_at
            )

            self.session_data['upload_result'] = result

            self.logger.info(f"✓ Video uploaded successfully!")
            self.logger.info(f"  Video ID: {result.video_id}")
            self.logger.info(f"  URL: {result.video_url}")
            self.logger.info(f"  Privacy: {result.privacy_status}")
            if publish_at:
                self.logger.info(f"  📅 Scheduled: Will publish at {publish_at} UTC")
            if playlist_id:
                self.logger.info(f"  Added to playlist: {playlist_id}")

            # Smart playlist organization
            try:
                if self.session_data.get('smart_playlist_category'):
                    manager = PlaylistManager(
                        credentials_path=str(self.project_root / 'config' / 'youtube_token.pickle')
                    )

                    category = self.session_data['smart_playlist_category']
                    topic_data = self.session_data.get('topic_data', {})
                    age_group = topic_data.get('age_group', '').split()[0]  # "2-6 years" -> "2-6"

                    # Organize video into category and age playlists
                    success = manager.organize_video(
                        video_id=result.video_id,
                        category=category,
                        age_group=age_group if '-' in age_group else None
                    )

                    if success:
                        self.logger.info(f"📚 Smart playlists organized: {category} + Age {age_group}")

            except Exception as e:
                self.logger.warning(f"⚠️ Smart playlist organization failed: {e}")

            return True

        except Exception as e:
            self.logger.error(f"✗ YouTube upload failed: {e}")
            return False

    def _log_success(self) -> None:
        """Log successful completion."""
        duration = (datetime.now() - self.session_data['start_time']).total_seconds()

        self.logger.info("=" * 80)
        self.logger.info("AUTOMATION COMPLETED SUCCESSFULLY!")
        self.logger.info("=" * 80)
        self.logger.info(f"Topic: {self.session_data['topic']}")
        self.logger.info(f"Video URL: {self.session_data['upload_result'].video_url}")
        self.logger.info(f"Total execution time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        self.logger.info("=" * 80)

    def _log_failure(self, error: str) -> None:
        """
        Log failure information.

        Args:
            error: Error message
        """
        duration = (datetime.now() - self.session_data['start_time']).total_seconds()

        self.logger.error("=" * 80)
        self.logger.error("AUTOMATION FAILED")
        self.logger.error("=" * 80)
        self.logger.error(f"Error: {error}")
        self.logger.error(f"Execution time before failure: {duration:.1f} seconds")
        self.logger.error("=" * 80)


def main():
    """Main entry point for automation script."""
    import argparse

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='YouTube Kids Video Automation System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Run in test mode using pre-written content (no OpenAI API calls)'
    )
    parser.add_argument(
        '--skip-upload',
        action='store_true',
        help='Skip YouTube upload step (for testing video creation only)'
    )
    parser.add_argument(
        '--use-videos',
        action='store_true',
        help='Use real video clips from Pexels instead of static images (requires PEXELS_API_KEY)'
    )
    parser.add_argument(
        '--category',
        type=str,
        choices=['tech', 'kids', 'science', 'auto'],
        default='auto',
        help='Video category: tech (technology/AI), kids (educational for children), science (physics/chemistry/biology), or auto (automatic detection)'
    )
    parser.add_argument(
        '--language',
        type=str,
        choices=['en', 'hi', 'es', 'fr', 'de', 'pt', 'ar', 'ja', 'ko', 'zh'],
        default='en',
        help='Video language: en (English), hi (Hindi), es (Spanish), fr (French), de (German), pt (Portuguese), ar (Arabic), ja (Japanese), ko (Korean), zh (Chinese)'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("YouTube Kids Video Automation System")
    if args.test_mode:
        print("[TEST MODE - Using pre-written content]")
    if args.use_videos:
        print("[VIDEO MODE - Using real Pexels video clips]")
    if args.category != 'auto':
        category_names = {'tech': 'Technology', 'kids': 'Kids Educational', 'science': 'Science'}
        print(f"[CATEGORY: {category_names[args.category]}]")
    if args.language != 'en':
        language_names = {'hi': 'Hindi', 'es': 'Spanish', 'fr': 'French', 'de': 'German', 'pt': 'Portuguese', 'ar': 'Arabic', 'ja': 'Japanese', 'ko': 'Korean', 'zh': 'Chinese'}
        print(f"[LANGUAGE: {language_names[args.language]}]")
    print("=" * 80)
    print()

    try:
        # Create orchestrator
        orchestrator = YouTubeAutomationOrchestrator(
            test_mode=args.test_mode,
            use_videos=args.use_videos,
            category=args.category,
            language=args.language
        )

        # Run automation
        success = orchestrator.run()

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"FATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
