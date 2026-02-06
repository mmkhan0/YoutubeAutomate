"""
YouTube Playlist Auto-Organization Manager
Automatically creates and manages playlists for kids learning videos
"""

from pathlib import Path
from typing import Optional, Dict, List
import json
import logging
from datetime import datetime

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.oauth2.credentials import Credentials
except ImportError:
    build = None
    HttpError = None
    Credentials = None


class PlaylistManager:
    """Manage YouTube playlists for organized content"""

    # Playlist definitions for each category
    PLAYLIST_DEFINITIONS = {
        'english_alphabet': {
            'title': '🔤 ABC Learning - English Alphabet for Kids',
            'description': 'Learn the English alphabet A to Z! Fun and educational videos for toddlers and preschoolers ages 2-6. Each letter comes with colorful examples and easy-to-remember words.',
            'tags': ['alphabet', 'ABC', 'learning', 'kids', 'toddlers', 'preschool', 'education']
        },
        'hindi_alphabet': {
            'title': '🔤 हिंदी वर्णमाला - Hindi Alphabet for Kids',
            'description': 'हिंदी वर्णमाला सीखें! अ से ज्ञ तक। बच्चों के लिए मज़ेदार और शिक्षाप्रद वीडियो। Learn Hindi alphabet from अ to ज्ञ with fun examples!',
            'tags': ['hindi', 'alphabet', 'varnamala', 'learning', 'kids', 'hindi learning']
        },
        'numbers_counting': {
            'title': '🔢 Counting Numbers 1-20 for Kids',
            'description': 'Learn to count from 1 to 20! Fun number learning videos for toddlers and preschoolers. Master counting skills with colorful animations.',
            'tags': ['numbers', 'counting', 'math', 'kids', 'toddlers', 'learning', '123']
        },
        'colors_shapes': {
            'title': '🎨 Colors and Shapes for Toddlers',
            'description': 'Learn colors and shapes! Educational videos teaching colors (red, blue, yellow, etc.) and shapes (circle, square, triangle) to young children ages 2-6.',
            'tags': ['colors', 'shapes', 'learning', 'kids', 'toddlers', 'preschool']
        },
        'fruits_vegetables': {
            'title': '🍎 Fruits and Vegetables for Kids',
            'description': 'Learn about healthy fruits and vegetables! Fun educational videos introducing apples, bananas, carrots, tomatoes, and more to young children.',
            'tags': ['fruits', 'vegetables', 'healthy', 'food', 'kids', 'learning', 'nutrition']
        },
        'animals_sounds': {
            'title': '🐶 Animals and Their Sounds',
            'description': 'Learn about animals and the sounds they make! Meet dogs, cats, cows, elephants, and many more animals. Perfect for toddlers and preschoolers.',
            'tags': ['animals', 'animal sounds', 'kids', 'toddlers', 'learning', 'wildlife']
        },
        'simple_logic': {
            'title': '🧩 Simple Logic Games for Toddlers',
            'description': 'Learn basic logic concepts! Videos teaching big/small, more/less, same/different, and other foundational thinking skills for ages 2-6.',
            'tags': ['logic', 'thinking', 'cognitive', 'kids', 'toddlers', 'learning']
        },
        'body_parts': {
            'title': '👦 Body Parts Learning for Kids',
            'description': 'Learn body parts! Fun videos teaching children about head, shoulders, knees, toes, and all body parts through songs and animations.',
            'tags': ['body parts', 'anatomy', 'kids', 'toddlers', 'learning', 'education']
        },
        'daily_habits': {
            'title': '🪥 Good Daily Habits for Kids',
            'description': 'Learn good daily habits! Educational videos teaching brushing teeth, washing hands, getting dressed, and other important routines for young children.',
            'tags': ['habits', 'routine', 'hygiene', 'kids', 'toddlers', 'life skills']
        },
        'emotions': {
            'title': '😊 Learning About Emotions',
            'description': 'Understand emotions! Videos helping children recognize and express feelings like happy, sad, angry, surprised, and more. Emotional intelligence for ages 2-6.',
            'tags': ['emotions', 'feelings', 'kids', 'toddlers', 'social skills', 'EQ']
        },
        'basic_math': {
            'title': '➕ Basic Math Games for Kids',
            'description': 'Introduction to basic math! Simple addition, subtraction, more/less, and number games for preschoolers. Make math fun from an early age!',
            'tags': ['math', 'addition', 'numbers', 'kids', 'learning', 'preschool']
        },
        'rhymes_learning': {
            'title': '🎵 Nursery Rhymes with Learning',
            'description': 'Classic nursery rhymes with educational content! Twinkle Twinkle, ABC Song, and more favorites teaching letters, numbers, and concepts.',
            'tags': ['rhymes', 'nursery rhymes', 'songs', 'kids', 'toddlers', 'music']
        },
        'memory_games': {
            'title': '🧠 Memory Games for Toddlers',
            'description': 'Boost memory skills! Fun memory matching games and activities designed for toddlers and preschoolers to enhance cognitive development.',
            'tags': ['memory', 'games', 'cognitive', 'kids', 'toddlers', 'brain games']
        },
        'puzzle_games': {
            'title': '🧩 Puzzle Games for Young Minds',
            'description': 'Develop problem-solving skills! Shape sorting, simple puzzles, and thinking games appropriate for ages 2-6. Make learning fun!',
            'tags': ['puzzles', 'problem solving', 'games', 'kids', 'toddlers', 'thinking']
        },
        'observation_games': {
            'title': '👀 Observation Games for Kids',
            'description': 'Sharpen observation skills! Spot the difference, find the object, and other visual games helping children develop attention to detail.',
            'tags': ['observation', 'attention', 'games', 'kids', 'toddlers', 'visual']
        }
    }

    # Age-based playlist collections
    AGE_PLAYLISTS = {
        '2-3': {
            'title': '👶 Learning Videos for Ages 2-3',
            'description': 'Perfect for toddlers! Simple learning videos covering alphabet, numbers, colors, animals, and basic concepts for 2-3 year olds.',
            'categories': ['colors_shapes', 'animals_sounds', 'body_parts', 'fruits_vegetables']
        },
        '4-5': {
            'title': '👦 Learning Videos for Ages 4-5',
            'description': 'Preschool learning! Videos teaching alphabet, counting, simple logic, emotions, and daily habits for 4-5 year olds.',
            'categories': ['english_alphabet', 'numbers_counting', 'simple_logic', 'emotions', 'daily_habits']
        },
        '5-6': {
            'title': '👧 Learning Videos for Ages 5-6',
            'description': 'Advanced preschool content! Math games, puzzles, memory activities, and complex concepts for 5-6 year olds preparing for kindergarten.',
            'categories': ['basic_math', 'puzzle_games', 'memory_games', 'observation_games']
        }
    }

    def __init__(
        self,
        credentials_path: str = "config/youtube_token.pickle",
        playlist_cache_path: str = "data/playlists.json"
    ):
        """
        Initialize playlist manager

        Args:
            credentials_path: Path to YouTube OAuth credentials
            playlist_cache_path: Path to cache playlist IDs
        """
        self.credentials_path = Path(credentials_path)
        self.playlist_cache_path = Path(playlist_cache_path)
        self.logger = logging.getLogger(__name__)
        self.youtube = None
        self.playlists_cache = self._load_playlist_cache()

    def _load_playlist_cache(self) -> dict:
        """Load cached playlist IDs"""
        if self.playlist_cache_path.exists():
            try:
                with open(self.playlist_cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load playlist cache: {e}")
        return {}

    def _save_playlist_cache(self):
        """Save playlist IDs to cache"""
        try:
            self.playlist_cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.playlist_cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.playlists_cache, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save playlist cache: {e}")

    def authenticate(self):
        """Authenticate with YouTube API"""
        try:
            if build is None:
                self.logger.error("google-api-python-client not installed")
                return False

            # Load credentials (should be already authenticated via youtube_uploader)
            if not self.credentials_path.exists():
                self.logger.error(f"Credentials not found: {self.credentials_path}")
                return False

            import pickle
            with open(self.credentials_path, 'rb') as f:
                creds = pickle.load(f)

            self.youtube = build('youtube', 'v3', credentials=creds)
            self.logger.info("✅ Authenticated with YouTube API")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to authenticate: {e}")
            return False

    def get_or_create_playlist(
        self,
        category: str,
        privacy_status: str = "public"
    ) -> Optional[str]:
        """
        Get existing playlist ID or create new playlist for category

        Args:
            category: Video category
            privacy_status: Playlist privacy (public, unlisted, private)

        Returns:
            Playlist ID or None if failed
        """
        if not self.youtube:
            if not self.authenticate():
                return None

        # Check cache first
        if category in self.playlists_cache:
            playlist_id = self.playlists_cache[category]
            if self._playlist_exists(playlist_id):
                return playlist_id

        # Get playlist definition
        playlist_def = self.PLAYLIST_DEFINITIONS.get(category)
        if not playlist_def:
            self.logger.warning(f"No playlist definition for category: {category}")
            return None

        try:
            # Create playlist
            request = self.youtube.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": playlist_def['title'],
                        "description": playlist_def['description'],
                        "tags": playlist_def['tags']
                    },
                    "status": {
                        "privacyStatus": privacy_status
                    }
                }
            )

            response = request.execute()
            playlist_id = response['id']

            # Cache the playlist ID
            self.playlists_cache[category] = playlist_id
            self._save_playlist_cache()

            self.logger.info(f"✅ Created playlist: {playlist_def['title']} ({playlist_id})")
            return playlist_id

        except Exception as e:
            self.logger.error(f"❌ Failed to create playlist: {e}")
            return None

    def add_video_to_playlist(
        self,
        video_id: str,
        category: str
    ) -> bool:
        """
        Add video to its category playlist

        Args:
            video_id: YouTube video ID
            category: Video category

        Returns:
            True if successful
        """
        playlist_id = self.get_or_create_playlist(category)
        if not playlist_id:
            return False

        try:
            request = self.youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            )

            request.execute()
            self.logger.info(f"✅ Added video to playlist: {video_id} → {playlist_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to add video to playlist: {e}")
            return False

    def organize_video(
        self,
        video_id: str,
        category: str,
        age_group: Optional[str] = None
    ) -> bool:
        """
        Add video to category playlist and age-specific playlist

        Args:
            video_id: YouTube video ID
            category: Video category
            age_group: Age group (e.g., "2-3", "4-5", "5-6")

        Returns:
            True if successful
        """
        success = True

        # Add to category playlist
        if not self.add_video_to_playlist(video_id, category):
            success = False

        # Add to age-specific playlist if applicable
        if age_group and age_group in self.AGE_PLAYLISTS:
            age_playlist_id = self._get_or_create_age_playlist(age_group)
            if age_playlist_id:
                try:
                    request = self.youtube.playlistItems().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "playlistId": age_playlist_id,
                                "resourceId": {
                                    "kind": "youtube#video",
                                    "videoId": video_id
                                }
                            }
                        }
                    )
                    request.execute()
                    self.logger.info(f"✅ Added to age playlist: {video_id} → {age_group}")
                except Exception as e:
                    self.logger.error(f"Failed to add to age playlist: {e}")
                    success = False

        return success

    def _get_or_create_age_playlist(self, age_group: str) -> Optional[str]:
        """Get or create age-specific playlist"""
        cache_key = f"age_{age_group}"

        if cache_key in self.playlists_cache:
            playlist_id = self.playlists_cache[cache_key]
            if self._playlist_exists(playlist_id):
                return playlist_id

        age_def = self.AGE_PLAYLISTS.get(age_group)
        if not age_def:
            return None

        try:
            request = self.youtube.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": age_def['title'],
                        "description": age_def['description']
                    },
                    "status": {
                        "privacyStatus": "public"
                    }
                }
            )

            response = request.execute()
            playlist_id = response['id']

            self.playlists_cache[cache_key] = playlist_id
            self._save_playlist_cache()

            return playlist_id

        except Exception as e:
            self.logger.error(f"Failed to create age playlist: {e}")
            return None

    def _playlist_exists(self, playlist_id: str) -> bool:
        """Check if playlist still exists"""
        try:
            request = self.youtube.playlists().list(
                part="id",
                id=playlist_id
            )
            response = request.execute()
            return len(response.get('items', [])) > 0
        except:
            return False

    def list_all_playlists(self) -> dict:
        """List all managed playlists"""
        return self.playlists_cache.copy()


def main():
    """Test playlist manager"""
    logging.basicConfig(level=logging.INFO)

    manager = PlaylistManager()

    if manager.authenticate():
        # Create all category playlists
        print("\n📚 Creating playlists for all categories...\n")
        for category in PlaylistManager.PLAYLIST_DEFINITIONS.keys():
            playlist_id = manager.get_or_create_playlist(category)
            if playlist_id:
                print(f"✅ {category}: {playlist_id}")

        print("\n📋 All playlists:")
        for key, playlist_id in manager.list_all_playlists().items():
            print(f"  {key}: {playlist_id}")
    else:
        print("❌ Failed to authenticate with YouTube")


if __name__ == "__main__":
    main()
