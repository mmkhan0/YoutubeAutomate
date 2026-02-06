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
                "You are a technology education specialist. "
                "You create engaging, informative video topics about technology, "
                "computers, internet, AI, robotics, and how digital things work. "
                "Focus on educational tech content suitable for all ages. "
                "Never suggest copyrighted characters or branded content."
            )
        elif self.category == 'kids':
            return (
                "You are a children's educational content specialist. "
                "You create safe, engaging, and age-appropriate video topics "
                "for preschool and early elementary children (ages 4-8). "
                "Focus on animals, nature, colors, numbers, and basic concepts. "
                "Never suggest copyrighted characters or branded content."
            )
        elif self.category == 'science':
            return (
                "You are a science education specialist. "
                "You create engaging video topics about physics, chemistry, biology, "
                "and natural phenomena. Explain scientific concepts in simple terms. "
                "Focus on educational science content suitable for all ages. "
                "Never suggest copyrighted characters or branded content."
            )
        else:  # auto
            return (
                "You are an educational content specialist. "
                "You create engaging, informative video topics about technology, "
                "science, nature, and how things work. "
                "Focus on educational content suitable for all ages. "
                "Never suggest copyrighted characters or branded content."
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
        return f"""Generate ONE educational and engaging YouTube video topic about TECHNOLOGY, COMPUTERS, or HOW THINGS WORK.

Requirements:
- Must be educational and informative about technology/science
- Evergreen content (not tied to trends or specific products)
- Explain how technology works in simple terms
- NO copyrighted characters or specific brand names
- Should be clear and specific (50-70 characters)

Great topic categories:
• How computers work (e.g., "How Does a Computer Process Information?")
• Internet & connectivity (e.g., "How Does WiFi Send Data Through the Air?")
• Artificial Intelligence (e.g., "What is AI and How Do Computers Learn?")
• Robotics (e.g., "How Do Robots See and Move Around?")
• Smartphones & devices (e.g., "How Does a Touchscreen Know Where You Touch?")
• Gaming technology (e.g., "How Are Video Games Created and Programmed?")
• Energy & power (e.g., "How Do Batteries Store and Release Energy?")
• Digital communication (e.g., "How Do Video Calls Work Across the World?")
• Coding concepts (e.g., "What is Programming and How Does Code Work?")
• Future tech (e.g., "What is Virtual Reality and How Does It Work?")

Return ONLY the video topic as a single line of text. No explanations, no quotes around it, just the topic.

Topic:"""

    def _build_kids_prompt(self) -> str:
        """Build kids category prompt."""
        return f"""Generate ONE educational and engaging YouTube video topic for children aged 4-8 years.

Requirements:
- Must be educational, entertaining, or story-based
- Evergreen content (not tied to trends or seasons)
- Safe for young children (no violence, fear, or complex topics)
- NO copyrighted characters (no Disney, Marvel, Nickelodeon, etc.)
- NO brand names or products
- Should be clear and specific (50-70 characters)

Great topic categories:
• Animal facts and sounds (e.g., "How Do Dolphins Talk to Each Other?")
• Numbers and counting (e.g., "Learning to Count from 1 to 20 with Fun Objects")
• Colors and shapes (e.g., "Finding Shapes in Nature - A Fun Adventure")
• Simple science (e.g., "Why Do Leaves Change Colors?")
• Life lessons (e.g., "The Story of the Kind Little Turtle")
• Nature exploration (e.g., "Amazing Facts About Butterflies")
• Body and health (e.g., "Why Do We Need to Sleep?")
• Daily routines (e.g., "The Morning Routine Song")

Return ONLY the video topic as a single line of text. No explanations, no quotes around it, just the topic.

Topic:"""

    def _build_science_prompt(self) -> str:
        """Build science category prompt."""
        return f"""Generate ONE educational and engaging YouTube video topic about SCIENCE and HOW NATURE WORKS.

Requirements:
- Must be educational and informative about scientific concepts
- Evergreen content (not tied to trends or specific products)
- Explain science in simple, understandable terms
- NO copyrighted characters or specific brand names
- Should be clear and specific (50-70 characters)

Great topic categories:
• Physics (e.g., "How Does Gravity Keep Us on the Ground?")
• Chemistry (e.g., "What Happens When Ice Melts? The Science of States")
• Biology (e.g., "How Do Plants Make Food from Sunlight?")
• Earth science (e.g., "Why Do We Have Seasons? Earth's Tilt Explained")
• Weather (e.g., "How Are Clouds Formed in the Sky?")
• Space (e.g., "Why Does the Moon Change Shape? Lunar Phases")
• Environment (e.g., "The Water Cycle: From Rain to Rivers to Clouds")
• Human body (e.g., "How Do Our Eyes See Colors?")
• Energy (e.g., "What is Energy and Where Does It Come From?")
• Natural phenomena (e.g., "Why Do We See Rainbows After Rain?")

Return ONLY the video topic as a single line of text. No explanations, no quotes around it, just the topic.

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
