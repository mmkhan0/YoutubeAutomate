"""
Pexels Video Fetcher Module

Fetches free stock videos from Pexels API with actual movement and animation.
Perfect for kids educational content with real animals, people, and scenes.

Provides:
- Search videos by keyword
- Download HD video clips
- Filter by duration and orientation
- Automatic video selection
"""

import logging
import requests
from pathlib import Path
from typing import List, Optional, Dict, Any
import time


class PexelsVideoFetcher:
    """
    Fetches free stock videos from Pexels API.

    Provides real video clips with movement instead of static images.
    Perfect for educational content showing animals, people, nature, etc.
    """

    API_BASE_URL = "https://api.pexels.com/videos"

    def __init__(self, api_key: str, output_dir: Optional[str] = None):
        """
        Initialize Pexels Video Fetcher.

        Args:
            api_key: Pexels API key (free from pexels.com)
            output_dir: Directory to save videos (default: output/videos/clips/)
        """
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)

        # Set up output directory
        if output_dir is None:
            project_root = Path(__file__).parent.parent
            self.output_dir = project_root / "output" / "videos" / "clips"
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Request headers
        self.headers = {
            "Authorization": api_key
        }

        self.logger.info("Pexels Video Fetcher initialized")

    def search_videos(
        self,
        query: str,
        per_page: int = 5,
        orientation: str = "landscape",
        size: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Search for videos on Pexels.

        Args:
            query: Search keywords (e.g., "cow walking", "children playing")
            per_page: Number of results (max 80)
            orientation: 'landscape', 'portrait', or 'square'
            size: 'small', 'medium', 'large'

        Returns:
            List of video metadata dictionaries
        """
        self.logger.info(f"Searching Pexels for: '{query}'")

        params = {
            "query": query,
            "per_page": per_page,
            "orientation": orientation,
            "size": size
        }

        try:
            response = requests.get(
                f"{self.API_BASE_URL}/search",
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            videos = data.get("videos", [])

            self.logger.info(f"Found {len(videos)} videos for '{query}'")
            return videos

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Pexels API error: {e}")
            return []

    def download_video(
        self,
        video_data: Dict[str, Any],
        filename: Optional[str] = None,
        quality: str = "hd"
    ) -> Optional[str]:
        """
        Download a video from Pexels.

        Args:
            video_data: Video metadata from search_videos()
            filename: Output filename (default: pexels_<id>.mp4)
            quality: 'hd', 'sd', or 'uhd' (if available)

        Returns:
            Path to downloaded video file, or None if failed
        """
        try:
            # Find best quality video file
            video_files = video_data.get("video_files", [])

            if not video_files:
                self.logger.warning(f"No video files found for video {video_data.get('id')}")
                return None

            # Filter by quality
            quality_map = {
                "uhd": "uhd",
                "hd": "hd",
                "sd": "sd"
            }

            target_quality = quality_map.get(quality, "hd")

            # Try to find requested quality
            video_url = None
            for vf in video_files:
                quality_str = vf.get('quality', '')
                if quality_str and target_quality in quality_str.lower():
                    video_url = vf.get("link")
                    break

            # Fallback to any available video
            if not video_url and video_files:
                video_url = video_files[0].get("link")

            if not video_url:
                self.logger.error("No video URL found")
                return None

            # Generate filename
            if filename is None:
                video_id = video_data.get("id", "unknown")
                filename = f"pexels_{video_id}.mp4"

            if not filename.endswith('.mp4'):
                filename += '.mp4'

            output_path = self.output_dir / filename

            # Download video
            self.logger.info(f"Downloading video from Pexels...")

            response = requests.get(video_url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(output_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Progress feedback
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if progress % 25 < 1:  # Log at 25%, 50%, 75%, 100%
                                self.logger.debug(f"Download progress: {progress:.0f}%")

            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            self.logger.info(f"✓ Video downloaded: {filename} ({file_size_mb:.2f} MB)")

            return str(output_path)

        except Exception as e:
            self.logger.error(f"Error downloading video: {e}")
            return None

    def fetch_videos_for_script(
        self,
        script_sections: List[Dict[str, str]],
        max_per_section: int = 1
    ) -> List[str]:
        """
        Fetch videos for each section of a script.

        Args:
            script_sections: List of script sections with descriptions
            max_per_section: Number of videos per section

        Returns:
            List of downloaded video file paths
        """
        self.logger.info(f"Fetching videos for {len(script_sections)} script sections")

        video_paths = []

        for i, section in enumerate(script_sections):
            # Extract keywords from section description
            description = section.get("description", "")

            if not description:
                self.logger.warning(f"Section {i+1} has no description, skipping")
                continue

            # Search for videos
            videos = self.search_videos(description, per_page=max_per_section)

            if not videos:
                self.logger.warning(f"No videos found for: {description}")
                continue

            # Download first video
            video_data = videos[0]
            filename = f"section_{i+1:03d}.mp4"

            video_path = self.download_video(video_data, filename)

            if video_path:
                video_paths.append(video_path)

            # Rate limiting (Pexels: 200 requests/hour)
            time.sleep(0.5)

        self.logger.info(f"✓ Downloaded {len(video_paths)} videos")
        return video_paths


def get_video_clip(
    query: str,
    api_key: str,
    output_filename: Optional[str] = None
) -> Optional[str]:
    """
    Convenience function to fetch a single video clip.

    Args:
        query: Search query (e.g., "cow walking")
        api_key: Pexels API key
        output_filename: Optional output filename

    Returns:
        Path to downloaded video, or None if failed

    Example:
        >>> api_key = os.getenv("PEXELS_API_KEY")
        >>> video = get_video_clip("butterfly flying", api_key)
        >>> print(f"Downloaded: {video}")
    """
    fetcher = PexelsVideoFetcher(api_key)
    videos = fetcher.search_videos(query, per_page=1)

    if not videos:
        return None

    return fetcher.download_video(videos[0], output_filename)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of Pexels Video Fetcher.
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Get API key from environment
    api_key = os.getenv("PEXELS_API_KEY")

    if not api_key:
        print("❌ PEXELS_API_KEY not found in .env file")
        print("\n🔑 Get your FREE API key from: https://www.pexels.com/api/")
        exit(1)

    fetcher = PexelsVideoFetcher(api_key)

    # Example: Search and download a video
    print("\n🎬 Searching for 'cow walking' videos...")
    videos = fetcher.search_videos("cow walking", per_page=3)

    if videos:
        print(f"\n✓ Found {len(videos)} videos")

        # Download first video
        video = videos[0]
        print(f"\n📥 Downloading: {video.get('url')}")

        path = fetcher.download_video(video, "cow_walking_sample.mp4")

        if path:
            print(f"\n✓ Success! Video saved to: {path}")
        else:
            print("\n❌ Download failed")
    else:
        print("\n❌ No videos found")
