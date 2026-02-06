"""
YouTube Uploader Module

Uploads videos to YouTube using YouTube Data API v3 with OAuth2 authentication.

Features:
- OAuth Desktop authentication flow
- Resumable upload for large files
- Video metadata (title, description, tags)
- Made for Kids compliance
- Education category
- Progress tracking
- Error handling with retries
"""

import logging
import pickle
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


@dataclass
class UploadResult:
    """Result of video upload."""
    video_id: str
    video_url: str
    title: str
    privacy_status: str
    category_id: str
    made_for_kids: bool


class YouTubeUploader:
    """
    Uploads videos to YouTube with OAuth2 authentication.
    
    Handles authentication, resumable uploads, and video metadata
    for educational content targeted at children.
    """
    
    # OAuth 2.0 scopes for YouTube upload and playlist management
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube',
        'https://www.googleapis.com/auth/youtube.force-ssl'
    ]
    
    # YouTube API settings
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'
    
    # Video settings
    EDUCATION_CATEGORY_ID = "27"  # Education category
    DEFAULT_PRIVACY = "private"   # Start private for safety
    
    # Upload settings
    CHUNK_SIZE = 1024 * 1024 * 5  # 5 MB chunks for resumable upload
    MAX_RETRIES = 10
    RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
    
    def __init__(
        self,
        client_secrets_file: str,
        token_file: Optional[str] = None
    ):
        """
        Initialize the YouTube Uploader.
        
        Args:
            client_secrets_file: Path to OAuth client secrets JSON file
            token_file: Path to save/load OAuth token (default: same dir as secrets)
        """
        self.client_secrets_file = Path(client_secrets_file)
        
        if not self.client_secrets_file.exists():
            raise FileNotFoundError(
                f"Client secrets file not found: {client_secrets_file}\n"
                "Download it from Google Cloud Console:\n"
                "1. Go to https://console.cloud.google.com/\n"
                "2. Select your project\n"
                "3. Go to APIs & Services > Credentials\n"
                "4. Download OAuth 2.0 Client ID JSON"
            )
        
        # Set token file location
        if token_file is None:
            self.token_file = self.client_secrets_file.parent / "youtube_token.pickle"
        else:
            self.token_file = Path(token_file)
        
        self.credentials = None
        self.youtube = None
        self.logger = logging.getLogger(__name__)
    
    def authenticate(self) -> None:
        """
        Authenticate with YouTube using OAuth 2.0.
        
        Opens browser for user authorization on first run,
        then saves credentials for future use.
        """
        self.logger.info("Authenticating with YouTube...")
        
        # Load existing credentials if available
        if self.token_file.exists():
            try:
                with open(self.token_file, 'rb') as token:
                    self.credentials = pickle.load(token)
                self.logger.info("Loaded existing credentials")
            except Exception as e:
                self.logger.warning(f"Failed to load credentials: {e}")
                self.credentials = None
        
        # Refresh or obtain new credentials
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.logger.info("Refreshing access token...")
                try:
                    self.credentials.refresh(Request())
                    self.logger.info("✓ Token refreshed successfully")
                except Exception as e:
                    self.logger.warning(f"Token refresh failed: {e}")
                    self.credentials = None
            
            if not self.credentials:
                self.logger.info("Starting OAuth flow (browser will open)...")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.client_secrets_file),
                    self.SCOPES
                )
                
                # Run local server for OAuth callback
                # Port 0 = automatically select an available port
                self.credentials = flow.run_local_server(
                    port=0,
                    prompt='consent',
                    success_message='Authentication successful! You can close this window.'
                )
                
                self.logger.info("✓ Authentication successful")
            
            # Save credentials for future use
            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.credentials, token)
                self.logger.info(f"Credentials saved to {self.token_file}")
            except Exception as e:
                self.logger.warning(f"Failed to save credentials: {e}")
        
        # Build YouTube API client
        try:
            self.youtube = build(
                self.API_SERVICE_NAME,
                self.API_VERSION,
                credentials=self.credentials
            )
            self.logger.info("✓ YouTube API client ready")
        except Exception as e:
            raise RuntimeError(f"Failed to build YouTube API client: {e}") from e
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str],
        thumbnail_path: Optional[str] = None,
        privacy_status: str = DEFAULT_PRIVACY,
        made_for_kids: bool = True,
        category_id: str = EDUCATION_CATEGORY_ID,
        playlist_id: Optional[str] = None,
        publish_at: Optional[str] = None
    ) -> UploadResult:
        """
        Upload a video to YouTube with optional scheduled publishing.
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            thumbnail_path: Optional path to thumbnail image
            privacy_status: "private", "unlisted", or "public" (ignored if publish_at is set)
            made_for_kids: Whether video is made for kids (COPPA compliance)
            category_id: YouTube category ID (default: Education)
            playlist_id: Optional playlist ID to add video to
            publish_at: ISO 8601 datetime for scheduled publishing (e.g., "2023-06-15T12:30:00Z")
            
        Returns:
            UploadResult: Upload result with video ID and URL
            
        Raises:
            FileNotFoundError: If video file doesn't exist
            RuntimeError: If upload fails
        """
        # Validate inputs
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if not self.youtube:
            self.authenticate()
        
        self.logger.info(f"Uploading video: {video_path.name}")
        
        # Scheduled publishing requires private initial status
        if publish_at:
            self.logger.info(f"📅 Video will be published at: {publish_at}")
            actual_privacy = "private"
        else:
            actual_privacy = privacy_status
        
        # Prepare video metadata
        body = self._build_video_metadata(
            title, description, tags, actual_privacy, made_for_kids, category_id, publish_at
        )
        
        # Create media upload with resumable support
        media = MediaFileUpload(
            str(video_path),
            chunksize=self.CHUNK_SIZE,
            resumable=True,
            mimetype='video/*'
        )
        
        # Insert video
        try:
            insert_request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            video_id = self._execute_resumable_upload(insert_request)
            
            self.logger.info(f"✓ Video uploaded successfully: {video_id}")
            
            # Upload thumbnail if provided
            if thumbnail_path and Path(thumbnail_path).exists():
                self._upload_thumbnail(video_id, thumbnail_path)
            
            # Add to playlist if specified
            if playlist_id:
                self.add_video_to_playlist(video_id, playlist_id)
            
            # Create result
            result = UploadResult(
                video_id=video_id,
                video_url=f"https://www.youtube.com/watch?v={video_id}",
                title=title,
                privacy_status=privacy_status,
                category_id=category_id,
                made_for_kids=made_for_kids
            )
            
            return result
            
        except HttpError as e:
            self.logger.error(f"YouTube API error: {e}")
            raise RuntimeError(f"Upload failed: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error during upload: {e}")
            raise RuntimeError(f"Upload failed: {e}") from e
    
    def _build_video_metadata(
        self,
        title: str,
        description: str,
        tags: List[str],
        privacy_status: str,
        made_for_kids: bool,
        category_id: str,
        publish_at: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build video metadata for YouTube API.
        
        Args:
            title: Video title
            description: Video description
            tags: List of tags
            privacy_status: Privacy setting
            made_for_kids: Made for kids flag
            category_id: Category ID
            publish_at: Optional ISO 8601 datetime for scheduled publishing
            
        Returns:
            dict: Metadata body for API request
        """
        # Limit tags to YouTube's constraints
        # Max 500 characters total, max 30 chars per tag
        cleaned_tags = []
        total_length = 0
        
        for tag in tags:
            tag = tag.strip()[:30]  # Limit tag length
            if total_length + len(tag) + 1 <= 500:  # +1 for comma
                cleaned_tags.append(tag)
                total_length += len(tag) + 1
            
            if len(cleaned_tags) >= 15:  # Reasonable limit
                break
        
        body = {
            'snippet': {
                'title': title[:100],  # YouTube title limit
                'description': description[:5000],  # YouTube description limit
                'tags': cleaned_tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': made_for_kids
            }
        }
        
        # Add scheduled publishing if publish_at is provided
        if publish_at:
            body['status']['publishAt'] = publish_at
            # When scheduling, video must start private
            body['status']['privacyStatus'] = 'private'
        
        return body
    
    def _execute_resumable_upload(self, insert_request) -> str:
        """
        Execute resumable upload with retry logic and progress tracking.
        
        Args:
            insert_request: YouTube API insert request
            
        Returns:
            str: Uploaded video ID
        """
        response = None
        error = None
        retry = 0
        
        while response is None:
            try:
                self.logger.info(f"Uploading... (attempt {retry + 1})")
                status, response = insert_request.next_chunk()
                
                if status:
                    progress = int(status.progress() * 100)
                    self.logger.info(f"Upload progress: {progress}%")
                
            except HttpError as e:
                if e.resp.status in self.RETRIABLE_STATUS_CODES:
                    error = f"Retriable HTTP error {e.resp.status}: {e.content}"
                    self.logger.warning(error)
                else:
                    raise
            
            except Exception as e:
                error = f"Unexpected error: {e}"
                self.logger.warning(error)
            
            if error is not None:
                retry += 1
                
                if retry > self.MAX_RETRIES:
                    raise RuntimeError(f"Upload failed after {self.MAX_RETRIES} retries: {error}")
                
                # Exponential backoff
                delay = 2 ** retry
                self.logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                
                error = None
        
        return response['id']
    
    def _upload_thumbnail(self, video_id: str, thumbnail_path: str) -> None:
        """
        Upload custom thumbnail for video.
        
        Args:
            video_id: Video ID
            thumbnail_path: Path to thumbnail image
        """
        try:
            self.logger.info("Uploading thumbnail...")
            
            request = self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype='image/jpeg')
            )
            
            request.execute()
            self.logger.info("✓ Thumbnail uploaded successfully")
            
        except HttpError as e:
            self.logger.warning(f"Failed to upload thumbnail: {e}")
        except Exception as e:
            self.logger.warning(f"Thumbnail upload error: {e}")
    
    def add_video_to_playlist(self, video_id: str, playlist_id: str) -> bool:
        """
        Add a video to a YouTube playlist.
        
        Args:
            video_id: Video ID to add
            playlist_id: Playlist ID to add to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Adding video to playlist {playlist_id}...")
            
            request = self.youtube.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        }
                    }
                }
            )
            
            request.execute()
            self.logger.info(f"✓ Video added to playlist successfully")
            return True
            
        except HttpError as e:
            self.logger.error(f"Failed to add video to playlist: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error adding video to playlist: {e}")
            return False
    
    def create_playlist(self, title: str, description: str = "", privacy_status: str = "private") -> Optional[str]:
        """
        Create a new YouTube playlist.
        
        Args:
            title: Playlist title
            description: Playlist description
            privacy_status: "private", "unlisted", or "public"
            
        Returns:
            str: Playlist ID if successful, None otherwise
        """
        try:
            self.logger.info(f"Creating playlist: {title}")
            
            request = self.youtube.playlists().insert(
                part='snippet,status',
                body={
                    'snippet': {
                        'title': title,
                        'description': description
                    },
                    'status': {
                        'privacyStatus': privacy_status
                    }
                }
            )
            
            response = request.execute()
            playlist_id = response['id']
            
            self.logger.info(f"✓ Playlist created: {playlist_id}")
            self.logger.info(f"  URL: https://www.youtube.com/playlist?list={playlist_id}")
            
            return playlist_id
            
        except HttpError as e:
            self.logger.error(f"Failed to create playlist: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error creating playlist: {e}")
            return None
    
    def verify_authentication(self) -> bool:
        """
        Verify that authentication is working.
        
        Returns:
            bool: True if authenticated successfully
        """
        try:
            if not self.youtube:
                self.authenticate()
            
            # Try to list channels (simple test)
            request = self.youtube.channels().list(
                part='snippet',
                mine=True
            )
            
            response = request.execute()
            
            if 'items' in response and len(response['items']) > 0:
                channel_title = response['items'][0]['snippet']['title']
                self.logger.info(f"✓ Authenticated as: {channel_title}")
                return True
            else:
                self.logger.warning("✗ No channel found for authenticated user")
                return False
                
        except Exception as e:
            self.logger.error(f"✗ Authentication verification failed: {e}")
            return False


def upload_to_youtube(
    video_path: str,
    title: str,
    description: str,
    tags: List[str],
    client_secrets_file: str,
    thumbnail_path: Optional[str] = None,
    privacy_status: str = "private",
    made_for_kids: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to upload a video to YouTube.
    
    Args:
        video_path: Path to video file
        title: Video title
        description: Video description
        tags: List of tags
        client_secrets_file: Path to OAuth client secrets JSON
        thumbnail_path: Optional thumbnail image path
        privacy_status: "private", "unlisted", or "public"
        made_for_kids: Whether video is made for kids
        
    Returns:
        dict: Upload result with video_id and video_url
        
    Example:
        >>> result = upload_to_youtube(
        ...     video_path="video.mp4",
        ...     title="Amazing Science for Kids",
        ...     description="Learn about...",
        ...     tags=["kids", "education", "science"],
        ...     client_secrets_file="config/client_secrets.json"
        ... )
        >>> print(f"Uploaded: {result['video_url']}")
    """
    uploader = YouTubeUploader(client_secrets_file)
    result = uploader.upload_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        thumbnail_path=thumbnail_path,
        privacy_status=privacy_status,
        made_for_kids=made_for_kids
    )
    
    return {
        'video_id': result.video_id,
        'video_url': result.video_url,
        'title': result.title,
        'privacy_status': result.privacy_status,
        'made_for_kids': result.made_for_kids
    }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of the YouTubeUploader.
    """
    import sys
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 80)
    print("YouTube Uploader Demo")
    print("=" * 80)
    print()
    
    # Check for client secrets file
    project_root = Path(__file__).parent.parent
    client_secrets = project_root / "config" / "client_secrets.json"
    
    if not client_secrets.exists():
        print("✗ Client secrets file not found!")
        print(f"Expected location: {client_secrets}")
        print()
        print("To get your client secrets:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project (or select existing)")
        print("3. Enable YouTube Data API v3")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download JSON and save as client_secrets.json")
        sys.exit(1)
    
    print(f"✓ Found client secrets: {client_secrets}")
    print()
    
    # Create uploader
    uploader = YouTubeUploader(str(client_secrets))
    
    # Test authentication
    print("Testing authentication...")
    print("(Browser will open for first-time authorization)")
    print()
    
    try:
        if uploader.verify_authentication():
            print()
            print("=" * 80)
            print("SUCCESS!")
            print("=" * 80)
            print("✓ YouTube API authentication is working")
            print()
            print("You can now use this module to upload videos.")
            print()
            print("Example code:")
            print("-" * 80)
            print("""
uploader = YouTubeUploader("config/client_secrets.json")

result = uploader.upload_video(
    video_path="output/videos/my_video.mp4",
    title="Amazing Science Facts for Kids",
    description="Learn about science in this fun video!",
    tags=["science", "kids", "education"],
    thumbnail_path="output/thumbnails/thumbnail.jpg",
    privacy_status="private",
    made_for_kids=True
)

print(f"Video uploaded: {result.video_url}")
            """)
            print("-" * 80)
        else:
            print("✗ Authentication test failed")
            sys.exit(1)
            
    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR")
        print("=" * 80)
        print(f"✗ {e}")
        sys.exit(1)
