"""
Kids Voiceover Generator Module

Converts narration text into child-friendly voiceover audio files
using ElevenLabs API.

Features:
- Calm, friendly voice for children
- Slightly slower speaking speed (0.85x)
- Handles long text with automatic chunking
- MP3 output format
- Retry logic with error handling
- Progress tracking
"""

import logging
import time
import asyncio
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import requests
from elevenlabs.client import ElevenLabs
import edge_tts


class KidsVoiceoverGenerator:
    """
    Generates child-friendly voiceover audio from text using ElevenLabs API.

    Features calm, warm voices suitable for educational content
    aimed at children aged 4-8 years.
    """

    # ElevenLabs API settings
    ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

    # Voice IDs (ElevenLabs voices suitable for kids content)
    # Bella: Soft, gentle, warm female voice (MORE NATURAL)
    DEFAULT_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"

    # Alternative kid-friendly voices:
    # Rachel: Calm, clear, warm female voice (more formal)
    RACHEL_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
    # Elli: Young, lively female voice
    ELLI_VOICE_ID = "MF3mGyEYCl7XYWbV9V6O"

    # Edge TTS voices (FREE, unlimited) - Used as fallback when ElevenLabs quota exceeded
    EDGE_VOICE_FEMALE_CHILD = "en-US-AnaNeural"  # Young, friendly female
    EDGE_VOICE_FEMALE_FRIENDLY = "en-US-AriaNeural"  # MOST NATURAL: Warm, expressive, human-like
    EDGE_VOICE_FEMALE_STORY = "en-US-SaraNeural"  # Natural storytelling voice

    # Voice settings optimized for NATURAL, HUMAN-LIKE speech
    DEFAULT_STABILITY = 0.35      # Lower = more variation = more human (0.3-0.5 recommended)
    DEFAULT_SIMILARITY = 0.80     # How close to original voice
    DEFAULT_STYLE = 0.40          # Higher = more expressive = more human (0.3-0.6 recommended)
    DEFAULT_SPEED = 0.90          # Natural speaking speed (0.85-1.0 for kids)

    # API settings
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    REQUEST_TIMEOUT = 120

    # Text chunking (ElevenLabs has character limits)
    MAX_CHARS_PER_REQUEST = 5000
    
    # Multilingual natural fillers and praise for human-like speech
    LANGUAGE_FILLERS = {
        'en': {'fillers': ['Okay', 'Alright', 'Now', 'So'], 'praise': ['Good', 'Great', 'Nice', 'Well done']},
        'hi': {'fillers': ['अच्छा', 'ठीक है', 'अब', 'तो'], 'praise': ['बहुत अच्छा', 'शाबाश', 'वाह', 'बढ़िया']},
        'es': {'fillers': ['Bueno', 'Vale', 'Ahora', 'Entonces'], 'praise': ['Bien', 'Genial', 'Excelente', 'Muy bien']},
        'fr': {'fillers': ['Bon', "D'accord", 'Maintenant', 'Alors'], 'praise': ['Bien', 'Génial', 'Excellent', 'Très bien']},
        'de': {'fillers': ['Gut', 'Also', 'Jetzt', 'So'], 'praise': ['Gut', 'Prima', 'Toll', 'Sehr gut']},
        'pt': {'fillers': ['Bom', 'Certo', 'Agora', 'Então'], 'praise': ['Bom', 'Ótimo', 'Excelente', 'Muito bem']},
        'ar': {'fillers': ['حسناً', 'طيب', 'الآن', 'إذاً'], 'praise': ['جيد', 'رائع', 'ممتاز', 'أحسنت']},
        'ja': {'fillers': ['さあ', 'では', '今', 'それで'], 'praise': ['いいね', 'すごい', 'よくできました', '素晴らしい']},
        'ko': {'fillers': ['좋아', '그래', '이제', '자'], 'praise': ['잘했어', '대단해', '훌륭해', '아주 좋아']},
        'zh': {'fillers': ['好', '那么', '现在', '所以'], 'praise': ['很好', '太棒了', '真棒', '非常好']}
    }

    def __init__(
        self,
        api_key: str,
        voice_id: Optional[str] = None,
        output_dir: Optional[str] = None,
        speed: float = DEFAULT_SPEED,
        language: str = 'en'
    ):
        """
        Initialize the Kids Voiceover Generator.

        Args:
            api_key: ElevenLabs API key
            voice_id: Voice ID to use (default: Rachel)
            output_dir: Directory to save audio files (default: output/)
            speed: Speaking speed multiplier (default: 0.85 for slower)
            language: Language code for fillers/praise (default: 'en')
        """
        self.api_key = api_key
        self.voice_id = voice_id or self.DEFAULT_VOICE_ID
        self.speed = speed
        self.language = language
        self.logger = logging.getLogger(__name__)

        # Initialize ElevenLabs client with official SDK
        self.client = ElevenLabs(api_key=api_key)

        # Set up output directory
        if output_dir is None:
            project_root = Path(__file__).parent.parent
            self.output_dir = project_root / "output"
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Audio files will be saved to: {self.output_dir}")

    def generate_voiceover(
        self,
        text: str,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Generate voiceover audio from text with natural human-like pauses.

        Args:
            text: Narration text to convert to speech
            output_filename: Output filename (default: auto-generated)

        Returns:
            str: Path to generated audio file

        Raises:
            ValueError: If text is empty or too short
            RuntimeError: If generation fails after retries
        """
        # Validate input
        if not text or len(text.strip()) < 10:
            raise ValueError("Text must be at least 10 characters long")

        # Add natural pauses between sentences (human-like speech)
        text = self._add_natural_pauses(text)
        
        # Add human-like elements (fillers, praise, natural flow)
        text = self._add_human_elements(text)

        self.logger.info(f"Generating voiceover ({len(text)} characters)")

        # Generate output filename if not provided
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"voiceover_{timestamp}.mp3"

        # Ensure .mp3 extension
        if not output_filename.endswith('.mp3'):
            output_filename += '.mp3'

        output_path = self.output_dir / output_filename

        # Check if text needs to be chunked
        if len(text) > self.MAX_CHARS_PER_REQUEST:
            self.logger.info("Text exceeds limit, using chunked generation")
            return self._generate_chunked_voiceover(text, output_path)
        else:
            return self._generate_single_voiceover(text, output_path)

    def _generate_single_voiceover(self, text: str, output_path: Path) -> str:
        """
        Generate voiceover for text that fits in one request.

        Args:
            text: Text to convert
            output_path: Path to save audio file

        Returns:
            str: Path to generated audio file
        """
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                self.logger.debug(f"Using ElevenLabs SDK (attempt {attempt}/{self.MAX_RETRIES})")

                # Use official ElevenLabs SDK with HUMAN-LIKE voice settings
                audio_generator = self.client.text_to_speech.convert(
                    text=text,
                    voice_id=self.voice_id,
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128",
                    voice_settings={
                        "stability": self.DEFAULT_STABILITY,     # Lower for natural variation
                        "similarity_boost": self.DEFAULT_SIMILARITY,
                        "style": self.DEFAULT_STYLE,            # Higher for expressiveness
                        "use_speaker_boost": True               # Enhanced clarity
                    }
                )

                # Write audio to file
                with open(output_path, 'wb') as f:
                    for chunk in audio_generator:
                        f.write(chunk)

                file_size_mb = output_path.stat().st_size / (1024 * 1024)
                self.logger.info(f"✓ Voiceover generated: {output_path.name} ({file_size_mb:.2f} MB)")

                return str(output_path)

            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"Attempt {attempt} failed: {error_msg}")
                
                # Check if quota exceeded - fall back to FREE Edge TTS
                if "quota_exceeded" in error_msg.lower() or "401" in error_msg:
                    self.logger.warning("⚠️  ElevenLabs quota exceeded - switching to FREE Edge TTS")
                    return self._generate_edge_tts(text, output_path)
                
                if attempt < self.MAX_RETRIES:
                    delay = self.RETRY_DELAY * attempt
                    self.logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    # Final fallback: try Edge TTS before giving up
                    self.logger.warning("⚠️  ElevenLabs failed - trying FREE Edge TTS as fallback")
                    return self._generate_edge_tts(text, output_path)

        raise RuntimeError("Voiceover generation failed")

    def _generate_chunked_voiceover(self, text: str, output_path: Path) -> str:
        """
        Generate voiceover for long text by chunking.

        Args:
            text: Long text to convert
            output_path: Path to save final audio file

        Returns:
            str: Path to generated audio file
        """
        self.logger.info("Chunking text for generation")

        # Split text into chunks
        chunks = self._split_text_into_chunks(text)
        self.logger.info(f"Split into {len(chunks)} chunks")

        # Generate audio for each chunk
        chunk_files = []

        for i, chunk in enumerate(chunks, 1):
            self.logger.info(f"Generating chunk {i}/{len(chunks)}")

            chunk_filename = f"chunk_{i:03d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            chunk_path = self.output_dir / chunk_filename

            try:
                self._generate_single_voiceover(chunk, chunk_path)
                chunk_files.append(chunk_path)

                # Small delay between chunks to avoid rate limits
                if i < len(chunks):
                    time.sleep(1)

            except Exception as e:
                self.logger.error(f"Failed to generate chunk {i}: {e}")
                # Clean up partial files
                for chunk_file in chunk_files:
                    if chunk_file.exists():
                        chunk_file.unlink()
                raise

        # Merge audio chunks
        self.logger.info("Merging audio chunks")
        merged_path = self._merge_audio_files(chunk_files, output_path)

        # Clean up chunk files
        for chunk_file in chunk_files:
            if chunk_file.exists():
                chunk_file.unlink()

        return merged_path

    def _split_text_into_chunks(self, text: str) -> List[str]:
        """
        Split long text into chunks at sentence boundaries.

        Args:
            text: Text to split

        Returns:
            List[str]: List of text chunks
        """
        # Split into sentences
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            # Check if adding this sentence would exceed limit
            if len(current_chunk) + len(sentence) > self.MAX_CHARS_PER_REQUEST:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence

        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _merge_audio_files(self, audio_files: List[Path], output_path: Path) -> str:
        """
        Merge multiple audio files into one using FFmpeg.

        Args:
            audio_files: List of audio file paths
            output_path: Path for merged output

        Returns:
            str: Path to merged audio file
        """
        import subprocess
        import tempfile

        try:
            # If only one file, just copy it
            if len(audio_files) == 1:
                import shutil
                shutil.copy(audio_files[0], output_path)
                self.logger.info(f"✓ Single audio file copied: {output_path.name}")
                return str(output_path)

            # Create concat file for FFmpeg
            concat_file = Path(tempfile.gettempdir()) / "concat_list.txt"
            with open(concat_file, 'w', encoding='utf-8') as f:
                for audio_file in audio_files:
                    # Need absolute paths and escape special characters
                    abs_path = str(audio_file.absolute()).replace('\\', '/')
                    f.write(f"file '{abs_path}'\n")

            # Use FFmpeg to concatenate audio files
            ffmpeg_path = self._get_ffmpeg_path()

            cmd = [
                ffmpeg_path,
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c', 'copy',  # Copy codec (no re-encoding, faster)
                '-y',  # Overwrite output
                str(output_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                self.logger.info(f"✓ Merged {len(audio_files)} audio files: {output_path.name}")
                return str(output_path)
            else:
                raise Exception(f"FFmpeg merge failed: {result.stderr}")

        except Exception as e:
            self.logger.error(f"Failed to merge audio files: {str(e)}")

            # Fallback: just use first chunk
            self.logger.warning("Using first audio chunk only as fallback")
            import shutil
            shutil.copy(audio_files[0], output_path)
            return str(output_path)
        finally:
            # Clean up concat file
            if 'concat_file' in locals() and concat_file.exists():
                concat_file.unlink()

    def _get_ffmpeg_path(self) -> str:
        """Get FFmpeg executable path."""
        import config
        import shutil

        # Try configured path first
        if config.FFMPEG_PATH and os.path.exists(config.FFMPEG_PATH):
            return config.FFMPEG_PATH

        # Try system ffmpeg
        system_ffmpeg = shutil.which('ffmpeg')
        if system_ffmpeg:
            return system_ffmpeg

        raise FileNotFoundError("FFmpeg not found. Install FFmpeg or set FFMPEG_PATH in config.")
    
    def _add_human_elements(self, text: str) -> str:
        """
        Add human-like teacher elements to plain text (for any TTS engine).
        
        Adds:
        - Natural fillers (language-specific: Okay/अच्छा/Bueno/etc.)
        - Gentle praise (language-specific: Good/बहुत अच्छा/Bien/etc.)
        - More natural flow
        
        Args:
            text: Plain script text
            
        Returns:
            str: Enhanced text with human-like elements
        """
        import re
        import random
        
        # Get language-specific fillers and praise
        lang_data = self.LANGUAGE_FILLERS.get(self.language, self.LANGUAGE_FILLERS['en'])
        fillers = lang_data['fillers']
        praise = lang_data['praise']
        
        # Split into sentences
        sentences = text.split('.')
        enhanced_sentences = []
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Add natural filler before some sentences (not first)
            if i > 0 and random.random() < 0.12:  # 12% chance
                sentence = f'{random.choice(fillers)}, {sentence}'
            
            # Add gentle praise occasionally
            if i > 0 and random.random() < 0.08:  # 8% chance
                sentence = f'{random.choice(praise)}! {sentence}'
            
            enhanced_sentences.append(sentence)
        
        return '. '.join(enhanced_sentences)

    def _transform_to_human_narration(self, text: str) -> str:
        """
        Transform script text into HUMAN-LIKE, warm teacher narration with SSML.
        
        Args:
            text: Plain script text
            
        Returns:
            str: SSML-enhanced human-like narration (plain text + breaks only)
        """
        import re
        import random
        
        # Add pauses after sentences
        text = re.sub(r'\.\s+', '.<break time="500ms"/> ', text)
        
        # Add longer pauses after questions
        text = re.sub(r'\?\s+', '?<break time="800ms"/> ', text)
        
        # Add pauses after exclamations
        text = re.sub(r'!\s+', '!<break time="600ms"/> ', text)
        
        # Add natural fillers and praise between sentences
        sentences = text.split('.')
        enhanced_sentences = []
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Add filler occasionally (not first sentence)
            if i > 0 and random.random() < 0.12:
                fillers = ['Okay', 'Alright', 'Now', 'So']
                sentence = f'{random.choice(fillers)},<break time="300ms"/> {sentence}'
            
            # Add gentle praise occasionally
            if i > 0 and random.random() < 0.08:
                praise = ['Good', 'Great', 'Nice', 'Well done']
                sentence = f'{random.choice(praise)}!<break time="400ms"/> {sentence}'
            
            enhanced_sentences.append(sentence)
        
        text = '. '.join(enhanced_sentences)
        
        # Stretch numbers for emphasis (verbal emphasis)
        numbers = {
            'one': 'o n e', 'two': 't w o', 'three': 'th r e e',
            'four': 'f o u r', 'five': 'f i v e', 'six': 's i x',
            'seven': 's e v e n', 'eight': 'e i g h t', 
            'nine': 'n i n e', 'ten': 't e n'
        }
        for num, stretched in numbers.items():
            text = re.sub(rf'\b{num}\b', stretched, text, flags=re.I)
        
        # Add breathing pauses at commas
        text = re.sub(r',\s*', ',<break time="300ms"/> ', text)
        
        return text

    def _generate_edge_tts(self, text: str, output_path: Path) -> str:
        """
        Generate voiceover using FREE Microsoft Edge TTS (unlimited, no API key).
        
        This is used as fallback when ElevenLabs quota is exceeded.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save audio file
            
        Returns:
            str: Path to generated audio file
        """
        try:
            self.logger.info("🆓 Using FREE Edge TTS (Microsoft)")
            
            # Transform text to human-like narration with SSML
            human_text = self._transform_to_human_narration(text)
            self.logger.info("🎙️  Applied human-like narration transformation (SSML)")
            
            # Run async Edge TTS generation with transformed text
            asyncio.run(self._edge_tts_async(human_text, output_path))
            
            if output_path.exists():
                file_size_mb = output_path.stat().st_size / (1024 * 1024)
                self.logger.info(f"✓ FREE voiceover generated: {output_path.name} ({file_size_mb:.2f} MB)")
                return str(output_path)
            else:
                raise RuntimeError("Edge TTS failed to create audio file")
                
        except Exception as e:
            self.logger.error(f"Edge TTS generation failed: {e}")
            raise
    
    async def _edge_tts_async(self, text: str, output_path: Path):
        """Async helper for Edge TTS generation."""
        # Use MOST NATURAL voice (Aria is most human-like)
        voice = self.EDGE_VOICE_FEMALE_FRIENDLY
        
        # NATURAL SETTINGS for human-like speech:
        # - Slower rate for kids content (easier to understand)
        # - Slight pitch variation (more natural, less monotone)
        # - Softer volume (less aggressive/robotic)
        communicate = edge_tts.Communicate(
            text, 
            voice, 
            rate="-15%",      # Slower, clearer for kids (was -5%)
            pitch="+0Hz",     # Natural pitch, no artificial raising
            volume="+0%"      # Normal volume
        )
        
        # Generate and save audio
        await communicate.save(str(output_path))
    
    def _add_natural_pauses(self, text: str) -> str:
        """
        Add natural pauses between sentences for human-like speech rhythm.
        
        Adds slight pauses (SSML breaks) after sentences to mimic how
        real humans naturally pause when speaking.
        
        Args:
            text: Original narration text
            
        Returns:
            str: Text with pause markers added
        """
        import re
        import random
        
        # Add natural pauses after sentence endings
        # Pause duration varies (300-700ms) for natural feel
        def add_pause(match):
            # Random pause between 300-700ms for variety
            pause_ms = random.randint(300, 700)
            ending = match.group(0)
            # Add a pause after sentence endings
            return f"{ending} ... "
        
        # Add pauses after periods, question marks, exclamation marks
        text = re.sub(r'[.!?](?=\s)', add_pause, text)
        
        return text

    def test_api(self) -> bool:
        """
        Test if the ElevenLabs API key is valid.

        Returns:
            bool: True if API key is valid, False otherwise
        """
        test_text = "Hello, this is a test."

        try:
            url = f"{self.ELEVENLABS_API_URL}/{self.voice_id}"

            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }

            payload = {
                "text": test_text,
                "model_id": "eleven_monolingual_v1"
            }

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                self.logger.info("✓ ElevenLabs API key is valid")
                return True
            else:
                self.logger.error(f"✗ API test failed: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"✗ API test error: {e}")
            return False

    def get_available_voices(self) -> List[dict]:
        """
        Get list of available voices from ElevenLabs.

        Returns:
            List[dict]: List of available voices with metadata
        """
        try:
            url = "https://api.elevenlabs.io/v1/voices"

            headers = {
                "Accept": "application/json",
                "xi-api-key": self.api_key
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                voices = response.json().get('voices', [])
                self.logger.info(f"Found {len(voices)} available voices")
                return voices
            else:
                self.logger.error(f"Failed to get voices: {response.status_code}")
                return []

        except Exception as e:
            self.logger.error(f"Error getting voices: {e}")
            return []


def generate_voiceover_from_script(
    script: dict,
    api_key: str,
    output_filename: Optional[str] = None,
    speed: float = 0.85
) -> str:
    """
    Convenience function to generate voiceover from a video script.

    Args:
        script: Video script dictionary (from kids_script_generator)
        api_key: ElevenLabs API key
        output_filename: Output filename (default: auto-generated)
        speed: Speaking speed (default: 0.85 for slightly slower)

    Returns:
        str: Path to generated audio file

    Example:
        >>> from kids_script_generator import generate_kids_script
        >>> script = generate_kids_script("Why Birds Fly", api_key="sk-...")
        >>> audio = generate_voiceover_from_script(script, api_key="elevenlabs-key")
        >>> print(f"Audio saved to: {audio}")
    """
    # Extract full narration from script
    narration = script.get('full_narration', '')

    if not narration:
        # Build narration from sections if full_narration not available
        parts = []

        if 'intro' in script:
            parts.append(script['intro'].get('narration', ''))

        if 'body_sections' in script:
            for section in script['body_sections']:
                parts.append(section.get('narration', ''))

        if 'outro' in script:
            parts.append(script['outro'].get('narration', ''))

        narration = "\n\n".join(parts)

    # Generate voiceover
    generator = KidsVoiceoverGenerator(api_key=api_key, speed=speed)
    return generator.generate_voiceover(narration, output_filename)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of the KidsVoiceoverGenerator.
    """
    import os
    import sys

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Get API key from environment
    api_key = os.getenv("ELEVENLABS_API_KEY")

    if not api_key:
        print("Error: ELEVENLABS_API_KEY environment variable not set")
        print("Get your API key from: https://elevenlabs.io/")
        sys.exit(1)

    print("=" * 80)
    print("Kids Voiceover Generator Demo")
    print("=" * 80)
    print()

    # Create generator
    generator = KidsVoiceoverGenerator(api_key=api_key, speed=0.85)

    # Test API connection
    print("Testing API connection...")
    if not generator.test_api():
        print("✗ API test failed. Check your API key.")
        sys.exit(1)

    print("✓ API connection successful")
    print()

    # Example narration text
    narration = """
    Hello friends! Today we're going to learn about something amazing.

    Have you ever wondered why the sky is blue? It's a great question!

    The sky looks blue because of something called sunlight. Sunlight has many colors in it.
    When sunlight comes through the air, the blue color spreads out more than other colors.
    That's why we see a beautiful blue sky!

    Isn't that cool? Now you know why the sky is blue!

    Thanks for learning with me today. See you next time!
    """

    print("Sample narration:")
    print("-" * 80)
    print(narration.strip())
    print("-" * 80)
    print()

    # Ask user if they want to proceed (API costs money)
    response = input("Generate voiceover? This will use your ElevenLabs API quota. (y/n): ").lower()

    if response != 'y':
        print("Cancelled.")
        sys.exit(0)

    print()
    print("Generating voiceover...")
    print()

    try:
        # Generate voiceover
        audio_path = generator.generate_voiceover(
            text=narration,
            output_filename="demo_voiceover.mp3"
        )

        print()
        print("=" * 80)
        print("SUCCESS!")
        print("=" * 80)
        print(f"✓ Voiceover generated: {audio_path}")
        print()
        print("You can now play this audio file in any media player.")

    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR")
        print("=" * 80)
        print(f"✗ Failed to generate voiceover: {e}")
        sys.exit(1)
