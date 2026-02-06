"""
Kids Video Image Generator Module

Generates AI images for long-form kids YouTube videos using OpenAI DALL-E API.
Creates high-quality 3D cartoon-style images in Pixar-Disney style suitable for children aged 4-8.

Features:
- Generates 1 image per 20-30 seconds of narration
- Optimized Pixar-Disney 3D cartoon style with vibrant colors
- Professional children's book illustration quality
- Soft lighting, rounded shapes, expressive characters
- No text or watermarks
- Saves to output/images/
- Returns ordered list of image paths
"""

import logging
import os
import time
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from openai import OpenAI, OpenAIError


@dataclass
class ImagePrompt:
    """Represents a prompt for image generation."""
    scene_number: int
    description: str
    duration_seconds: int


@dataclass
class GeneratedImage:
    """Represents a generated image with metadata."""
    scene_number: int
    file_path: str
    prompt: str
    generation_time: float


class KidsImageGenerator:
    """
    Generates high-quality 3D cartoon-style AI images for kids YouTube videos.

    Uses OpenAI DALL-E API to create vibrant Pixar-Disney style images
    with professional children's book illustration quality.
    Optimized prompts ensure consistent, appealing cartoon aesthetics.
    """

    # Image generation settings
    IMAGE_SIZE = "1024x1024"  # DALL-E 3 standard size
    IMAGE_QUALITY = "standard"  # or "hd" for higher quality (more expensive)
    IMAGE_MODEL = "dall-e-3"  # Latest DALL-E model

    # Timing: 1 image per 20-30 seconds (default: 25 seconds)
    SECONDS_PER_IMAGE = 25

    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY = 2

    # Download settings
    DOWNLOAD_TIMEOUT = 30

    def __init__(
        self,
        api_key: str,
        output_dir: Optional[str] = None,
        seconds_per_image: int = 25
    ):
        """
        Initialize the Kids Image Generator.

        Args:
            api_key: OpenAI API key
            output_dir: Directory to save images (default: assets/images/)
            seconds_per_image: Generate 1 image per N seconds (default: 25)
        """
        self.client = OpenAI(api_key=api_key)
        self.seconds_per_image = seconds_per_image
        self.logger = logging.getLogger(__name__)

        # Set up output directory
        if output_dir is None:
            project_root = Path(__file__).parent.parent
            self.output_dir = project_root / "output" / "images"
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create session-specific subdirectory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.output_dir / f"video_{timestamp}"
        self.session_dir.mkdir(exist_ok=True)

        self.logger.info(f"Images will be saved to: {self.session_dir}")

    def generate_images_from_script(
        self,
        script: Dict[str, Any]
    ) -> List[str]:
        """
        Generate images for all sections of a video script.

        Args:
            script: Video script dictionary (from kids_script_generator)

        Returns:
            List[str]: Ordered list of image file paths
        """
        self.logger.info("Starting image generation from script")

        # Calculate number of images needed
        total_duration = script.get('target_duration_seconds', 300)
        num_images = max(1, total_duration // self.seconds_per_image)

        self.logger.info(f"Video duration: {total_duration}s, generating {num_images} images")

        # Extract image prompts from script sections
        image_prompts = self._extract_prompts_from_script(script, num_images)

        # Generate images
        generated_images = []

        for idx, prompt_data in enumerate(image_prompts, 1):
            self.logger.info(f"Generating image {idx}/{len(image_prompts)}")

            try:
                image_path = self._generate_single_image(
                    scene_number=idx,
                    description=prompt_data['description'],
                    visual_suggestions=prompt_data.get('visual_suggestions', [])
                )

                if image_path:
                    generated_images.append(image_path)
                    self.logger.info(f"✓ Image {idx} saved: {Path(image_path).name}")
                else:
                    self.logger.warning(f"✗ Failed to generate image {idx}")

                # Small delay between requests to avoid rate limits
                if idx < len(image_prompts):
                    time.sleep(1)

            except Exception as e:
                self.logger.error(f"Error generating image {idx}: {e}")
                # Continue with remaining images

        self.logger.info(f"Image generation complete: {len(generated_images)}/{len(image_prompts)} successful")

        return generated_images

    def _extract_prompts_from_script(
        self,
        script: Dict[str, Any],
        num_images: int
    ) -> List[Dict[str, Any]]:
        """
        Extract image generation prompts from script sections.

        Args:
            script: Video script dictionary
            num_images: Number of images to generate

        Returns:
            List[dict]: List of prompt data for each image
        """
        prompts = []

        # Collect all sections
        sections = []

        # Add intro
        if 'intro' in script:
            sections.append({
                'title': script['intro'].get('title', 'Introduction'),
                'narration': script['intro'].get('narration', ''),
                'visual_suggestions': script['intro'].get('visual_suggestions', [])
            })

        # Add body sections
        if 'body_sections' in script:
            for section in script['body_sections']:
                sections.append({
                    'title': section.get('title', ''),
                    'narration': section.get('narration', ''),
                    'visual_suggestions': section.get('visual_suggestions', [])
                })

        # Add outro
        if 'outro' in script:
            sections.append({
                'title': script['outro'].get('title', 'Conclusion'),
                'narration': script['outro'].get('narration', ''),
                'visual_suggestions': script['outro'].get('visual_suggestions', [])
            })

        # Distribute images across sections
        total_sections = len(sections)

        # Guard against empty sections
        if total_sections == 0:
            self.logger.warning("No sections found in script, using default prompt")
            return [{
                'description': "A colorful educational illustration for children",
                'visual_suggestions': []
            }] * min(num_images, 5)  # Limit to 5 default images

        images_per_section = max(1, num_images // total_sections)

        for section in sections:
            # Create prompts based on visual suggestions and narration
            prompt_text = self._create_prompt_from_section(section)

            prompts.append({
                'description': prompt_text,
                'visual_suggestions': section.get('visual_suggestions', [])
            })

        # If we need more images, duplicate some prompts with variations
        while len(prompts) < num_images:
            base_prompt = prompts[len(prompts) % len(sections)]
            prompts.append(base_prompt)

        # Trim to exact number needed
        return prompts[:num_images]

    def _create_prompt_from_section(self, section: Dict[str, Any]) -> str:
        """
        Create an image generation prompt from a script section.

        Args:
            section: Script section with narration and visual suggestions

        Returns:
            str: Description for image generation
        """
        visual_suggestions = section.get('visual_suggestions', [])
        title = section.get('title', '')

        # Use visual suggestions if available
        if visual_suggestions:
            description = ', '.join(visual_suggestions[:3])
        else:
            # Extract key concepts from title
            description = title

        return description

    def _generate_single_image(
        self,
        scene_number: int,
        description: str,
        visual_suggestions: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Generate a single AI image with retry logic.

        Args:
            scene_number: Scene number for filename
            description: Basic description of the scene
            visual_suggestions: Additional visual elements

        Returns:
            str: Path to saved image file, or None if failed
        """
        # Build enhanced prompt with style guidelines
        prompt = self._build_dalle_prompt(description, visual_suggestions)

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                # Generate image with DALL-E
                response = self.client.images.generate(
                    model=self.IMAGE_MODEL,
                    prompt=prompt,
                    size=self.IMAGE_SIZE,
                    quality=self.IMAGE_QUALITY,
                    n=1
                )

                # Get image URL
                image_url = response.data[0].url

                # Download and save image
                image_path = self._download_image(image_url, scene_number)

                return image_path

            except OpenAIError as e:
                self.logger.error(f"OpenAI API error (attempt {attempt}/{self.MAX_RETRIES}): {e}")

                if attempt < self.MAX_RETRIES:
                    delay = self.RETRY_DELAY * attempt
                    self.logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"Failed to generate image after {self.MAX_RETRIES} attempts")
                    return None

            except Exception as e:
                self.logger.error(f"Unexpected error generating image: {e}")
                return None

        return None

    def _build_dalle_prompt(
        self,
        description: str,
        visual_suggestions: Optional[List[str]] = None
    ) -> str:
        """
        Build an optimized DALL-E prompt with advanced style guidelines for kids cartoon content.

        Args:
            description: Basic scene description
            visual_suggestions: Additional visual elements

        Returns:
            str: Complete DALL-E prompt with optimized cartoon style
        """
        # Enhanced style guidelines for high-quality kids cartoon content
        # Inspired by Disney, Pixar, and modern children's book illustrations
        style = (
            "High-quality 3D cartoon illustration in vibrant Pixar-Disney style "
            "for children aged 4-8. Ultra-colorful with saturated bright colors, "
            "soft rounded shapes, big expressive eyes, friendly smiling characters. "
            "Professional children's book illustration quality with soft lighting, "
            "gentle gradients, smooth textures. Cheerful, warm, inviting atmosphere. "
            "Clean composition with clear focal point. Playful and educational. "
            "Cute proportions with large heads and small bodies. Smooth 3D rendering style. "
            "No text, no words, no letters, no watermarks, no labels."
        )

        # Combine description with visual suggestions
        if visual_suggestions:
            scene_elements = ', '.join(visual_suggestions[:3])
            content = f"{description}. Featured elements: {scene_elements}."
        else:
            content = description

        # Add composition and quality enhancers
        quality_keywords = (
            "Professional digital art, high detail, sharp focus, perfect composition, "
            "trending on children's illustration platforms, award-winning style"
        )

        # Complete prompt with style + content + quality
        prompt = f"{style} Scene: {content} {quality_keywords}"

        # Ensure prompt isn't too long (DALL-E has limits)
        if len(prompt) > 1000:
            # Trim quality keywords first if needed
            prompt = f"{style} Scene: {content}"
            if len(prompt) > 1000:
                prompt = prompt[:1000]

        return prompt

    def _download_image(self, url: str, scene_number: int) -> str:
        """
        Download image from URL and save to file.

        Args:
            url: Image URL
            scene_number: Scene number for filename

        Returns:
            str: Path to saved image file

        Raises:
            RuntimeError: If download fails
        """
        try:
            response = requests.get(url, timeout=self.DOWNLOAD_TIMEOUT)
            response.raise_for_status()

            # Save image
            filename = f"scene_{scene_number:03d}.png"
            file_path = self.session_dir / filename

            with open(file_path, 'wb') as f:
                f.write(response.content)

            return str(file_path)

        except requests.RequestException as e:
            raise RuntimeError(f"Failed to download image: {e}") from e

    def generate_placeholder_images(
        self,
        num_images: int,
        topic: str = "Educational Content"
    ) -> List[str]:
        """
        Generate placeholder images when API is unavailable.

        Creates simple colored images with scene numbers as fallback.

        Args:
            num_images: Number of placeholder images to create
            topic: Video topic for reference

        Returns:
            List[str]: List of placeholder image paths
        """
        self.logger.warning("Generating placeholder images (API unavailable)")

        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            self.logger.error("PIL not available for placeholder generation")
            return []

        placeholders = []

        for i in range(1, num_images + 1):
            try:
                # Create colorful gradient background
                img = Image.new('RGB', (1024, 1024), color=(100, 150, 200))
                draw = ImageDraw.Draw(img)

                # Add scene number
                text = f"Scene {i}"

                # Try to use a nice font, fallback to default
                try:
                    font = ImageFont.truetype("arial.ttf", 80)
                except:
                    font = ImageFont.load_default()

                # Calculate text position (centered)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                position = ((1024 - text_width) // 2, (1024 - text_height) // 2)

                # Draw text
                draw.text(position, text, fill=(255, 255, 255), font=font)

                # Save placeholder
                filename = f"placeholder_{i:03d}.png"
                file_path = self.session_dir / filename
                img.save(file_path)

                placeholders.append(str(file_path))

            except Exception as e:
                self.logger.error(f"Error creating placeholder {i}: {e}")

        return placeholders


def generate_images_for_video(
    script: Dict[str, Any],
    api_key: str,
    output_dir: Optional[str] = None,
    seconds_per_image: int = 25
) -> List[str]:
    """
    Convenience function to generate images for a video script.

    Args:
        script: Video script dictionary (from kids_script_generator)
        api_key: OpenAI API key
        output_dir: Directory to save images (default: assets/images/)
        seconds_per_image: Generate 1 image per N seconds (default: 25)

    Returns:
        List[str]: Ordered list of image file paths

    Example:
        >>> from kids_script_generator import generate_kids_script
        >>> script = generate_kids_script("Why Birds Fly", api_key="sk-...")
        >>> images = generate_images_for_video(script, api_key="sk-...")
        >>> print(f"Generated {len(images)} images")
    """
    generator = KidsImageGenerator(
        api_key=api_key,
        output_dir=output_dir,
        seconds_per_image=seconds_per_image
    )

    return generator.generate_images_from_script(script)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of the KidsImageGenerator.
    """
    import os
    import sys
    import json

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    print("=" * 80)
    print("Kids Video Image Generator Demo")
    print("=" * 80)
    print()

    # Example: Create a simple mock script
    mock_script = {
        'topic': 'Why Do Leaves Change Colors?',
        'target_duration_seconds': 180,  # 3 minutes
        'intro': {
            'title': 'Introduction',
            'narration': 'Hello! Have you ever wondered why leaves change colors?',
            'visual_suggestions': ['colorful autumn leaves', 'happy tree', 'sunny day']
        },
        'body_sections': [
            {
                'title': 'What Makes Leaves Green',
                'narration': 'Leaves are green because of something called chlorophyll.',
                'visual_suggestions': ['green leaves', 'sunlight', 'tree in summer']
            },
            {
                'title': 'Why Colors Change',
                'narration': 'When fall comes, trees stop making chlorophyll.',
                'visual_suggestions': ['yellow leaves', 'orange leaves', 'fall season']
            },
            {
                'title': 'Beautiful Fall Colors',
                'narration': 'Now we can see the beautiful red, yellow, and orange colors!',
                'visual_suggestions': ['red leaves', 'yellow leaves', 'colorful fall tree']
            }
        ],
        'outro': {
            'title': 'Conclusion',
            'narration': 'Now you know why leaves change colors in the fall!',
            'visual_suggestions': ['pile of colorful leaves', 'happy children', 'autumn scene']
        }
    }

    print(f"Topic: {mock_script['topic']}")
    print(f"Duration: {mock_script['target_duration_seconds']} seconds")
    print()

    # Ask user if they want to proceed (API costs money)
    response = input("Generate images with DALL-E API? (y/n): ").lower()

    if response != 'y':
        print("Cancelled. Using placeholder generation instead.")
        print()

        generator = KidsImageGenerator(api_key=api_key)
        num_images = mock_script['target_duration_seconds'] // generator.seconds_per_image
        images = generator.generate_placeholder_images(num_images, mock_script['topic'])
    else:
        print()
        print("Generating images...")
        print()

        try:
            # Generate images
            generator = KidsImageGenerator(api_key=api_key, seconds_per_image=30)
            images = generator.generate_images_from_script(mock_script)

            print()
            print("=" * 80)
            print("GENERATED IMAGES")
            print("=" * 80)

            for i, image_path in enumerate(images, 1):
                print(f"{i}. {image_path}")

            print()
            print(f"✓ Successfully generated {len(images)} images")
            print(f"✓ Saved to: {generator.session_dir}")

        except Exception as e:
            print(f"✗ Error: {e}")
            sys.exit(1)
