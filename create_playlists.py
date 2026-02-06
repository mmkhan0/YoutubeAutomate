"""
YouTube Playlist Creator

Helper script to create playlists for organizing your automated videos.
Creates playlists and displays their IDs to add to your .env file.

Usage:
    python create_playlists.py
"""

import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from src.youtube_uploader import YouTubeUploader


def create_playlists():
    """Create playlists for video organization."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "=" * 80)
    print("📋 YouTube Playlist Creator")
    print("=" * 80 + "\n")
    
    # Load environment
    load_dotenv()
    
    # Check for client secrets
    project_root = Path(__file__).parent
    client_secrets = project_root / 'config' / 'client_secrets.json'
    
    if not client_secrets.exists():
        print("❌ Client secrets file not found!")
        print(f"Expected: {client_secrets}")
        print("\nPlease set up YouTube OAuth first.")
        sys.exit(1)
    
    # Create uploader
    print("🔐 Authenticating with YouTube...")
    uploader = YouTubeUploader(str(client_secrets))
    
    if not uploader.verify_authentication():
        print("\n❌ Authentication failed!")
        sys.exit(1)
    
    print("\n✓ Authenticated successfully!\n")
    
    # Define playlists to create
    playlists_to_create = [
        {
            "title": "Tech Knowledge Videos",
            "description": "Educational videos about technology, computers, internet, AI, and how things work.",
            "privacy": "public",
            "env_key": "TECH_PLAYLIST_ID"
        },
        {
            "title": "Kids Educational Videos",
            "description": "Fun and educational content for children covering animals, nature, and learning basics.",
            "privacy": "public",
            "env_key": "KIDS_PLAYLIST_ID"
        },
        {
            "title": "Science Explained",
            "description": "Science concepts made simple! Physics, chemistry, biology, and natural phenomena.",
            "privacy": "public",
            "env_key": "SCIENCE_PLAYLIST_ID"
        }
    ]
    
    print("Creating playlists...\n")
    
    created_playlists = []
    
    for playlist_config in playlists_to_create:
        print(f"📁 Creating: {playlist_config['title']}")
        
        playlist_id = uploader.create_playlist(
            title=playlist_config['title'],
            description=playlist_config['description'],
            privacy_status=playlist_config['privacy']
        )
        
        if playlist_id:
            created_playlists.append({
                'title': playlist_config['title'],
                'id': playlist_id,
                'env_key': playlist_config['env_key'],
                'url': f"https://www.youtube.com/playlist?list={playlist_id}"
            })
            print(f"  ✓ Created: {playlist_id}")
            print(f"  🔗 {created_playlists[-1]['url']}\n")
        else:
            print(f"  ❌ Failed to create\n")
    
    if not created_playlists:
        print("\n❌ No playlists were created.")
        sys.exit(1)
    
    # Display results
    print("\n" + "=" * 80)
    print("✅ SUCCESS! Playlists Created")
    print("=" * 80 + "\n")
    
    print("📋 Your Playlists:\n")
    for playlist in created_playlists:
        print(f"  {playlist['title']}")
        print(f"  ID: {playlist['id']}")
        print(f"  🔗 {playlist['url']}\n")
    
    print("=" * 80)
    print("📝 Add these IDs to your .env file:")
    print("=" * 80 + "\n")
    
    for playlist in created_playlists:
        print(f"{playlist['env_key']}={playlist['id']}")
    
    print("\n" + "=" * 80)
    print("🎯 Usage:")
    print("=" * 80 + "\n")
    
    print("Videos will be automatically added to the right playlist based on topic:")
    print("  • Tech topics → Tech Knowledge Videos")
    print("  • Kids topics → Kids Educational Videos")
    print("  • Science topics → Science Explained")
    print("\nJust run your automation as usual:")
    print("  python run_automation.py --use-videos")
    print("\n")


if __name__ == "__main__":
    try:
        create_playlists()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
