"""
Kids Video Script Generator Module

Generates structured narration scripts for 3-15 minute kids YouTube videos
with simple language, friendly tone, and clear sections.

Features:
- Structured outline (intro, body sections, ending)
- Full narration text optimized for text-to-speech
- Simple English for ages 4-8
- Duration-aware content generation
- Clean JSON output for automation
"""

import logging
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from openai import OpenAI, OpenAIError


@dataclass
class ScriptSection:
    """Represents a single section of the video script."""
    section_number: int
    title: str
    duration_seconds: int
    narration: str
    visual_suggestions: List[str]


@dataclass
class VideoScript:
    """Complete video script with metadata and sections."""
    topic: str
    target_duration_seconds: int
    total_sections: int
    intro: ScriptSection
    body_sections: List[ScriptSection]
    outro: ScriptSection
    full_narration: str
    estimated_word_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'topic': self.topic,
            'target_duration_seconds': self.target_duration_seconds,
            'total_sections': self.total_sections,
            'intro': asdict(self.intro),
            'body_sections': [asdict(section) for section in self.body_sections],
            'outro': asdict(self.outro),
            'full_narration': self.full_narration,
            'estimated_word_count': self.estimated_word_count
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class KidsScriptGenerator:
    """
    Generates kid-friendly video scripts using OpenAI API.

    Creates structured narration with:
    - Engaging intro (hook + topic introduction)
    - 3-5 educational body sections
    - Memorable outro (recap + call-to-action)
    """

    # Words per minute for narration (slower for kids)
    WORDS_PER_MINUTE = 120

    # Section duration limits
    MIN_SECTION_DURATION = 20
    MAX_SECTION_DURATION = 90

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        min_duration: int = 180,
        max_duration: int = 900,
        language: str = "en"
    ):
        """
        Initialize the Kids Script Generator.

        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4o-mini)
            temperature: Creativity level 0.0-2.0 (default: 0.7)
            min_duration: Minimum video duration in seconds (default: 180)
            max_duration: Maximum video duration in seconds (default: 900)
            language: Language code (en, hi, es, fr, de, pt, ar, ja, ko, zh)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.language = language
        self.logger = logging.getLogger(__name__)

        # Language names for prompts
        self.language_names = {
            'en': 'English',
            'hi': 'Hindi (हिंदी)',
            'es': 'Spanish (Español)',
            'fr': 'French (Français)',
            'de': 'German (Deutsch)',
            'pt': 'Portuguese (Português)',
            'ar': 'Arabic (العربية)',
            'ja': 'Japanese (日本語)',
            'ko': 'Korean (한국어)',
            'zh': 'Chinese (中文)'
        }

    def generate_script(
        self,
        topic: str,
        target_duration: Optional[int] = None
    ) -> VideoScript:
        """
        Generate a complete video script for the given topic.

        Args:
            topic: Video topic string
            target_duration: Target duration in seconds (uses default if None)

        Returns:
            VideoScript: Complete structured script

        Raises:
            ValueError: If topic is invalid or duration out of range
            RuntimeError: If script generation fails
        """
        # Validate inputs
        if not topic or len(topic.strip()) < 5:
            raise ValueError("Topic must be at least 5 characters long")

        if target_duration is None:
            target_duration = (self.min_duration + self.max_duration) // 2

        if target_duration < self.min_duration or target_duration > self.max_duration:
            raise ValueError(
                f"Duration must be between {self.min_duration} and {self.max_duration} seconds"
            )

        self.logger.info(f"Generating script for topic: {topic}")
        self.logger.info(f"Target duration: {target_duration} seconds")

        try:
            # Calculate content structure
            structure = self._calculate_structure(target_duration)

            # Generate script content using AI
            script_data = self._generate_script_with_ai(topic, target_duration, structure)

            # Parse and structure the response
            video_script = self._parse_script_response(topic, target_duration, script_data)

            self.logger.info(f"Script generated: {video_script.total_sections} sections, "
                           f"{video_script.estimated_word_count} words")

            return video_script

        except OpenAIError as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"Failed to generate script: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise RuntimeError(f"Script generation failed: {e}") from e

    def _calculate_structure(self, duration: int) -> Dict[str, Any]:
        """
        Calculate optimal script structure based on duration.

        Args:
            duration: Target duration in seconds

        Returns:
            dict: Structure with section counts and durations
        """
        # Intro: 10-15% of video
        intro_duration = max(15, int(duration * 0.12))

        # Outro: 8-12% of video
        outro_duration = max(15, int(duration * 0.10))

        # Body: remaining time
        body_duration = duration - intro_duration - outro_duration

        # Number of body sections (3-5 based on duration)
        if duration <= 240:  # Up to 4 minutes
            body_sections = 3
        elif duration <= 480:  # 4-8 minutes
            body_sections = 4
        else:  # 8+ minutes
            body_sections = 5

        # Duration per body section
        section_duration = body_duration // body_sections

        return {
            'intro_duration': intro_duration,
            'outro_duration': outro_duration,
            'body_sections': body_sections,
            'section_duration': section_duration,
            'total_words': int((duration / 60) * self.WORDS_PER_MINUTE)
        }

    def _generate_script_with_ai(
        self,
        topic: str,
        duration: int,
        structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate script content using OpenAI API.

        Args:
            topic: Video topic
            duration: Target duration in seconds
            structure: Script structure parameters

        Returns:
            dict: AI-generated script data
        """
        prompt = self._build_prompt(topic, duration, structure)

        # Build language-specific system message
        language_name = self.language_names.get(self.language, 'English')
        language_instruction = ""
        if self.language != 'en':
            language_instruction = f" Write the ENTIRE script in {language_name}. Do not use English."

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        # CREATE Formula: Character
                        "CHARACTER: You are a world-class children's educational scriptwriter "
                        "with 15 years of experience writing for PBS Kids, Sesame Street, "
                        f"and top YouTube educational channels.{language_instruction} "
                        # CREATE Formula: Adjustments
                        "ADJUSTMENTS: Your writing style uses short sentences (5-10 words), "
                        "grade 1-2 vocabulary, present tense, and a warm conversational tone. "
                        "You never use complex words, violence, fear, or copyrighted characters. "
                        # CREATE Formula: Extras
                        "EXTRAS: Every script you write scores 95%+ on readability for ages 4-8, "
                        "sounds like a real parent/teacher talking naturally (NOT robotic), "
                        "uses varied vocabulary without repeating enthusiastic words like 'wow' or 'amazing', "
                        "and naturally includes pauses via punctuation for voiceover timing."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=3000
        )

        content = response.choices[0].message.content.strip()

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            script_data = json.loads(content)
            return script_data

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse AI response as JSON: {e}")
            raise RuntimeError("AI returned invalid JSON format")

    def _build_prompt(
        self,
        topic: str,
        duration: int,
        structure: Dict[str, Any]
    ) -> str:
        """
        Build the prompt for script generation.

        Args:
            topic: Video topic
            duration: Target duration
            structure: Script structure

        Returns:
            str: Complete prompt for OpenAI
        """
        minutes = duration // 60
        language_name = self.language_names.get(self.language, 'English')
        language_instruction = ""
        if self.language != 'en':
            language_instruction = f"\n\n🌐 IMPORTANT: Write the ENTIRE script in {language_name}. The narration text, titles, and visual suggestions must ALL be in {language_name}, not English."

        prompt = f"""=== CREATE FORMULA PROMPT ===

[C] CHARACTER:
You are a top children's educational scriptwriter creating narration for a YouTube kids video.

[R] REQUEST:
Write a complete narration script for this video topic:
TOPIC: {topic}{language_instruction}

Video specs: {minutes} minutes ({duration} seconds), ~{structure['total_words']} words total.

[E] EXAMPLES:
Here is the quality and style to follow (sound NATURAL like real human speech):
- Hook: "Hey friends! Have you ever looked up at the sky and wondered... why is it blue?"
- Teaching: "The sky looks blue because of tiny bits of light. Cool, right?"
- Natural Questions: "What do you think happens next?" or "Can you see it?"
- Outro: "Great job learning today! You did so well. I'll see you again next time!"

[A] ADJUSTMENTS:
- Sentences: 5-10 words each, grade 1-2 reading level
- Tone: Warm, friendly, conversational (like a real parent talking to their child)
- Natural Speech: Sound like REAL human conversation - vary your words, don't repeat "wow", "amazing", "wonderful" etc.
- Engagement: Use natural questions like "What do you think?" "Can you see it?" "Let me show you!"
- Pauses: Use periods and commas naturally for voiceover breathing
- AVOID AI Clichés: Don't overuse "awesome", "incredible", "fantastic" - sound like a real person
- NEVER use: complex vocabulary, scary topics, copyrighted characters, brand names
- Structure:
  * INTRO ({structure['intro_duration']}s): Exciting hook + introduce topic + build curiosity
  * BODY ({structure['body_sections']} sections x ~{structure['section_duration']}s): One key idea per section with questions
  * OUTRO ({structure['outro_duration']}s): Recap + positive message + gentle encouragement

[T] TYPE OF OUTPUT:
Return ONLY valid JSON (no markdown, no code blocks) in this exact format:
{{
  "intro": {{
    "title": "Introduction",
    "duration_seconds": {structure['intro_duration']},
    "narration": "Full narration text for intro...",
    "visual_suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"]
  }},
  "body_sections": [
    {{
      "section_number": 1,
      "title": "Section title",
      "duration_seconds": {structure['section_duration']},
      "narration": "Full narration text...",
      "visual_suggestions": ["visual 1", "visual 2", "visual 3"]
    }}
  ],
  "outro": {{
    "title": "Conclusion",
    "duration_seconds": {structure['outro_duration']},
    "narration": "Full narration text for outro...",
    "visual_suggestions": ["suggestion 1", "suggestion 2"]
  }}
}}

[E] EXTRAS:
- Each body section MUST have exactly 3 visual_suggestions describing what to show on screen
- Visual suggestions should be specific and descriptive (e.g., "A happy cartoon elephant splashing in water" not just "elephant")
- Narration word count per section should match the duration (roughly 2.5 words per second)
- Make the intro hook irresistible - kids should want to keep watching

Generate the script now:"""

        return prompt

    def _parse_script_response(
        self,
        topic: str,
        target_duration: int,
        script_data: Dict[str, Any]
    ) -> VideoScript:
        """
        Parse AI response into VideoScript object.

        Args:
            topic: Video topic
            target_duration: Target duration
            script_data: Parsed JSON from AI

        Returns:
            VideoScript: Structured script object
        """
        # Parse intro
        intro_data = script_data['intro']
        intro = ScriptSection(
            section_number=0,
            title=intro_data.get('title', 'Introduction'),
            duration_seconds=intro_data['duration_seconds'],
            narration=intro_data['narration'].strip(),
            visual_suggestions=intro_data.get('visual_suggestions', [])
        )

        # Parse body sections
        body_sections = []
        for section_data in script_data['body_sections']:
            section = ScriptSection(
                section_number=section_data['section_number'],
                title=section_data['title'],
                duration_seconds=section_data['duration_seconds'],
                narration=section_data['narration'].strip(),
                visual_suggestions=section_data.get('visual_suggestions', [])
            )
            body_sections.append(section)

        # Parse outro
        outro_data = script_data['outro']
        outro = ScriptSection(
            section_number=len(body_sections) + 1,
            title=outro_data.get('title', 'Conclusion'),
            duration_seconds=outro_data['duration_seconds'],
            narration=outro_data['narration'].strip(),
            visual_suggestions=outro_data.get('visual_suggestions', [])
        )

        # Combine full narration
        full_narration = self._combine_narration([intro] + body_sections + [outro])

        # Calculate word count
        word_count = len(full_narration.split())

        # Create VideoScript object
        video_script = VideoScript(
            topic=topic,
            target_duration_seconds=target_duration,
            total_sections=len(body_sections) + 2,  # intro + body + outro
            intro=intro,
            body_sections=body_sections,
            outro=outro,
            full_narration=full_narration,
            estimated_word_count=word_count
        )

        return video_script

    def _combine_narration(self, sections: List[ScriptSection]) -> str:
        """
        Combine narration from all sections into single text.

        Args:
            sections: List of script sections

        Returns:
            str: Combined narration text
        """
        narration_parts = [section.narration for section in sections]
        return "\n\n".join(narration_parts)

    def estimate_duration(self, text: str) -> int:
        """
        Estimate narration duration from text.

        Args:
            text: Narration text

        Returns:
            int: Estimated duration in seconds
        """
        word_count = len(text.split())
        duration_seconds = int((word_count / self.WORDS_PER_MINUTE) * 60)
        return duration_seconds


def generate_kids_script(
    topic: str,
    api_key: str,
    duration: int = 300,
    model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """
    Convenience function to generate a kids video script.

    Args:
        topic: Video topic
        api_key: OpenAI API key
        duration: Target duration in seconds (default: 300 = 5 minutes)
        model: OpenAI model to use

    Returns:
        dict: Script data as dictionary

    Example:
        >>> script = generate_kids_script(
        ...     "Why Do We Have Day and Night?",
        ...     api_key="sk-...",
        ...     duration=240
        ... )
        >>> print(script['full_narration'])
    """
    generator = KidsScriptGenerator(api_key=api_key, model=model)
    video_script = generator.generate_script(topic, target_duration=duration)
    return video_script.to_dict()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of the KidsScriptGenerator.
    """
    import os
    import sys

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
    print("Kids Video Script Generator Demo")
    print("=" * 80)
    print()

    # Example topic
    topic = "Why Do Birds Fly South for the Winter?"
    duration = 240  # 4 minutes

    print(f"Topic: {topic}")
    print(f"Target Duration: {duration // 60} minutes ({duration} seconds)")
    print()
    print("Generating script...")
    print()

    try:
        # Generate script
        generator = KidsScriptGenerator(api_key=api_key)
        script = generator.generate_script(topic, target_duration=duration)

        # Display results
        print("=" * 80)
        print("GENERATED SCRIPT")
        print("=" * 80)
        print()

        # Show structure
        print(f"Topic: {script.topic}")
        print(f"Total Sections: {script.total_sections}")
        print(f"Word Count: {script.estimated_word_count}")
        print(f"Estimated Duration: {script.target_duration_seconds}s")
        print()

        # Show intro
        print("-" * 80)
        print(f"INTRO ({script.intro.duration_seconds}s)")
        print("-" * 80)
        print(script.intro.narration)
        print()

        # Show body sections
        for section in script.body_sections:
            print("-" * 80)
            print(f"SECTION {section.section_number}: {section.title} ({section.duration_seconds}s)")
            print("-" * 80)
            print(section.narration)
            print()

        # Show outro
        print("-" * 80)
        print(f"OUTRO ({script.outro.duration_seconds}s)")
        print("-" * 80)
        print(script.outro.narration)
        print()

        # Save to file
        output_file = "example_script.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(script.to_json())

        print("=" * 80)
        print(f"✓ Script saved to: {output_file}")
        print("=" * 80)

    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
