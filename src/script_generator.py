"""
Script Generator Module

Generates detailed video scripts from topics using AI.
Creates scene-by-scene breakdowns with narration, timing, and visual descriptions.
"""

import logging
import json
from typing import Dict, Any
from pathlib import Path
from openai import OpenAI


class ScriptGenerator:
    """Generates video scripts from topics using AI."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ScriptGenerator.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger("YouTubeAutomation.ScriptGenerator")
        self.client = OpenAI(api_key=config['api_keys']['openai_api_key'])
        self.prompts_dir = Path(config['paths']['prompts_dir'])

    def generate_script(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete video script from a topic.

        Args:
            topic: Topic dictionary from TopicSelector

        Returns:
            Dictionary containing script information:
            - scenes: List of scene dictionaries
            - narration: Full narration text
            - description: Video description
            - tags: List of tags for YouTube
        """

        self.logger.info(f"Generating script for topic: {topic['title']}")

        # Load script generation prompt template
        prompt = self._build_script_prompt(topic)

        try:
            response = self.client.chat.completions.create(
                model=self.config['ai']['model'],
                messages=[
                    {"role": "system", "content": "You are an expert video scriptwriter for educational YouTube content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config['ai']['temperature'],
                max_tokens=self.config['ai']['max_tokens']
            )

            script_data = json.loads(response.choices[0].message.content)

            # Validate and process script
            script = self._process_script(script_data, topic)

            # Save script for reference
            self._save_script(script, topic)

            self.logger.info(f"Script generated with {len(script['scenes'])} scenes")
            return script

        except Exception as e:
            self.logger.error(f"Error generating script: {e}")
            raise

    def _build_script_prompt(self, topic: Dict[str, Any]) -> str:
        """Build prompt for AI script generation."""

        target_duration = topic.get('target_duration', 180)

        prompt = f"""Create a detailed video script for the following topic:

Title: {topic['title']}
Topic: {topic['topic']}
Target Duration: {target_duration} seconds
Keywords: {', '.join(topic.get('keywords', []))}

Create an engaging script that:
- Has a strong hook in the first 5 seconds
- Is well-structured with clear sections
- Includes interesting facts and information
- Has a natural flow and pacing
- Ends with a call-to-action

Break the script into scenes (approximately 15-30 seconds each).
For each scene, provide:
- Scene number and duration
- Narration text (what will be spoken)
- Visual description (what should be shown on screen)
- Keywords for image/video search

Return ONLY valid JSON (no markdown, no code blocks):
{{
    "title": "Video title",
    "scenes": [
        {{
            "scene_number": 1,
            "duration_seconds": 15,
            "narration": "Text to be spoken",
            "visual_description": "Description of visual content",
            "search_keywords": ["keyword1", "keyword2"]
        }}
    ],
    "description": "YouTube video description (2-3 paragraphs)",
    "tags": ["tag1", "tag2", "tag3"]
}}"""

        return prompt

    def _process_script(self, script_data: Dict[str, Any], topic: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate generated script."""

        # Ensure all required fields exist
        if 'scenes' not in script_data or not script_data['scenes']:
            raise ValueError("Script must contain scenes")

        # Add metadata
        script_data['topic'] = topic
        script_data['total_scenes'] = len(script_data['scenes'])

        # Calculate estimated duration
        total_duration = sum(scene.get('duration_seconds', 15) for scene in script_data['scenes'])
        script_data['estimated_duration'] = total_duration

        # Combine all narration
        full_narration = " ".join(scene.get('narration', '') for scene in script_data['scenes'])
        script_data['full_narration'] = full_narration

        return script_data

    def _save_script(self, script: Dict[str, Any], topic: Dict[str, Any]) -> None:
        """Save generated script to file for reference."""

        try:
            self.prompts_dir.mkdir(exist_ok=True)

            timestamp = topic.get('timestamp', '').replace(':', '-').split('.')[0]
            script_file = self.prompts_dir / f"script_{timestamp}.json"

            with open(script_file, 'w', encoding='utf-8') as f:
                json.dump(script, f, indent=2, ensure_ascii=False)

            self.logger.debug(f"Script saved to {script_file}")

        except Exception as e:
            self.logger.warning(f"Error saving script: {e}")
