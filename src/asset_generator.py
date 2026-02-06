"""
Asset Generator Module

Generates all assets needed for video creation:
- Downloads/generates images based on script
- Creates voiceover from narration text
- Fetches background music
"""

import logging
import requests
from typing import Dict, Any, List
from pathlib import Path
from gtts import gTTS
import random


class AssetGenerator:
    """Generates video assets (images, voiceover, music)."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the AssetGenerator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger("YouTubeAutomation.AssetGenerator")
        self.assets_dir = Path(config['paths']['assets_dir'])
        self.pexels_api_key = config['api_keys'].get('pexels_api_key', '')
    
    def generate_assets(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate all assets needed for the video.
        
        Args:
            script: Script dictionary from ScriptGenerator
            
        Returns:
            Dictionary containing paths to generated assets:
            - voiceover_path: Path to audio file
            - images: List of image paths for each scene
            - music_path: Path to background music (optional)
        """
        
        self.logger.info("Generating video assets...")
        
        assets = {
            'images': [],
            'voiceover_path': None,
            'music_path': None
        }
        
        # Generate voiceover from narration
        self.logger.info("Generating voiceover...")
        assets['voiceover_path'] = self._generate_voiceover(script)
        
        # Download images for each scene
        self.logger.info("Downloading scene images...")
        assets['images'] = self._download_scene_images(script)
        
        # Get background music (optional)
        assets['music_path'] = self._select_background_music()
        
        self.logger.info("Asset generation complete")
        return assets
    
    def _generate_voiceover(self, script: Dict[str, Any]) -> str:
        """
        Generate voiceover audio from script narration.
        
        Args:
            script: Script dictionary
            
        Returns:
            Path to generated audio file
        """
        
        try:
            # Combine all narration text
            narration_text = script.get('full_narration', '')
            
            if not narration_text:
                raise ValueError("No narration text found in script")
            
            # Generate audio using gTTS (Google Text-to-Speech)
            # For better quality, consider using ElevenLabs or other TTS services
            language = self.config['content'].get('language', 'en')
            
            tts = gTTS(text=narration_text, lang=language, slow=False)
            
            # Save audio file
            timestamp = script['topic'].get('timestamp', '').replace(':', '-').split('.')[0]
            audio_dir = Path(self.config['paths']['output_dir']) / 'audio'
            audio_dir.mkdir(parents=True, exist_ok=True)
            audio_path = audio_dir / f"voiceover_{timestamp}.mp3"
            
            tts.save(str(audio_path))
            
            self.logger.info(f"Voiceover generated: {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            self.logger.error(f"Error generating voiceover: {e}")
            raise
    
    def _download_scene_images(self, script: Dict[str, Any]) -> List[str]:
        """
        Download images for each scene in the script.
        
        Args:
            script: Script dictionary
            
        Returns:
            List of paths to downloaded images
        """
        
        image_paths = []
        
        for idx, scene in enumerate(script['scenes']):
            try:
                # Get search keywords for this scene
                keywords = scene.get('search_keywords', [])
                if not keywords:
                    keywords = [script['topic'].get('topic', 'abstract')]
                
                # Download image from Pexels
                image_path = self._download_pexels_image(keywords, idx)
                
                if image_path:
                    image_paths.append(image_path)
                else:
                    # Fallback: use a placeholder or default image
                    self.logger.warning(f"Could not download image for scene {idx}, using placeholder")
                    image_paths.append(None)
                    
            except Exception as e:
                self.logger.error(f"Error downloading image for scene {idx}: {e}")
                image_paths.append(None)
        
        return image_paths
    
    def _download_pexels_image(self, keywords: List[str], scene_idx: int) -> str:
        """
        Download an image from Pexels API.
        
        Args:
            keywords: List of search keywords
            scene_idx: Scene index for filename
            
        Returns:
            Path to downloaded image or None if failed
        """
        
        if not self.pexels_api_key or self.pexels_api_key.startswith('your_'):
            self.logger.warning("Pexels API key not configured, skipping image download")
            return None
        
        try:
            # Search for images
            search_query = ' '.join(keywords[:3])
            headers = {'Authorization': self.pexels_api_key}
            
            response = requests.get(
                'https://api.pexels.com/v1/search',
                headers=headers,
                params={'query': search_query, 'per_page': 5, 'orientation': 'landscape'}
            )
            
            if response.status_code != 200:
                self.logger.warning(f"Pexels API error: {response.status_code}")
                return None
            
            data = response.json()
            
            if not data.get('photos'):
                self.logger.warning(f"No images found for: {search_query}")
                return None
            
            # Get a random image from results
            photo = random.choice(data['photos'])
            image_url = photo['src']['large']
            
            # Download image
            img_response = requests.get(image_url, timeout=30)
            img_response.raise_for_status()
            
            # Save image
            images_dir = self.assets_dir / 'images'
            images_dir.mkdir(exist_ok=True)
            
            image_path = images_dir / f"scene_{scene_idx:03d}.jpg"
            
            with open(image_path, 'wb') as f:
                f.write(img_response.content)
            
            self.logger.debug(f"Downloaded image: {image_path}")
            return str(image_path)
            
        except Exception as e:
            self.logger.error(f"Error downloading from Pexels: {e}")
            return None
    
    def _select_background_music(self) -> str:
        """
        Select background music for the video.
        
        Returns:
            Path to music file or None
        """
        
        # Check if music directory has any files
        music_dir = self.assets_dir / 'music'
        
        if not music_dir.exists():
            return None
        
        music_files = list(music_dir.glob('*.mp3')) + list(music_dir.glob('*.wav'))
        
        if music_files:
            # Select random music file
            music_path = random.choice(music_files)
            self.logger.info(f"Selected background music: {music_path.name}")
            return str(music_path)
        
        return None
