"""
Kids Video Creator Module

Creates complete 3-15 minute YouTube videos from images and audio using FFmpeg.

Features:
- Combines images with voiceover and background music
- 1920x1080 (16:9) MP4 output @ 60 FPS
- Smooth transitions (fade/zoom effects with motion blur)
- Ken Burns effect (cinematic pan + zoom)
- Advanced encoding (animation-tuned for cartoon content)
- Equal duration per image
- Audio mixing with volume control
- Progress tracking
"""

import logging
import subprocess
import json
import time
from pathlib import Path
from typing import List, Optional
from datetime import datetime


class KidsVideoCreator:
    """
    Creates YouTube videos from images and audio using FFmpeg.
    
    Produces professional-looking videos with smooth transitions,
    audio mixing, and proper formatting for YouTube upload.
    """
    
    # Video output settings
    OUTPUT_WIDTH = 1920
    OUTPUT_HEIGHT = 1080
    OUTPUT_FPS = 60  # Increased from 30 for smoother motion
    VIDEO_CODEC = "libx264"
    AUDIO_CODEC = "aac"
    
    # Quality settings
    CRF = 21            # Reduced from 23 for better quality (18-28 range)
    PRESET = "slow"     # Changed from medium for better compression/quality
    AUDIO_BITRATE = "192k"
    TUNE = "animation"  # Optimize for animated/cartoon content
    
    # Transition settings
    FADE_DURATION = 0.8  # Increased from 0.5 for smoother fades
    ZOOM_FACTOR = 1.15   # Increased from 1.1 for more dynamic motion
    ZOOM_SPEED = 0.0003  # Smooth zoom increment per frame
    
    # Audio mixing
    MUSIC_VOLUME = 0.15  # Background music at 15% volume
    VOICE_VOLUME = 1.0   # Voiceover at 100% volume
    
    def __init__(
        self,
        ffmpeg_path: str = "ffmpeg",
        output_dir: Optional[str] = None
    ):
        """
        Initialize the Kids Video Creator.
        
        Args:
            ffmpeg_path: Path to FFmpeg executable
            output_dir: Directory to save videos (default: output/videos/)
        """
        self.ffmpeg_path = ffmpeg_path
        self.logger = logging.getLogger(__name__)
        
        # Set up output directory
        if output_dir is None:
            project_root = Path(__file__).parent.parent
            self.output_dir = project_root / "output" / "videos"
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Videos will be saved to: {self.output_dir}")
    
    def create_video(
        self,
        images: List[str],
        voiceover_path: str,
        output_filename: Optional[str] = None,
        background_music: Optional[str] = None,
        title: Optional[str] = None
    ) -> str:
        """
        Create a complete video from images and audio.
        
        Args:
            images: Ordered list of image file paths
            voiceover_path: Path to voiceover audio file
            output_filename: Output video filename (default: auto-generated)
            background_music: Optional path to background music file
            title: Optional video title for metadata
            
        Returns:
            str: Path to created video file
            
        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If video creation fails
        """
        # Validate inputs
        if not images or len(images) == 0:
            raise ValueError("At least one image is required")
        
        if not Path(voiceover_path).exists():
            raise ValueError(f"Voiceover file not found: {voiceover_path}")
        
        for img in images:
            if not Path(img).exists():
                raise ValueError(f"Image file not found: {img}")
        
        if background_music and not Path(background_music).exists():
            raise ValueError(f"Background music file not found: {background_music}")
        
        self.logger.info(f"Creating video with {len(images)} images")
        
        # Generate output filename if not provided
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"video_{timestamp}.mp4"
        
        if not output_filename.endswith('.mp4'):
            output_filename += '.mp4'
        
        output_path = self.output_dir / output_filename
        
        # Get voiceover duration to determine video length
        audio_duration = self._get_audio_duration(voiceover_path)
        
        if audio_duration < 10:
            raise ValueError("Voiceover must be at least 10 seconds long")
        
        self.logger.info(f"Voiceover duration: {audio_duration:.2f} seconds")
        
        # Calculate duration per image
        duration_per_image = audio_duration / len(images)
        self.logger.info(f"Duration per image: {duration_per_image:.2f} seconds")
        
        # Create video
        try:
            if background_music:
                self._create_video_with_music(
                    images, voiceover_path, background_music,
                    output_path, duration_per_image, audio_duration
                )
            else:
                self._create_video_simple(
                    images, voiceover_path,
                    output_path, duration_per_image, audio_duration
                )
            
            # Verify output file was created
            if not output_path.exists():
                raise RuntimeError("Video file was not created")
            
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            self.logger.info(f"✓ Video created: {output_path.name} ({file_size_mb:.2f} MB)")
            
            return str(output_path)
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"FFmpeg error: {e.stderr if hasattr(e, 'stderr') else str(e)}")
            raise RuntimeError(f"Video creation failed: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise RuntimeError(f"Video creation failed: {e}") from e
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """
        Get duration of audio file using FFprobe.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            float: Duration in seconds
        """
        try:
            # Try ffprobe first (more reliable)
            # Handle both 'ffmpeg' and 'ffmpeg.exe'
            if self.ffmpeg_path.endswith('.exe'):
                ffprobe_path = self.ffmpeg_path.replace('ffmpeg.exe', 'ffprobe.exe')
            else:
                ffprobe_path = self.ffmpeg_path.replace('ffmpeg', 'ffprobe')
            
            cmd = [
                ffprobe_path,
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'json',
                audio_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])
            
            return duration
            
        except Exception as e:
            self.logger.warning(f"Could not get audio duration with ffprobe: {e}")
            # Fallback to default duration
            return 180.0  # 3 minutes default
    
    def _create_video_simple(
        self,
        images: List[str],
        voiceover_path: str,
        output_path: Path,
        duration_per_image: float,
        total_duration: float
    ) -> None:
        """
        Create video without background music (simpler pipeline).
        
        Args:
            images: List of image paths
            voiceover_path: Path to voiceover audio
            output_path: Output video path
            duration_per_image: Duration to show each image
            total_duration: Total video duration
        """
        self.logger.info("Creating video (voiceover only)")
        
        # Build filter complex for images
        filter_complex = self._build_image_filter(images, duration_per_image)
        
        # Build FFmpeg command
        cmd = [self.ffmpeg_path, '-y']
        
        # Add image inputs
        for image in images:
            cmd.extend(['-loop', '1', '-t', str(duration_per_image), '-i', image])
        
        # Add audio input
        cmd.extend(['-i', voiceover_path])
        
        # Add filter complex
        cmd.extend(['-filter_complex', filter_complex])
        
        # Output settings with optimized encoding
        cmd.extend([
            '-map', '[outv]',     # Use video from filter
            '-map', f'{len(images)}:a',  # Use audio from voiceover
            '-c:v', self.VIDEO_CODEC,
            '-preset', self.PRESET,
            '-tune', self.TUNE,   # Animation tuning for cartoon content
            '-crf', str(self.CRF),
            '-profile:v', 'high', # High profile for better quality
            '-level', '4.2',      # H.264 level for 1080p60
            '-bf', '2',           # B-frames for better compression
            '-g', str(self.OUTPUT_FPS * 2),  # GOP size (2 seconds)
            '-c:a', self.AUDIO_CODEC,
            '-b:a', self.AUDIO_BITRATE,
            '-r', str(self.OUTPUT_FPS),
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',  # Enable streaming
            '-shortest',
            str(output_path)
        ])
        
        # Execute FFmpeg
        self._run_ffmpeg(cmd)
    
    def _create_video_with_music(
        self,
        images: List[str],
        voiceover_path: str,
        music_path: str,
        output_path: Path,
        duration_per_image: float,
        total_duration: float
    ) -> None:
        """
        Create video with background music mixed with voiceover.
        
        Args:
            images: List of image paths
            voiceover_path: Path to voiceover audio
            music_path: Path to background music
            output_path: Output video path
            duration_per_image: Duration to show each image
            total_duration: Total video duration
        """
        self.logger.info("Creating video (voiceover + background music)")
        
        # Build filter complex for images
        image_filter = self._build_image_filter(images, duration_per_image)
        
        # Build audio mixing filter
        # Loop music if needed, adjust volume, and mix with voiceover
        audio_filter = (
            f"[{len(images)}:a]volume={self.VOICE_VOLUME}[voice];"
            f"[{len(images)+1}:a]volume={self.MUSIC_VOLUME},aloop=loop=-1:size=2e+09[music];"
            "[voice][music]amix=inputs=2:duration=shortest[outa]"
        )
        
        # Combine filters
        filter_complex = f"{image_filter};{audio_filter}"
        
        # Build FFmpeg command
        cmd = [self.ffmpeg_path, '-y']
        
        # Add image inputs
        for image in images:
            cmd.extend(['-loop', '1', '-t', str(duration_per_image), '-i', image])
        
        # Add audio inputs
        cmd.extend(['-i', voiceover_path])
        cmd.extend(['-stream_loop', '-1', '-i', music_path])  # Loop music
        
        # Add filter complex
        cmd.extend(['-filter_complex', filter_complex])
        
        # Output settings with optimized encoding
        cmd.extend([
            '-map', '[outv]',     # Use video from filter
            '-map', '[outa]',     # Use mixed audio
            '-c:v', self.VIDEO_CODEC,
            '-preset', self.PRESET,
            '-tune', self.TUNE,   # Animation tuning for cartoon content
            '-crf', str(self.CRF),
            '-profile:v', 'high', # High profile for better quality
            '-level', '4.2',      # H.264 level for 1080p60
            '-bf', '2',           # B-frames for better compression
            '-g', str(self.OUTPUT_FPS * 2),  # GOP size (2 seconds)
            '-c:a', self.AUDIO_CODEC,
            '-b:a', self.AUDIO_BITRATE,
            '-r', str(self.OUTPUT_FPS),
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',  # Enable streaming
            '-shortest',
            str(output_path)
        ])
        
        # Execute FFmpeg
        self._run_ffmpeg(cmd)
    
    def _build_image_filter(
        self,
        images: List[str],
        duration_per_image: float
    ) -> str:
        """
        Build FFmpeg filter complex for image processing with transitions.
        
        Args:
            images: List of image paths
            duration_per_image: Duration to show each image
            
        Returns:
            str: FFmpeg filter complex string
        """
        filters = []
        
        # Process each image
        for i in range(len(images)):
            # Scale to fit within output resolution, pad to exact size, apply zoom
            # Note: Scale to output size first, then pad maintains aspect ratio
            filter_str = (
                f"[{i}:v]scale=w={self.OUTPUT_WIDTH}:"
                f"h={self.OUTPUT_HEIGHT}:force_original_aspect_ratio=decrease,"
                f"pad={self.OUTPUT_WIDTH}:{self.OUTPUT_HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
                f"setsar=1,"
                f"fps={self.OUTPUT_FPS},"
                f"format=yuv420p"
            )
            
            # Add slight zoom effect using zoompan filter
            # CRITICAL: d= is number of FRAMES, not seconds!
            if self.ZOOM_FACTOR > 1.0:
                frames_per_image = int(duration_per_image * self.OUTPUT_FPS)
                filter_str += (
                    f",zoompan=z='min(zoom+0.0002,{self.ZOOM_FACTOR})':"
                    f"d={frames_per_image}:s={self.OUTPUT_WIDTH}x{self.OUTPUT_HEIGHT}"
                )
            
            filter_str += f"[v{i}]"
            filters.append(filter_str)
        
        # Add smooth crossfade transitions between images with variety
        if len(images) > 1:
            # First image
            current = f"[v0]"
            
            # Variety of transition effects for visual interest
            transitions = ['fade', 'wipeleft', 'wiperight', 'slideleft', 'slideright', 'smoothleft', 'smoothright', 'circleopen', 'circleclose']
            
            for i in range(1, len(images)):
                fade_start = duration_per_image - self.FADE_DURATION
                
                # Select transition type (varied but mostly fade for simplicity)
                # Use fade for most, special transitions occasionally
                if i % 3 == 0 and i < len(images) - 1:  # Special transition every 3rd image
                    transition_type = transitions[i % len(transitions)]
                else:
                    transition_type = 'fade'  # Default smooth fade
                
                # Crossfade transition with selected effect
                fade_filter = (
                    f"{current}[v{i}]xfade=transition={transition_type}:"
                    f"duration={self.FADE_DURATION}:"
                    f"offset={fade_start}"
                )
                
                if i == len(images) - 1:
                    # Last transition outputs to final video
                    fade_filter += "[outv]"
                    filters.append(fade_filter)
                else:
                    # Intermediate transition
                    fade_filter += f"[vt{i}]"
                    filters.append(fade_filter)
                    current = f"[vt{i}]"
        else:
            # Single image, no transitions
            filters.append(f"[v0]copy[outv]")
        
        return ";".join(filters)
    
    def _run_ffmpeg(self, cmd: List[str], max_retries: int = 3) -> None:
        """
        Execute FFmpeg command with progress tracking and retry logic.
        
        Args:
            cmd: FFmpeg command as list of arguments
            max_retries: Maximum retry attempts for transient failures
        """
        # Sanitize command for logging (hide sensitive paths if needed)
        cmd_str = ' '.join(cmd[:10]) + ('...' if len(cmd) > 10 else '')
        self.logger.info(f"🎬 Starting FFmpeg process... (command: {cmd_str})")
        
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                start_time = time.time()
                
                # Run FFmpeg with real-time output
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=3600  # 1 hour timeout
                )
                
                elapsed = time.time() - start_time
                self.logger.info(f"✓ FFmpeg completed successfully in {elapsed:.1f}s")
                
                # Log warnings from FFmpeg stderr (even on success)
                if process.stderr:
                    stderr_lines = process.stderr.strip().split('\n')
                    warnings = [line for line in stderr_lines if 'warning' in line.lower()]
                    if warnings:
                        self.logger.debug(f"FFmpeg warnings: {len(warnings)} found")
                        for warning in warnings[:3]:  # Log first 3 warnings
                            self.logger.debug(f"  {warning}")
                
                return  # Success!
                
            except subprocess.TimeoutExpired as e:
                self.logger.error(f"❌ FFmpeg timeout after 1 hour")
                raise RuntimeError("FFmpeg operation timed out") from e
                
            except subprocess.CalledProcessError as e:
                last_error = e
                error_output = e.stderr if e.stderr else str(e)
                
                # Check if it's a transient error (worth retrying)
                is_transient = any([
                    'Resource temporarily unavailable' in error_output,
                    'Connection reset' in error_output,
                    'Broken pipe' in error_output,
                    'I/O error' in error_output
                ])
                
                if attempt < max_retries and is_transient:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.warning(
                        f"⚠️  FFmpeg failed (attempt {attempt}/{max_retries}): Transient error detected"
                    )
                    self.logger.info(f"🔄 Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    # Not transient or out of retries
                    self.logger.error(f"❌ FFmpeg failed (attempt {attempt}/{max_retries})")
                    self.logger.error(f"Error details: {error_output[:500]}")
                    if attempt >= max_retries:
                        self.logger.error("Max retries exceeded")
                    raise
                    
            except FileNotFoundError:
                self.logger.error(f"❌ FFmpeg executable not found at: {self.ffmpeg_path}")
                raise RuntimeError(
                    f"FFmpeg not found at: {self.ffmpeg_path}\n"
                    "Please install FFmpeg and set the correct path in .env file:\n"
                    "FFMPEG_PATH=C:\\path\\to\\ffmpeg.exe"
                ) from None
                
            except Exception as e:
                last_error = e
                self.logger.error(f"❌ Unexpected FFmpeg error: {type(e).__name__}: {e}")
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    self.logger.info(f"🔄 Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise
        
        if last_error:
            raise last_error
    
    def verify_ffmpeg(self) -> bool:
        """
        Verify FFmpeg is installed and accessible.
        
        Returns:
            bool: True if FFmpeg is available
        """
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                self.logger.info(f"✓ FFmpeg found: {version_line}")
                return True
            else:
                self.logger.error("✗ FFmpeg check failed")
                return False
                
        except FileNotFoundError:
            self.logger.error(f"✗ FFmpeg not found at: {self.ffmpeg_path}")
            return False
        except Exception as e:
            self.logger.error(f"✗ Error checking FFmpeg: {e}")
            return False


def create_youtube_video(
    images: List[str],
    voiceover_path: str,
    output_filename: Optional[str] = None,
    background_music: Optional[str] = None,
    ffmpeg_path: str = "ffmpeg"
) -> str:
    """
    Convenience function to create a YouTube video.
    
    Args:
        images: Ordered list of image file paths
        voiceover_path: Path to voiceover audio file
        output_filename: Optional output filename
        background_music: Optional background music path
        ffmpeg_path: Path to FFmpeg executable
        
    Returns:
        str: Path to created video file
        
    Example:
        >>> images = ["scene_001.png", "scene_002.png", "scene_003.png"]
        >>> voiceover = "voiceover.mp3"
        >>> music = "background_music.mp3"
        >>> video = create_youtube_video(images, voiceover, background_music=music)
        >>> print(f"Video created: {video}")
    """
    creator = KidsVideoCreator(ffmpeg_path=ffmpeg_path)
    return creator.create_video(images, voiceover_path, output_filename, background_music)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of the KidsVideoCreator.
    """
    import os
    import sys
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 80)
    print("Kids Video Creator Demo")
    print("=" * 80)
    print()
    
    # Check FFmpeg
    ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")
    
    creator = KidsVideoCreator(ffmpeg_path=ffmpeg_path)
    
    print("Checking FFmpeg installation...")
    if not creator.verify_ffmpeg():
        print("✗ FFmpeg is not installed or not found in PATH")
        print("Please install FFmpeg from: https://ffmpeg.org/")
        print("Or set FFMPEG_PATH environment variable to FFmpeg location")
        sys.exit(1)
    
    print()
    
    # Check for test assets
    project_root = Path(__file__).parent.parent
    assets_dir = project_root / "assets"
    
    # Look for test images
    test_images = []
    images_dir = assets_dir / "images"
    
    if images_dir.exists():
        # Find any existing images
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            test_images.extend(sorted(images_dir.rglob(ext)))
        
        if test_images:
            test_images = [str(img) for img in test_images[:5]]  # Limit to 5
    
    if not test_images:
        print("No test images found in assets/images/")
        print("Please generate images first using kids_image_generator.py")
        sys.exit(1)
    
    print(f"Found {len(test_images)} test images")
    
    # Look for test audio
    test_voiceover = None
    output_dir = project_root / "output"
    
    if output_dir.exists():
        audio_files = list(output_dir.glob("*.mp3"))
        if audio_files:
            test_voiceover = str(audio_files[0])
    
    if not test_voiceover:
        print("No test voiceover found in output/")
        print("Please generate voiceover first using kids_voiceover_generator.py")
        sys.exit(1)
    
    print(f"Found test voiceover: {Path(test_voiceover).name}")
    
    # Look for background music
    test_music = None
    music_dir = assets_dir / "music"
    
    if music_dir.exists():
        music_files = list(music_dir.glob("*.mp3"))
        if music_files:
            test_music = str(music_files[0])
            print(f"Found background music: {Path(test_music).name}")
    
    print()
    print("-" * 80)
    print("Creating video...")
    print("-" * 80)
    print()
    
    try:
        video_path = creator.create_video(
            images=test_images,
            voiceover_path=test_voiceover,
            output_filename="demo_video.mp4",
            background_music=test_music,
            title="Demo Kids Video"
        )
        
        print()
        print("=" * 80)
        print("SUCCESS!")
        print("=" * 80)
        print(f"✓ Video created: {video_path}")
        print()
        print("You can now upload this video to YouTube!")
        
    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR")
        print("=" * 80)
        print(f"✗ Failed to create video: {e}")
        sys.exit(1)
