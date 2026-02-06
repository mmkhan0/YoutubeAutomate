"""
Kids-Friendly Topic Selector Module

Automatically selects safe, educational, and age-appropriate video topics
for children aged 4-8 years using OpenAI API.

Features:
- Evergreen educational content
- Story-based themes
- No copyrighted characters or brands
- Retry logic with exponential backoff
- Error handling
"""

import logging
import time
import json
from typing import Optional
from openai import OpenAI, OpenAIError


class KidsTopicSelector:
    """
    Selects technology and science video topics for educational content.

    Focuses on:
    - How computers and technology work
    - Internet, WiFi, and digital communication
    - Artificial Intelligence and machine learning
    - Robotics and automation
    - Smartphones, apps, and devices
    - Programming and coding concepts
    - Energy, batteries, and power systems
    - Gaming technology and 3D graphics

    Avoids:
    - Specific brand names (Apple, Google, Microsoft products)
    - Copyrighted content
    - Complex technical jargon
    - Product reviews or comparisons
    """

    # Age range for content
    MIN_AGE = 4
    MAX_AGE = 8

    # Maximum retry attempts for API calls
    MAX_RETRIES = 3

    # Initial retry delay in seconds
    RETRY_DELAY = 1

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.8, category: str = 'auto'):
        """
        Initialize the topic selector.

        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4o-mini)
            temperature: Creativity level 0.0-2.0 (default: 0.8 for variety)
            category: Video category ('tech', 'kids', 'science', or 'auto')
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.category = category
        self.logger = logging.getLogger(__name__)

    def select_topic(self) -> str:
        """
        Select a single kids-friendly video topic.

        Returns:
            str: A video topic suitable for ages 4-8

        Raises:
            RuntimeError: If topic selection fails after all retries
        """
        self.logger.info(f"Selecting {self.category} topic for educational content")

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                topic = self._generate_topic_with_ai()

                # Validate the topic
                if self._is_valid_topic(topic):
                    self.logger.info(f"Selected topic: {topic}")
                    return topic
                else:
                    self.logger.warning(f"Invalid topic generated: {topic}. Retrying...")
                    continue

            except OpenAIError as e:
                self.logger.error(f"OpenAI API error (attempt {attempt}/{self.MAX_RETRIES}): {e}")

                if attempt < self.MAX_RETRIES:
                    delay = self.RETRY_DELAY * (2 ** (attempt - 1))  # Exponential backoff
                    self.logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    # Use fallback topic if all attempts failed
                    self.logger.warning("All API attempts failed, using fallback topic")
                    return self._get_fallback_topic()

            except Exception as e:
                self.logger.error(f"Unexpected error (attempt {attempt}/{self.MAX_RETRIES}): {e}")

                if attempt < self.MAX_RETRIES:
                    delay = self.RETRY_DELAY * (2 ** (attempt - 1))
                    time.sleep(delay)
                else:
                    # Fallback to safe default topic
                    return self._get_fallback_topic()

        # Should not reach here, but provide fallback
        return self._get_fallback_topic()

    def _generate_topic_with_ai(self) -> str:
        """
        Generate a topic using OpenAI API.

        Returns:
            str: Generated topic
        """
        prompt = self._build_prompt()
        system_message = self._get_system_message()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=100
        )

        topic = response.choices[0].message.content.strip()

        # Remove quotes if present
        topic = topic.strip('"\'')

        return topic

    def _get_system_message(self) -> str:
        """
        Get the system message based on category.

        Returns:
            str: System message for OpenAI
        """
        if self.category == 'tech':
            return (
                # CREATE Formula: Character + Adjustments + Extras
                "CHARACTER: You are a senior technology educator and viral YouTube content strategist "
                "with 10 years of experience creating tech-explainer videos that get millions of views. "
                "ADJUSTMENTS: You specialize in breaking down complex technology concepts into "
                "simple, visual explanations suitable for all ages. "
                "EXTRAS: You never suggest copyrighted characters or branded content. "
                "You always pick evergreen topics with high search volume."
            )
        elif self.category == 'kids':
            return (
                "CHARACTER: You are a children's educational content strategist with 15 years "
                "creating safe, engaging video topics for preschool and early elementary children (ages 4-8). "
                "ADJUSTMENTS: You focus on animals, nature, colors, numbers, and basic science concepts "
                "that spark curiosity and joy. "
                "EXTRAS: You NEVER suggest copyrighted characters (Disney, Marvel, Nickelodeon, etc.) "
                "or branded content. Topics must be evergreen and parent-approved."
            )
        elif self.category == 'science':
            return (
                "CHARACTER: You are a science communication expert and viral educational "
                "content creator with a talent for making physics, chemistry, and biology "
                "fascinating and simple for any age. "
                "ADJUSTMENTS: You translate complex scientific concepts into visual, "
                "easy-to-understand explanations. "
                "EXTRAS: You never suggest copyrighted characters or branded content. "
                "Your topics always pass the 'I never knew that!' test."
            )
        else:  # auto
            return (
                "CHARACTER: You are a versatile educational content strategist who creates "
                "engaging video topics across technology, science, nature, and how things work. "
                "ADJUSTMENTS: You focus on educational content suitable for all ages "
                "with high search potential on YouTube. "
                "EXTRAS: You never suggest copyrighted characters or branded content. "
                "You prioritize topics with proven viewer interest."
            )

    def _build_prompt(self) -> str:
        """
        Build the prompt for topic generation based on category.

        Returns:
            str: Prompt for OpenAI
        """
        if self.category == 'tech':
            return self._build_tech_prompt()
        elif self.category == 'kids':
            return self._build_kids_prompt()
        elif self.category == 'science':
            return self._build_science_prompt()
        else:  # auto
            return self._build_tech_prompt()  # Default to tech

    def _build_tech_prompt(self) -> str:
        """Build tech category prompt."""
        return f"""=== CREATE FORMULA PROMPT ===

[C] CHARACTER:
You are a senior tech education YouTuber who selects viral-worthy video topics.

[R] REQUEST:
Generate ONE educational and engaging YouTube video topic about TECHNOLOGY, COMPUTERS, or HOW THINGS WORK.

[E] EXAMPLES:
- "How Does a Computer Process Information?"
- "How Does WiFi Send Data Through the Air?"
- "What is AI and How Do Computers Learn?"
- "How Do Robots See and Move Around?"
- "How Does a Touchscreen Know Where You Touch?"
- "How Are Video Games Created and Programmed?"
- "How Do Batteries Store and Release Energy?"
- "How Do Video Calls Work Across the World?"
- "What is Programming and How Does Code Work?"
- "What is Virtual Reality and How Does It Work?"

[A] ADJUSTMENTS:
- Must be educational and informative about technology/science
- Evergreen content (not tied to trends or specific products)
- Explain how technology works in simple terms
- NO copyrighted characters or specific brand names
- Should be clear and specific (50-70 characters)

[T] TYPE OF OUTPUT:
Return ONLY the video topic as a single line of text. No explanations, no quotes, just the topic.

[E] EXTRAS:
- Pick a topic with high YouTube search volume
- Think about what people actually search for

Topic:"""

    def _build_kids_prompt(self) -> str:
        """Build kids category prompt."""
        return f"""=== CREATE FORMULA PROMPT ===

[C] CHARACTER:
You are a children's content strategist selecting the perfect video topic for kids aged 4-8.

[R] REQUEST:
Generate ONE educational and engaging YouTube video topic for young children.

[E] EXAMPLES:
- "How Do Dolphins Talk to Each Other?"
- "Learning to Count from 1 to 20 with Fun Objects"
- "Finding Shapes in Nature - A Fun Adventure"
- "Why Do Leaves Change Colors?"
- "The Story of the Kind Little Turtle"
- "Amazing Facts About Butterflies"
- "Why Do We Need to Sleep?"
- "The Morning Routine Song"

[A] ADJUSTMENTS:
- Must be educational, entertaining, or story-based
- Evergreen content (not tied to trends or seasons)
- Safe for young children (no violence, fear, or complex topics)
- NO copyrighted characters (no Disney, Marvel, Nickelodeon, etc.)
- NO brand names or products
- Should be clear and specific (50-70 characters)

[T] TYPE OF OUTPUT:
Return ONLY the video topic as a single line of text. No explanations, no quotes, just the topic.

[E] EXTRAS:
- Focus on topics that make kids say "wow!" or "why?"
- Parents should feel good about their child watching this

Topic:"""

    def _build_science_prompt(self) -> str:
        """Build science category prompt."""
        return f"""=== CREATE FORMULA PROMPT ===

[C] CHARACTER:
You are a science communicator selecting a captivating video topic about how nature and science work.

[R] REQUEST:
Generate ONE educational and engaging YouTube video topic about SCIENCE and HOW NATURE WORKS.

[E] EXAMPLES:
- "How Does Gravity Keep Us on the Ground?"
- "What Happens When Ice Melts? The Science of States"
- "How Do Plants Make Food from Sunlight?"
- "Why Do We Have Seasons? Earth's Tilt Explained"
- "How Are Clouds Formed in the Sky?"
- "Why Does the Moon Change Shape? Lunar Phases"
- "The Water Cycle: From Rain to Rivers to Clouds"
- "How Do Our Eyes See Colors?"
- "What is Energy and Where Does It Come From?"
- "Why Do We See Rainbows After Rain?"

[A] ADJUSTMENTS:
- Must be educational and informative about scientific concepts
- Evergreen content (not tied to trends or specific products)
- Explain science in simple, understandable terms
- NO copyrighted characters or specific brand names
- Should be clear and specific (50-70 characters)

[T] TYPE OF OUTPUT:
Return ONLY the video topic as a single line of text. No explanations, no quotes, just the topic.

[E] EXTRAS:
- Pick a topic that triggers curiosity and the "I never knew that!" reaction
- Ensure the topic can be visually explained in a video

Topic:"""

    def _is_valid_topic(self, topic: str) -> bool:
        """
        Validate that a topic is safe and appropriate.

        Args:
            topic: Topic string to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not topic or len(topic) < 10:
            return False

        if len(topic) > 100:
            return False

        # Check for banned terms (copyrighted characters and brands)
        banned_terms = [
            'disney', 'marvel', 'mickey', 'minnie', 'elsa', 'frozen', 'spider-man', 'spiderman',
            'batman', 'superman', 'peppa pig', 'paw patrol', 'pokemon', 'sonic',
            'mario', 'luigi', 'fortnite', 'minecraft', 'roblox', 'youtube',
            'coca-cola', 'mcdonalds', 'burger king', 'nike', 'adidas',
            'barbie', 'mattel', 'lego', 'hasbro', 'nerf', 'hot wheels',
            'dora', 'spongebob', 'transformers', 'star wars', 'harry potter'
        ]

        topic_lower = topic.lower()

        for term in banned_terms:
            if term in topic_lower:
                self.logger.warning(f"Topic contains banned term '{term}': {topic}")
                return False

        return True

    def _get_fallback_topic(self) -> str:
        """
        Get a safe fallback topic if AI generation fails.

        Returns:
            str: Safe default topic
        """
        import random

        if self.category == 'tech':
            fallback_topics = [
                "How Does the Internet Work? A Simple Explanation",
                "What Happens Inside a Computer When You Click?",
                "How Do Smartphones Know Your Location with GPS?",
                "The Amazing World of Artificial Intelligence Explained",
                "How Do Video Games Create 3D Worlds?",
                "What is Cloud Computing and Where is the Cloud?",
                "How Do Robots Work and Move Around?",
                "The Science Behind Touchscreens and How They Work",
                "How Does WiFi Send Data Through the Air?",
                "What is Coding? Understanding Computer Programming",
                "How Do Batteries Store and Release Energy?",
                "The Technology Behind Virtual Reality Headsets",
                "How Do Search Engines Find Information So Fast?",
                "Understanding How Computer Memory and Storage Work",
                "How Do Electric Cars Work Without Gasoline?"
            ]
        elif self.category == 'kids':
            fallback_topics = [
                "Learning Colors with Fruits and Vegetables",
                "Counting from 1 to 10 with Friendly Animals",
                "The Story of a Brave Little Seed",
                "How Do Birds Build Their Nests?",
                "Fun Facts About Ocean Animals",
                "Why Do We Have Day and Night?",
                "The Adventure of the Curious Caterpillar",
                "Learning Shapes Around Our House",
                "How Do Flowers Grow?",
                "The Story of Sharing and Kindness",
                "Amazing Facts About Baby Animals",
                "Why Do We Brush Our Teeth?",
                "The Life Cycle of a Butterfly",
                "Learning About Different Weather Types",
                "The Tale of the Helpful Little Ant"
            ]
        elif self.category == 'science':
            fallback_topics = [
                "The Water Cycle: From Rain to Rivers to Clouds",
                "How Do Plants Make Food from Sunlight?",
                "Why Do We Have Seasons? Earth's Tilt Explained",
                "How Are Clouds Formed in the Sky?",
                "What is Gravity and How Does It Work?",
                "The Amazing Journey of a Raindrop",
                "Why Does the Moon Change Shape?",
                "How Do Our Eyes See Colors?",
                "What Makes Thunder and Lightning?",
                "The Science of Melting Ice: States of Matter",
                "How Do Magnets Attract and Repel?",
                "Why Do Leaves Change Color in Fall?",
                "The Life Cycle of a Star in Space",
                "How Do Volcanoes Form and Erupt?",
                "What is Energy and Where Does It Come From?"
            ]
        else:  # auto
            fallback_topics = [
                "How Does the Internet Work? A Simple Explanation",
                "The Water Cycle: From Rain to Rivers to Clouds",
                "Learning Colors with Fruits and Vegetables",
                "How Do Smartphones Know Your Location with GPS?",
                "Why Do We Have Seasons? Earth's Tilt Explained",
                "How Do Video Games Create 3D Worlds?",
                "Fun Facts About Ocean Animals",
                "What is AI and How Do Computers Learn?",
                "How Do Plants Make Food from Sunlight?",
                "Learning to Count from 1 to 20"
            ]

        topic = random.choice(fallback_topics)
        self.logger.info(f"Using fallback topic: {topic}")

        return topic

    def select_multiple_topics(self, count: int = 5) -> list:
        """
        Select multiple unique topics at once.

        Args:
            count: Number of topics to generate (default: 5)

        Returns:
            list: List of unique topic strings
        """
        topics = []
        attempts = 0
        max_attempts = count * 3  # Allow some retries

        while len(topics) < count and attempts < max_attempts:
            try:
                topic = self.select_topic()

                # Ensure uniqueness
                if topic not in topics:
                    topics.append(topic)

                attempts += 1

                # Small delay between requests to avoid rate limits
                if len(topics) < count:
                    time.sleep(0.5)

            except Exception as e:
                self.logger.error(f"Error generating topic: {e}")
                attempts += 1

        if len(topics) < count:
            self.logger.warning(f"Only generated {len(topics)} of {count} requested topics")

        return topics


def select_kids_topic(api_key: str, model: str = "gpt-4o-mini") -> str:
    """
    Simple function to select a kids-friendly topic.

    Args:
        api_key: OpenAI API key
        model: OpenAI model to use (default: gpt-4o-mini)

    Returns:
        str: A kids-friendly video topic

    Example:
        >>> topic = select_kids_topic("sk-...")
        >>> print(topic)
        "Learning to Count with Colorful Butterflies"
    """
    selector = KidsTopicSelector(api_key=api_key, model=model)
    return selector.select_topic()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of the KidsTopicSelector.
    """
    import os
    import sys

    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Usage: set OPENAI_API_KEY=your-key-here")
        sys.exit(1)

    print("=" * 80)
    print("Kids-Friendly Topic Selector Demo")
    print("=" * 80)
    print()

    # Create selector
    selector = KidsTopicSelector(api_key=api_key)

    # Generate a single topic
    print("Generating a single topic...")
    try:
        topic = selector.select_topic()
        print(f"✓ Selected Topic: {topic}")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

    print()
    print("-" * 80)
    print()

    # Generate multiple topics
    print("Generating 5 unique topics...")
    try:
        topics = selector.select_multiple_topics(count=5)
        for i, topic in enumerate(topics, 1):
            print(f"{i}. {topic}")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

    print()
    print("=" * 80)
    print("Demo complete!")
