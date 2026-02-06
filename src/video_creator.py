"""
Video Creator Module

Uses FFmpeg to compile all assets into a final video file.
Combines images, voiceover, transitions, and background music.
"""

import logging
import subprocess
from typing import Dict, Any, List
from pathlib import Path


class VideoCreator:
    """Creates video files using FFmpeg from script and assets."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the VideoCreator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger("YouTubeAutomation.VideoCreator")
        self.ffmpeg_path = config['paths']['ffmpeg_path']
        self.output_dir = Path(config['paths']['output_dir'])
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_video(self, script: Dict[str, Any], assets: Dict[str, Any]) -> str:
        """
        Create video from script and assets using FFmpeg.
        
        Args:
            script: Script dictionary
            assets: Assets dictionary with paths to images, audio, etc.
            
        Returns:
            Path to created video file
        """
        
        self.logger.info("Creating video with FFmpeg...")
        
        # Generate output filename
        timestamp = script['topic'].get('timestamp', '').replace(':', '-').split('.')[0]
        output_filename = f"video_{timestamp}.mp4"
        output_path = self.output_dir / output_filename
        
        try:
            # Create video using FFmpeg
            # Strategy: Create video from images with slide durations, then merge with audio
            
            # Step 1: Create input file list for FFmpeg
            input_list_path = self._create_ffmpeg_input_list(script, assets)
            
            # Step 2: Build FFmpeg command
            ffmpeg_cmd = self._build_ffmpeg_command(
                input_list_path,
                assets['voiceover_path'],
                assets.get('music_path'),
                output_path
            )
            
            # Step 3: Execute FFmpeg
            self._execute_ffmpeg(ffmpeg_cmd)
            
            self.logger.info(f"Video created successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error creating video: {e}")
            raise
    
    def _create_ffmpeg_input_list(self, script: Dict[str, Any], assets: Dict[str, Any]) -> str:
        """
        Create FFmpeg concat demuxer input file.
        
        Args:
            script: Script dictionary with scene durations
            assets: Assets dictionary with image paths
            
        Returns:
            Path to input list file
        """
        
        input_list = []
        
        for idx, scene in enumerate(script['scenes']):
            image_path = assets['images'][idx] if idx < len(assets['images']) else None
            
            if image_path and Path(image_path).exists():
                duration = scene.get('duration_seconds', 15)
                
                # FFmpeg concat format
                input_list.append(f"file '{image_path}'")
                input_list.append(f"duration {duration}")
        
        # Repeat last file (FFmpeg concat demuxer requirement)
        if input_list:
            last_file = input_list[-2]  # Get the last "file" line
            input_list.append(last_file)
        
        # Write to temporary file
        input_list_path = self.output_dir / "_ffmpeg_input_list.txt"
        
        with open(input_list_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(input_list))
        
        return str(input_list_path)
    
    def _build_ffmpeg_command(
        self,
        input_list_path: str,
        voiceover_path: str,
        music_path: str,
        output_path: Path
    ) -> List[str]:
        """
        Build FFmpeg command for video creation.
        
        Args:
            input_list_path: Path to FFmpeg input list file
            voiceover_path: Path to voiceover audio
            music_path: Path to background music (optional)
            output_path: Path for output video
            
        Returns:
            List of command arguments
        """
        
        resolution = self.config['video']['resolution']
        fps = self.config['video']['fps']
        
        cmd = [
            self.ffmpeg_path,
            '-f', 'concat',
            '-safe', '0',
            '-i', input_list_path,  # Input images
            '-i', voiceover_path,    # Voiceover audio
        ]
        
        # Add background music if available
        if music_path and Path(music_path).exists():
            cmd.extend(['-i', music_path])
            
            # Mix audio: voiceover at 100%, music at 20% volume
            filter_complex = (
                '[1:a]volume=1.0[voice];'
                '[2:a]volume=0.2[music];'
                '[voice][music]amix=inputs=2:duration=shortest[aout]'
            )
            cmd.extend([
                '-filter_complex', filter_complex,
                '-map', '0:v',
                '-map', '[aout]'
            ])
        else:
            # Just use voiceover
            cmd.extend([
                '-map', '0:v',
                '-map', '1:a'
            ])
        
        # Video encoding settings
        cmd.extend([
            '-c:v', self.config['video']['video_codec'],
            '-preset', 'medium',
            '-crf', '23',
            '-s', resolution,
            '-r', str(fps),
            '-pix_fmt', 'yuv420p',
            '-c:a', self.config['video']['audio_codec'],
            '-b:a', '192k',
            '-shortest',  # End video when shortest stream ends (audio)
            '-y',  # Overwrite output file
            str(output_path)
        ])
        
        return cmd
    
    def _execute_ffmpeg(self, cmd: List[str]) -> None:
        """
        Execute FFmpeg command.
        
        Args:
            cmd: FFmpeg command as list of arguments
        """
        
        self.logger.debug(f"Executing FFmpeg command: {' '.join(cmd)}")
        
        try:
            # Execute FFmpeg
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            self.logger.debug("FFmpeg execution completed")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"FFmpeg error: {e.stderr}")
            raise RuntimeError(f"FFmpeg failed: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                f"FFmpeg not found at {self.ffmpeg_path}. "
                "Please install FFmpeg and update config.yaml with the correct path."
            )
