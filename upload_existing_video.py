"""
Upload an existing video to YouTube

Usage:
    python upload_existing_video.py path/to/video.mp4
    python upload_existing_video.py path/to/video.mp4 --title "Custom Title" --description "Custom description"
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import config
from src.youtube_uploader import YouTubeUploader


def upload_video(
    video_path: str,
    title: str = None,
    description: str = None,
    tags: list = None,
    category_id: int = 27,  # Education category
    privacy_status: str = None
):
    """
    Upload a video to YouTube.
    
    Args:
        video_path: Path to video file
        title: Video title (default: filename)
        description: Video description
        tags: List of tags
        category_id: YouTube category (27 = Education)
        privacy_status: 'public', 'private', or 'unlisted'
    """
    video_path = Path(video_path)
    
    if not video_path.exists():
        print(f"❌ Error: Video file not found: {video_path}")
        return False
    
    # Default values
    if title is None:
        title = video_path.stem.replace('_', ' ').title()
    
    if description is None:
        description = f"""Educational video for kids created with YouTube Automation System.

📚 Perfect for children ages 4-8
🎨 Colorful and engaging content
👨‍👩‍👧‍👦 Safe for the whole family

#KidsEducation #LearningForKids #EducationalContent"""
    
    if tags is None:
        tags = [
            "kids education",
            "educational videos",
            "learning for kids",
            "children learning",
            "kids videos",
            "educational content",
            "kids learning",
            "preschool education"
        ]
    
    if privacy_status is None:
        privacy_status = config.YOUTUBE_PRIVACY_STATUS or 'private'
    
    print("=" * 60)
    print("YouTube Video Upload")
    print("=" * 60)
    print(f"Video: {video_path.name}")
    print(f"Title: {title}")
    print(f"Privacy: {privacy_status}")
    print(f"Category: {category_id} (Education)")
    print(f"Tags: {len(tags)}")
    print("=" * 60)
    print()
    
    try:
        # Create uploader
        uploader = YouTubeUploader(
            client_secrets_file=str(config.YOUTUBE_CLIENT_SECRETS_FILE)
        )
        
        # Upload video
        print("Starting upload...")
        print("Note: Browser will open for authorization on first use")
        print()
        
        video_id = uploader.upload_video(
            video_path=str(video_path),
            title=title,
            description=description,
            tags=tags,
            category_id=category_id,
            privacy_status=privacy_status,
            made_for_kids=config.YOUTUBE_MADE_FOR_KIDS
        )
        
        print()
        print("=" * 60)
        print("✅ Upload Successful!")
        print("=" * 60)
        print(f"Video ID: {video_id}")
        print(f"Watch URL: https://www.youtube.com/watch?v={video_id}")
        
        if privacy_status == 'private':
            print()
            print("⚠️  Video is PRIVATE - only you can see it")
            print("To make it public, go to YouTube Studio and change privacy")
        
        print("=" * 60)
        
        return True
        
    except KeyboardInterrupt:
        print("\n❌ Upload canceled by user")
        return False
    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Upload an existing video to YouTube',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python upload_existing_video.py output/videos/video_20260206_022442.mp4
  python upload_existing_video.py video.mp4 --title "My Video" --privacy public
  python upload_existing_video.py video.mp4 --tags "kids,education,fun"
        """
    )
    
    parser.add_argument(
        'video_path',
        help='Path to video file to upload'
    )
    parser.add_argument(
        '--title',
        help='Video title (default: filename)'
    )
    parser.add_argument(
        '--description',
        help='Video description'
    )
    parser.add_argument(
        '--tags',
        help='Comma-separated tags (e.g., "kids,education,fun")'
    )
    parser.add_argument(
        '--privacy',
        choices=['public', 'private', 'unlisted'],
        help='Privacy status (default: from config or private)'
    )
    parser.add_argument(
        '--category',
        type=int,
        default=27,
        help='YouTube category ID (default: 27 = Education)'
    )
    
    args = parser.parse_args()
    
    # Parse tags if provided
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(',')]
    
    # Upload video
    success = upload_video(
        video_path=args.video_path,
        title=args.title,
        description=args.description,
        tags=tags,
        category_id=args.category,
        privacy_status=args.privacy
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
