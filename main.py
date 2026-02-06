"""
Main entry point for the YouTube automation system.

This script orchestrates the entire video generation and upload pipeline:
1. Loads configuration
2. Selects a video topic using AI
3. Generates a script
4. Creates video assets (images, voiceover)
5. Compiles video with FFmpeg
6. Generates thumbnail
7. Uploads to YouTube
8. Logs all activities

This script is designed to be run by Windows Task Scheduler on a schedule.
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config_loader import load_config
from src.logger_setup import setup_logging
from src.topic_selector import TopicSelector
from src.script_generator import ScriptGenerator
from src.asset_generator import AssetGenerator
from src.video_creator import VideoCreator
from src.thumbnail_generator import ThumbnailGenerator
from src.youtube_uploader import YouTubeUploader


def main():
    """Main execution function for automated YouTube video generation."""

    # Initialize logging
    logger = setup_logging()
    logger.info("=" * 80)
    logger.info("YouTube Automation System Starting")
    logger.info(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()
        logger.info("Configuration loaded successfully")

        # Initialize components
        topic_selector = TopicSelector(config)
        script_generator = ScriptGenerator(config)
        asset_generator = AssetGenerator(config)
        video_creator = VideoCreator(config)
        thumbnail_generator = ThumbnailGenerator(config)
        youtube_uploader = YouTubeUploader(config)

        # Step 1: Select topic
        logger.info("Selecting video topic...")
        topic = topic_selector.select_topic()
        logger.info(f"Selected topic: {topic['title']}")

        # Step 2: Generate script
        logger.info("Generating video script...")
        script = script_generator.generate_script(topic)
        logger.info(f"Script generated: {len(script['scenes'])} scenes")

        # Step 3: Generate assets (images, voiceover)
        logger.info("Generating video assets...")
        assets = asset_generator.generate_assets(script)
        logger.info("Assets generated successfully")

        # Step 4: Create video
        logger.info("Creating video with FFmpeg...")
        video_path = video_creator.create_video(script, assets)
        logger.info(f"Video created: {video_path}")

        # Step 5: Generate thumbnail
        logger.info("Generating thumbnail...")
        thumbnail_path = thumbnail_generator.generate_thumbnail(topic, script)
        logger.info(f"Thumbnail created: {thumbnail_path}")

        # Step 6: Upload to YouTube
        logger.info("Uploading to YouTube...")
        video_metadata = {
            'title': topic['title'],
            'description': script['description'],
            'tags': script.get('tags', []),
            'category_id': config['youtube']['category_id'],
            'privacy_status': config['youtube']['privacy_status']
        }

        upload_result = youtube_uploader.upload_video(
            video_path,
            thumbnail_path,
            video_metadata
        )

        logger.info(f"Upload successful! Video ID: {upload_result['video_id']}")
        logger.info(f"Video URL: https://www.youtube.com/watch?v={upload_result['video_id']}")

        # Success summary
        logger.info("=" * 80)
        logger.info("YouTube Automation System Completed Successfully")
        logger.info(f"Topic: {topic['title']}")
        logger.info(f"Video ID: {upload_result['video_id']}")
        logger.info(f"Duration: {upload_result.get('duration', 'N/A')} seconds")
        logger.info("=" * 80)

        return 0

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"FATAL ERROR: {str(e)}", exc_info=True)
        logger.error("YouTube Automation System Failed")
        logger.error("=" * 80)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
