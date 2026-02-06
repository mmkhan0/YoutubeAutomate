"""
Thumbnail Generator Module

Generates attractive thumbnails for YouTube videos.
Uses PIL (Pillow) to create custom thumbnails with text overlay.
"""

import logging
from typing import Dict, Any
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap


class ThumbnailGenerator:
    """Generates YouTube thumbnails for videos."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ThumbnailGenerator.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger("YouTubeAutomation.ThumbnailGenerator")
        self.thumbnail_dir = Path(config['paths']['thumbnail_dir'])
        self.assets_dir = Path(config['paths']['assets_dir'])

        # Ensure thumbnail directory exists
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)

    def generate_thumbnail(self, topic: Dict[str, Any], script: Dict[str, Any]) -> str:
        """
        Generate a thumbnail for the video.

        Args:
            topic: Topic dictionary
            script: Script dictionary

        Returns:
            Path to generated thumbnail image
        """

        self.logger.info("Generating thumbnail...")

        try:
            # Create thumbnail image
            thumbnail = self._create_thumbnail_image(topic['title'], script)

            # Save thumbnail
            timestamp = topic.get('timestamp', '').replace(':', '-').split('.')[0]
            thumbnail_path = self.thumbnail_dir / f"thumbnail_{timestamp}.jpg"

            thumbnail.save(thumbnail_path, 'JPEG', quality=95)

            self.logger.info(f"Thumbnail generated: {thumbnail_path}")
            return str(thumbnail_path)

        except Exception as e:
            self.logger.error(f"Error generating thumbnail: {e}")
            raise

    def _create_thumbnail_image(self, title: str, script: Dict[str, Any]) -> Image.Image:
        """
        Create thumbnail image with title text overlay.

        Args:
            title: Video title
            script: Script dictionary

        Returns:
            PIL Image object
        """

        # YouTube thumbnail size: 1280x720
        width, height = 1280, 720

        # Create base image with gradient background
        thumbnail = self._create_gradient_background(width, height)

        # Add text overlay
        self._add_text_overlay(thumbnail, title)

        # Add decorative elements
        self._add_decorative_elements(thumbnail)

        return thumbnail

    def _create_gradient_background(self, width: int, height: int) -> Image.Image:
        """
        Create bright, kid-friendly gradient background for thumbnail.

        Args:
            width: Image width
            height: Image height

        Returns:
            PIL Image with gradient
        """

        # Create vibrant gradient for kids appeal
        base = Image.new('RGB', (width, height), color=(255, 100, 100))
        draw = ImageDraw.Draw(base)

        # Create bright gradient effect (orange to pink)
        for i in range(height):
            # Interpolate between bright colors
            r = int(255 - (80 * i / height))   # 255 -> 175 (bright red to pink)
            g = int(140 - (50 * i / height))   # 140 -> 90 (orange to dimmer)
            b = int(70 + (130 * i / height))   # 70 -> 200 (orange to pink)

            draw.line([(0, i), (width, i)], fill=(r, g, b))

        return base

    def _add_text_overlay(self, image: Image.Image, title: str) -> None:
        """
        Add title text overlay to thumbnail.

        Args:
            image: PIL Image to draw on (modified in place)
            title: Video title text
        """

        draw = ImageDraw.Draw(image)

        # Try to load a nice font, fallback to default
        try:
            # Try to find a bold font
            font_paths = [
                "C:/Windows/Fonts/arialbd.ttf",  # Arial Bold
                "C:/Windows/Fonts/arial.ttf",     # Arial
            ]

            font = None
            for font_path in font_paths:
                if Path(font_path).exists():
                    font = ImageFont.truetype(font_path, 80)
                    break

            if font is None:
                font = ImageFont.load_default()

        except Exception:
            font = ImageFont.load_default()

        # Wrap text to fit thumbnail
        wrapped_text = textwrap.fill(title, width=20)

        # Calculate text position (centered)
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (image.width - text_width) // 2
        y = (image.height - text_height) // 2

        # Draw text shadow for better readability
        shadow_offset = 4
        draw.text(
            (x + shadow_offset, y + shadow_offset),
            wrapped_text,
            font=font,
            fill=(0, 0, 0),
            align='center'
        )

        # Draw main text in white
        draw.text(
            (x, y),
            wrapped_text,
            font=font,
            fill=(255, 255, 255),
            align='center'
        )

    def _add_decorative_elements(self, image: Image.Image) -> None:
        """
        Add decorative elements to thumbnail.

        Args:
            image: PIL Image to modify (modified in place)
        """

        draw = ImageDraw.Draw(image)

        # Add bright border for kids appeal
        line_color = (255, 255, 0)  # Bright yellow
        line_width = 12

        # Full border
        draw.rectangle(
            [(line_width//2, line_width//2),
             (image.width - line_width//2, image.height - line_width//2)],
            outline=line_color,
            width=line_width
        )

        # Add age badge (Ages 2-6) in top right
        try:
            badge_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 40)
        except:
            badge_font = ImageFont.load_default()

        badge_text = "Ages 2-6"
        badge_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        badge_width = badge_bbox[2] - badge_bbox[0] + 40
        badge_height = badge_bbox[3] - badge_bbox[1] + 20

        # Badge position (top-right)
        badge_x = image.width - badge_width - 30
        badge_y = 30

        # Draw badge background
        draw.rounded_rectangle(
            [(badge_x, badge_y), (badge_x + badge_width, badge_y + badge_height)],
            radius=15,
            fill=(255, 215, 0),  # Gold
            outline=(255, 140, 0),  # Dark orange border
            width=3
        )

        # Draw badge text
        text_x = badge_x + 20
        text_y = badge_y + 10
        draw.text((text_x, text_y), badge_text, font=badge_font, fill=(0, 0, 0))
