"""
YouTube Metadata Generator Module

Generates SEO-friendly YouTube metadata for kids educational videos using AI.

Features:
- SEO-optimized titles (no emojis)
- 2-paragraph descriptions for kids & parents
- 8-12 relevant tags
- Child-friendly language
- No call-to-action text
- Retry logic with error handling
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from openai import OpenAI, OpenAIError
import time


@dataclass
class YouTubeMetadata:
    """YouTube video metadata."""
    title: str
    description: str
    tags: List[str]
    hashtags: List[str] = None  # Hashtags for better reach

    def __post_init__(self):
        """Initialize hashtags if not provided."""
        if self.hashtags is None:
            self.hashtags = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def get_description_with_hashtags(self) -> str:
        """Get description with hashtags appended."""
        desc = self.description
        if self.hashtags:
            # Add hashtags at the end (first 3 appear above title)
            hashtag_text = "\n\n" + " ".join([f"#{tag}" for tag in self.hashtags[:15]])
            desc += hashtag_text
        return desc


class YouTubeMetadataGenerator:
    """
    Generates YouTube metadata for kids educational videos using AI.

    Creates SEO-friendly titles, descriptions, and tags optimized
    for discoverability by both children and parents.
    """

    # Title constraints
    MAX_TITLE_LENGTH = 70      # YouTube recommends 60-70 characters
    MIN_TITLE_LENGTH = 30

    # Description constraints
    MAX_DESCRIPTION_LENGTH = 5000  # YouTube limit
    TARGET_DESCRIPTION_LENGTH = 300  # 2 paragraphs

    # Tags constraints
    MIN_TAGS = 12
    MAX_TAGS = 20
    MAX_TAG_LENGTH = 30

    # Hashtag constraints
    MIN_HASHTAGS = 5
    MAX_HASHTAGS = 15  # YouTube allows up to 15

    # API settings
    MAX_RETRIES = 3
    RETRY_DELAY = 2

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7
    ):
        """
        Initialize the YouTube Metadata Generator.

        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4o-mini)
            temperature: Creativity level (default: 0.7)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.logger = logging.getLogger(__name__)

    def generate_metadata(
        self,
        topic: str,
        script: Optional[Dict[str, Any]] = None
    ) -> YouTubeMetadata:
        """
        Generate complete YouTube metadata for a video.

        Args:
            topic: Video topic or title
            script: Optional script dictionary for context

        Returns:
            YouTubeMetadata: Complete metadata with title, description, tags

        Raises:
            ValueError: If topic is invalid
            RuntimeError: If generation fails after retries
        """
        # Validate input
        if not topic or len(topic.strip()) < 5:
            raise ValueError("Topic must be at least 5 characters long")

        self.logger.info(f"Generating metadata for topic: {topic}")

        # Extract context from script if provided
        context = self._extract_script_context(script) if script else None

        # Generate metadata with retry logic
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                metadata = self._generate_metadata_with_ai(topic, context)

                # Validate and clean metadata
                metadata = self._validate_and_clean(metadata)

                self.logger.info(f"✓ Metadata generated successfully")
                return metadata

            except OpenAIError as e:
                self.logger.error(f"OpenAI API error (attempt {attempt}/{self.MAX_RETRIES}): {e}")

                if attempt < self.MAX_RETRIES:
                    delay = self.RETRY_DELAY * attempt
                    self.logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise RuntimeError(f"Failed to generate metadata after {self.MAX_RETRIES} attempts") from e

            except Exception as e:
                self.logger.error(f"Unexpected error (attempt {attempt}/{self.MAX_RETRIES}): {e}")

                if attempt < self.MAX_RETRIES:
                    delay = self.RETRY_DELAY * attempt
                    time.sleep(delay)
                else:
                    # Return fallback metadata
                    return self._generate_fallback_metadata(topic)

        # Should not reach here
        return self._generate_fallback_metadata(topic)

    def _extract_script_context(self, script: Dict[str, Any]) -> str:
        """
        Extract relevant context from script for metadata generation.

        Args:
            script: Script dictionary

        Returns:
            str: Context summary
        """
        context_parts = []

        # Get intro narration (preview of content)
        if 'intro' in script and 'narration' in script['intro']:
            intro = script['intro']['narration'][:200]
            context_parts.append(f"Intro: {intro}")

        # Get section titles
        if 'body_sections' in script:
            titles = [s.get('title', '') for s in script['body_sections'] if s.get('title')]
            if titles:
                context_parts.append(f"Topics covered: {', '.join(titles)}")

        return " | ".join(context_parts)

    def _generate_metadata_with_ai(
        self,
        topic: str,
        context: Optional[str] = None
    ) -> YouTubeMetadata:
        """
        Generate metadata using OpenAI API.

        Args:
            topic: Video topic
            context: Optional script context

        Returns:
            YouTubeMetadata: Generated metadata
        """
        prompt = self._build_prompt(topic, context)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in YouTube SEO and children's educational content. "
                        "You create engaging, searchable metadata that appeals to both kids and parents. "
                        "Your titles are clear, descriptive, and optimized for search. "
                        "You never use emojis in titles or call-to-action phrases."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=800
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

            data = json.loads(content)

            return YouTubeMetadata(
                title=data['title'],
                description=data['description'],
                tags=data['tags'],
                hashtags=data.get('hashtags', [])
            )

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse AI response as JSON: {e}")
            raise RuntimeError("AI returned invalid JSON format")

    def _build_prompt(self, topic: str, context: Optional[str] = None) -> str:
        """
        Build prompt for metadata generation.

        Args:
            topic: Video topic
            context: Optional context

        Returns:
            str: Complete prompt
        """
        context_section = f"\n\nCONTEXT:\n{context}" if context else ""

        prompt = f"""Generate YouTube metadata for a kids educational video.

TOPIC: {topic}{context_section}

TARGET AUDIENCE: Children aged 4-8 years and their parents
VIDEO TYPE: Educational, family-friendly

REQUIREMENTS:

1. TITLE ({self.MIN_TITLE_LENGTH}-{self.MAX_TITLE_LENGTH} characters):
   - Clear, descriptive, and engaging
   - Include main keywords for SEO
   - Appeal to both kids and parents
   - NO emojis (text only)
   - NO click-bait language
   - Should clearly state what the video is about
   Example: "Why Do Leaves Change Colors? | Science for Kids"

2. DESCRIPTION (2 paragraphs, ~{self.TARGET_DESCRIPTION_LENGTH} characters):
   - First paragraph: Brief overview for kids (simple, exciting)
   - Second paragraph: Educational value for parents (what kids will learn)
   - Include relevant keywords naturally
   - NO call-to-action text (no "subscribe", "like", "comment", etc.)
   - Friendly, informative tone
   - Do NOT include hashtags in description (they will be added separately)

3. TAGS ({self.MIN_TAGS}-{self.MAX_TAGS} tags):
   - Mix of broad and specific tags
   - Include variations of main keywords
   - Age group tags (preschool, kindergarten, early learning)
   - Category tags (science, nature, education, kids learning)
   - Long-tail keywords for better SEO
   - Each tag max {self.MAX_TAG_LENGTH} characters
   - Focus on searchable terms parents and kids use

4. HASHTAGS ({self.MIN_HASHTAGS}-{self.MAX_HASHTAGS} hashtags):
   - Trending educational hashtags
   - Category-specific hashtags (e.g., KidsScience, LearnWithFun)
   - Age-appropriate hashtags (e.g., PreschoolLearning, KidsEducation)
   - General reach hashtags (e.g., EducationalVideos, LearningForKids)
   - Single words or camelCase phrases (no spaces)
   - First 3 hashtags appear above the video title (most important)
   - Mix of popular and niche hashtags for maximum reach
   - Examples: KidsLearning, EducationalContent, ScienceForKids, FunLearning

Return ONLY valid JSON (no markdown, no code blocks):
{{
  "title": "Video Title Here",
  "description": "First paragraph for kids...\\n\\nSecond paragraph for parents...",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12"],
  "hashtags": ["KidsLearning", "EducationalVideos", "ScienceForKids", "FunLearning", "PreschoolEducation"]
}}"""

        return prompt

    def _validate_and_clean(self, metadata: YouTubeMetadata) -> YouTubeMetadata:
        """
        Validate and clean generated metadata.

        Args:
            metadata: Generated metadata

        Returns:
            YouTubeMetadata: Cleaned and validated metadata
        """
        # Clean and validate title
        title = metadata.title.strip()

        # Remove emojis from title
        title = self._remove_emojis(title)

        # Ensure title length
        if len(title) > self.MAX_TITLE_LENGTH:
            title = title[:self.MAX_TITLE_LENGTH-3] + "..."

        if len(title) < self.MIN_TITLE_LENGTH:
            self.logger.warning(f"Title too short: {title}")

        # Clean description
        description = metadata.description.strip()

        # Remove call-to-action phrases
        description = self._remove_cta(description)

        # Ensure description length
        if len(description) > self.MAX_DESCRIPTION_LENGTH:
            description = description[:self.MAX_DESCRIPTION_LENGTH]

        # Clean tags
        tags = []
        for tag in metadata.tags:
            tag = tag.strip().lower()

            # Remove empty or too long tags
            if tag and len(tag) <= self.MAX_TAG_LENGTH:
                tags.append(tag)

        # Ensure we have enough tags
        if len(tags) < self.MIN_TAGS:
            self.logger.warning(f"Only {len(tags)} tags generated, minimum is {self.MIN_TAGS}")

        # Limit to max tags
        tags = tags[:self.MAX_TAGS]

        # Clean hashtags
        hashtags = []
        for hashtag in metadata.hashtags if metadata.hashtags else []:
            hashtag = hashtag.strip().replace('#', '').replace(' ', '')

            # Remove empty or too long hashtags
            if hashtag and len(hashtag) <= 30 and hashtag.isalnum():
                hashtags.append(hashtag)

        # Ensure we have enough hashtags
        if len(hashtags) < self.MIN_HASHTAGS:
            self.logger.warning(f"Only {len(hashtags)} hashtags generated, minimum is {self.MIN_HASHTAGS}")
            # Add default hashtags if needed
            default_hashtags = [
                "KidsEducation", "LearningForKids", "EducationalVideos",
                "KidsLearning", "ChildrensEducation"
            ]
            for tag in default_hashtags:
                if tag not in hashtags and len(hashtags) < self.MIN_HASHTAGS:
                    hashtags.append(tag)

        # Limit to max hashtags
        hashtags = hashtags[:self.MAX_HASHTAGS]

        return YouTubeMetadata(
            title=title,
            description=description,
            tags=tags,
            hashtags=hashtags
        )

    def _remove_emojis(self, text: str) -> str:
        """
        Remove emojis from text.

        Args:
            text: Text with possible emojis

        Returns:
            str: Text without emojis
        """
        # Emoji pattern (covers most emojis)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )

        return emoji_pattern.sub('', text).strip()

    def _remove_cta(self, text: str) -> str:
        """
        Remove call-to-action phrases from text.

        Args:
            text: Text with possible CTAs

        Returns:
            str: Text without CTAs
        """
        # Common CTA phrases to remove
        cta_patterns = [
            r'subscribe\s+to\s+our\s+channel',
            r'don\'t\s+forget\s+to\s+subscribe',
            r'hit\s+the\s+like\s+button',
            r'smash\s+that\s+like\s+button',
            r'leave\s+a\s+comment',
            r'comment\s+below',
            r'share\s+this\s+video',
            r'turn\s+on\s+notifications',
            r'ring\s+the\s+bell',
            r'check\s+out\s+our\s+other\s+videos',
        ]

        for pattern in cta_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def _generate_fallback_metadata(self, topic: str) -> YouTubeMetadata:
        """
        Generate simple fallback metadata if AI fails.

        Args:
            topic: Video topic

        Returns:
            YouTubeMetadata: Fallback metadata
        """
        self.logger.info("Using fallback metadata generation")

        # Simple title
        title = topic
        if len(title) > self.MAX_TITLE_LENGTH:
            title = title[:self.MAX_TITLE_LENGTH-3] + "..."

        # Simple description
        description = (
            f"Learn about {topic.lower()} in this fun educational video for kids! "
            f"Perfect for preschool and early elementary children.\n\n"
            f"This video helps children learn in an engaging and age-appropriate way. "
            f"Great for parents looking for educational content for their kids."
        )

        # Basic tags
        words = topic.lower().split()
        tags = [
            "kids education",
            "learning for kids",
            "educational video",
            "preschool learning",
            "children learning",
            "kids learning",
            "early learning",
            "science for kids"
        ]

        # Add topic-related tags
        tags.extend(words[:4])
        tags = list(set(tags))[:self.MAX_TAGS]

        # Basic hashtags for better reach
        hashtags = [
            "KidsEducation",
            "LearningForKids",
            "EducationalVideos",
            "KidsLearning",
            "ChildrensEducation",
            "FunLearning",
            "ScienceForKids",
            "PreschoolLearning"
        ]

        return YouTubeMetadata(
            title=title,
            description=description,
            tags=tags,
            hashtags=hashtags
        )


def generate_youtube_metadata(
    topic: str,
    script: Optional[Dict[str, Any]] = None,
    api_key: str = None
) -> Dict[str, Any]:
    """
    Convenience function to generate YouTube metadata.

    Args:
        topic: Video topic
        script: Optional script dictionary for context
        api_key: OpenAI API key

    Returns:
        dict: Metadata dictionary with title, description, tags

    Example:
        >>> metadata = generate_youtube_metadata(
        ...     topic="Why Birds Fly South",
        ...     api_key="sk-..."
        ... )
        >>> print(metadata['title'])
        >>> print(metadata['description'])
        >>> print(metadata['tags'])
    """
    generator = YouTubeMetadataGenerator(api_key=api_key)
    metadata = generator.generate_metadata(topic, script)
    return metadata.to_dict()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of the YouTubeMetadataGenerator.
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
    print("YouTube Metadata Generator Demo")
    print("=" * 80)
    print()

    # Example topic and script
    topic = "Why Do Butterflies Have Colorful Wings?"

    mock_script = {
        'topic': topic,
        'intro': {
            'narration': 'Hello friends! Have you ever seen a beautiful butterfly with colorful wings? Today we will learn why butterflies have such amazing colors!'
        },
        'body_sections': [
            {'title': 'What Makes Wings Colorful'},
            {'title': 'Why Butterflies Need Colors'},
            {'title': 'Amazing Butterfly Facts'}
        ]
    }

    print(f"Topic: {topic}")
    print()
    print("Generating metadata...")
    print()

    try:
        # Generate metadata
        generator = YouTubeMetadataGenerator(api_key=api_key)
        metadata = generator.generate_metadata(topic, mock_script)

        print("=" * 80)
        print("GENERATED METADATA")
        print("=" * 80)
        print()

        print("TITLE:")
        print("-" * 80)
        print(metadata.title)
        print(f"({len(metadata.title)} characters)")
        print()

        print("DESCRIPTION:")
        print("-" * 80)
        print(metadata.description)
        print(f"({len(metadata.description)} characters)")
        print()

        print("TAGS:")
        print("-" * 80)
        for i, tag in enumerate(metadata.tags, 1):
            print(f"{i}. {tag}")
        print(f"({len(metadata.tags)} tags)")
        print()

        # Save to file
        output_file = "example_metadata.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(metadata.to_json())

        print("=" * 80)
        print(f"✓ Metadata saved to: {output_file}")
        print("=" * 80)

    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
