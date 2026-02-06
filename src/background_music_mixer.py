"""
Background Music Mixer for Kids Learning Videos
Adds royalty-free background music with volume ducking during narration
"""

from pathlib import Path
from typing import Optional, List
import subprocess
import logging
import json


class BackgroundMusicMixer:
    """Mix background music with video voiceover using FFmpeg"""

    # Royalty-free background music URLs (YouTube Audio Library)
    # These are placeholder URLs - you should download actual royalty-free music
    DEFAULT_MUSIC_TRACKS = {
        'upbeat_kids': 'upbeat_kids.mp3',
        'gentle_learning': 'gentle_learning.mp3',
        'playful_melody': 'playful_melody.mp3',
        'happy_piano': 'happy_piano.mp3',
        'cheerful_ukulele': 'cheerful_ukulele.mp3'
    }

    # Music settings for different categories
    CATEGORY_MUSIC_SETTINGS = {
        'english_alphabet': {'track': 'upbeat_kids', 'volume': 0.15},
        'hindi_alphabet': {'track': 'upbeat_kids', 'volume': 0.15},
        'numbers_counting': {'track': 'playful_melody', 'volume': 0.18},
        'colors_shapes': {'track': 'cheerful_ukulele', 'volume': 0.16},
        'fruits_vegetables': {'track': 'happy_piano', 'volume': 0.15},
        'animals_sounds': {'track': 'playful_melody', 'volume': 0.14},
        'simple_logic': {'track': 'gentle_learning', 'volume': 0.17},
        'body_parts': {'track': 'upbeat_kids', 'volume': 0.16},
        'daily_habits': {'track': 'gentle_learning', 'volume': 0.15},
        'emotions': {'track': 'gentle_learning', 'volume': 0.14},
        'basic_math': {'track': 'playful_melody', 'volume': 0.17},
        'rhymes_learning': {'track': 'cheerful_ukulele', 'volume': 0.18},
        'memory_games': {'track': 'upbeat_kids', 'volume': 0.16},
        'puzzle_games': {'track': 'playful_melody', 'volume': 0.17},
        'observation_games': {'track': 'upbeat_kids', 'volume': 0.16},
        'default': {'track': 'upbeat_kids', 'volume': 0.15}
    }

    def __init__(
        self,
        music_dir: str = "assets/music",
        output_dir: str = "output/audio",
        ffmpeg_path: str = "ffmpeg"
    ):
        """
        Initialize background music mixer

        Args:
            music_dir: Directory containing background music files
            output_dir: Directory for output audio files
            ffmpeg_path: Path to FFmpeg executable
        """
        self.music_dir = Path(music_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_path = ffmpeg_path
        self.logger = logging.getLogger(__name__)

        # Create music directory if it doesn't exist
        self.music_dir.mkdir(parents=True, exist_ok=True)

    def mix_audio_with_music(
        self,
        voiceover_path: str,
        output_path: str,
        category: str = "default",
        music_volume: Optional[float] = None,
        fade_in_duration: float = 2.0,
        fade_out_duration: float = 3.0,
        ducking_enabled: bool = True,
        ducking_amount: float = 0.4
    ) -> str:
        """
        Mix voiceover with background music using volume ducking

        Args:
            voiceover_path: Path to voiceover audio file
            output_path: Path for output mixed audio
            category: Video category (determines music track)
            music_volume: Background music volume (0.0-1.0), None for category default
            fade_in_duration: Music fade-in duration in seconds
            fade_out_duration: Music fade-out duration in seconds
            ducking_enabled: Enable volume ducking during narration
            ducking_amount: How much to reduce music during speech (0.0-1.0)

        Returns:
            Path to mixed audio file
        """
        try:
            # Get music settings for category
            settings = self.CATEGORY_MUSIC_SETTINGS.get(
                category,
                self.CATEGORY_MUSIC_SETTINGS['default']
            )

            # Get music track path
            music_track = settings['track']
            music_path = self.music_dir / self.DEFAULT_MUSIC_TRACKS[music_track]

            # Check if music file exists
            if not music_path.exists():
                self.logger.warning(
                    f"⚠️ Music file not found: {music_path}. "
                    "Skipping background music."
                )
                # Copy voiceover as-is if no music available
                import shutil
                shutil.copy2(voiceover_path, output_path)
                return output_path

            # Use category default volume if not specified
            if music_volume is None:
                music_volume = settings['volume']

            # Get voiceover duration
            duration = self._get_audio_duration(voiceover_path)

            if ducking_enabled:
                # Create complex filter with volume ducking
                mixed_audio = self._mix_with_ducking(
                    voiceover_path,
                    music_path,
                    output_path,
                    duration,
                    music_volume,
                    ducking_amount,
                    fade_in_duration,
                    fade_out_duration
                )
            else:
                # Simple mixing without ducking
                mixed_audio = self._mix_simple(
                    voiceover_path,
                    music_path,
                    output_path,
                    duration,
                    music_volume,
                    fade_in_duration,
                    fade_out_duration
                )

            self.logger.info(f"✅ Mixed audio with background music: {output_path}")
            return mixed_audio

        except Exception as e:
            self.logger.error(f"❌ Failed to mix audio with music: {e}")
            # Fallback: copy voiceover without music
            import shutil
            shutil.copy2(voiceover_path, output_path)
            return output_path

    def _mix_with_ducking(
        self,
        voiceover_path: str,
        music_path: str,
        output_path: str,
        duration: float,
        music_volume: float,
        ducking_amount: float,
        fade_in: float,
        fade_out: float
    ) -> str:
        """Mix audio with volume ducking (lowers music during speech)"""

        # Calculate ducked volume
        ducked_volume = music_volume * ducking_amount

        # FFmpeg command with sidechaincompress for ducking
        cmd = [
            self.ffmpeg_path,
            '-i', str(music_path),
            '-i', str(voiceover_path),
            '-filter_complex',
            f'[0:a]aloop=loop=-1:size={int(duration * 48000)},'
            f'volume={music_volume},'
            f'afade=t=in:st=0:d={fade_in},'
            f'afade=t=out:st={duration - fade_out}:d={fade_out}[music];'
            f'[music][1:a]sidechaincompress=threshold=0.02:ratio=4:attack=50:release=200[out]',
            '-map', '[out]',
            '-ac', '2',
            '-ar', '48000',
            '-b:a', '192k',
            '-y',
            str(output_path)
        ]

        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return output_path

    def _mix_simple(
        self,
        voiceover_path: str,
        music_path: str,
        output_path: str,
        duration: float,
        music_volume: float,
        fade_in: float,
        fade_out: float
    ) -> str:
        """Simple audio mixing without ducking"""

        # FFmpeg command for simple mixing
        cmd = [
            self.ffmpeg_path,
            '-i', str(music_path),
            '-i', str(voiceover_path),
            '-filter_complex',
            f'[0:a]aloop=loop=-1:size={int(duration * 48000)},'
            f'volume={music_volume},'
            f'afade=t=in:st=0:d={fade_in},'
            f'afade=t=out:st={duration - fade_out}:d={fade_out}[music];'
            f'[music][1:a]amix=inputs=2:duration=first:dropout_transition=2[out]',
            '-map', '[out]',
            '-ac', '2',
            '-ar', '48000',
            '-b:a', '192k',
            '-y',
            str(output_path)
        ]

        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return output_path

    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio file duration in seconds"""

        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            str(audio_path)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)
        return float(data['format']['duration'])

    def add_sound_effects(
        self,
        audio_path: str,
        output_path: str,
        effects: List[dict]
    ) -> str:
        """
        Add sound effects at specific timestamps

        Args:
            audio_path: Input audio file
            output_path: Output audio file
            effects: List of effects with format:
                     [{'file': 'clap.mp3', 'time': 5.0, 'volume': 0.5}, ...]

        Returns:
            Path to audio with effects
        """
        try:
            if not effects:
                import shutil
                shutil.copy2(audio_path, output_path)
                return output_path

            # Build FFmpeg filter for layering sound effects
            inputs = ['-i', str(audio_path)]
            filter_parts = ['[0:a]']

            for i, effect in enumerate(effects):
                effect_path = self.music_dir.parent / 'sound_effects' / effect['file']
                if not effect_path.exists():
                    self.logger.warning(f"Sound effect not found: {effect_path}")
                    continue

                inputs.extend(['-i', str(effect_path)])

                # Add delay and volume adjustment
                filter_parts.append(
                    f"[{i+1}:a]adelay={int(effect['time']*1000)}|"
                    f"{int(effect['time']*1000)},"
                    f"volume={effect['volume']}[sfx{i}];"
                )

            # Mix all streams
            mix_inputs = '[0:a]' + ''.join([f'[sfx{i}]' for i in range(len(effects))])
            filter_parts.append(f"{mix_inputs}amix=inputs={len(effects)+1}[out]")

            filter_complex = ''.join(filter_parts)

            cmd = [
                self.ffmpeg_path,
                *inputs,
                '-filter_complex', filter_complex,
                '-map', '[out]',
                '-y',
                str(output_path)
            ]

            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            self.logger.info(f"✅ Added {len(effects)} sound effects")
            return output_path

        except Exception as e:
            self.logger.error(f"❌ Failed to add sound effects: {e}")
            import shutil
            shutil.copy2(audio_path, output_path)
            return output_path

    def download_royalty_free_music(self):
        """
        Instructions for downloading royalty-free music

        NOTE: This is a placeholder. You need to manually download music.
        """
        self.logger.info("""
        📥 To use background music, download royalty-free tracks:

        Recommended Sources:
        1. YouTube Audio Library (https://studio.youtube.com/channel/UC.../music)
        2. Incompetech (https://incompetech.com/music/royalty-free/)
        3. Bensound (https://www.bensound.com/)
        4. FreePD (https://freepd.com/)

        Save music files to: {music_dir}/

        Required tracks:
        - upbeat_kids.mp3 (happy, energetic)
        - gentle_learning.mp3 (calm, educational)
        - playful_melody.mp3 (fun, playful)
        - happy_piano.mp3 (simple piano melody)
        - cheerful_ukulele.mp3 (ukulele, upbeat)

        Ensure all music is:
        ✅ Royalty-free or Creative Commons
        ✅ Appropriate for kids content
        ✅ 2-5 minutes long (will loop)
        ✅ MP3 format, 48kHz sample rate
        """.format(music_dir=self.music_dir))


def main():
    """Test background music mixer"""
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 3:
        print("Usage: python background_music_mixer.py <voiceover.mp3> <output.mp3> [category]")
        sys.exit(1)

    voiceover = sys.argv[1]
    output = sys.argv[2]
    category = sys.argv[3] if len(sys.argv) > 3 else "default"

    mixer = BackgroundMusicMixer()
    mixed_audio = mixer.mix_audio_with_music(voiceover, output, category)
    print(f"Mixed audio: {mixed_audio}")


if __name__ == "__main__":
    main()
