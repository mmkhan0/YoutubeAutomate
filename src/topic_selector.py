"""
Topic Selector Module

Uses AI to select interesting and trending topics for video generation.
Ensures variety and avoids repeating recent topics.
"""

import logging
import json
import random
from typing import Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
from openai import OpenAI


class TopicSelector:
    """Selects appropriate video topics using AI and topic history."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the TopicSelector.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger("YouTubeAutomation.TopicSelector")
        self.client = OpenAI(api_key=config['api_keys']['openai_api_key'])
        self.history_file = Path(config['paths']['logs_dir']) / "topic_history.json"
        
    def select_topic(self) -> Dict[str, Any]:
        """
        Select a topic for the next video.
        
        Returns:
            Dictionary containing topic information:
            - title: Video title
            - topic: Main topic/theme
            - keywords: List of relevant keywords
            - target_duration: Target video duration in seconds
        """
        
        self.logger.info("Selecting new video topic...")
        
        # Load topic history to avoid repetition
        recent_topics = self._load_recent_topics(days=30)
        self.logger.debug(f"Loaded {len(recent_topics)} recent topics")
        
        # Get available topic categories
        available_topics = self.config['content']['topics']
        
        # Use AI to generate topic
        prompt = self._build_topic_prompt(available_topics, recent_topics)
        
        try:
            response = self.client.chat.completions.create(
                model=self.config['ai']['model'],
                messages=[
                    {"role": "system", "content": "You are a creative content strategist for YouTube videos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config['ai']['temperature']
            )
            
            topic_data = json.loads(response.choices[0].message.content)
            
            # Add metadata
            topic_data['timestamp'] = datetime.now().isoformat()
            topic_data['target_duration'] = random.randint(
                self.config['video']['target_duration_seconds'],
                self.config['video']['max_duration_seconds']
            )
            
            # Save to history
            self._save_topic_to_history(topic_data)
            
            self.logger.info(f"Selected topic: {topic_data['title']}")
            return topic_data
            
        except Exception as e:
            self.logger.error(f"Error selecting topic: {e}")
            # Fallback to random topic
            return self._fallback_topic(available_topics)
    
    def _build_topic_prompt(self, available_topics: list, recent_topics: list) -> str:
        """Build prompt for AI topic generation."""
        
        recent_titles = [t.get('title', '') for t in recent_topics]
        
        prompt = f"""Generate a unique and engaging video topic for a YouTube video.

Available topic categories: {', '.join(available_topics)}
Recent topics to avoid: {', '.join(recent_titles[-10:])}

Create a topic that:
- Is interesting and engaging
- Has educational or entertainment value
- Is suitable for a 3-15 minute video
- Has not been covered recently

Return ONLY valid JSON with this exact structure (no markdown, no code blocks):
{{
    "title": "Catchy video title (50-60 characters)",
    "topic": "Main topic category",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "description": "Brief description of video content"
}}"""
        
        return prompt
    
    def _load_recent_topics(self, days: int = 30) -> list:
        """Load topics generated in the last N days."""
        
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                all_topics = json.load(f)
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            recent = [
                t for t in all_topics
                if datetime.fromisoformat(t.get('timestamp', '2000-01-01')) > cutoff_date
            ]
            
            return recent
            
        except Exception as e:
            self.logger.warning(f"Error loading topic history: {e}")
            return []
    
    def _save_topic_to_history(self, topic: Dict[str, Any]) -> None:
        """Save generated topic to history file."""
        
        try:
            # Load existing history
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = []
            
            # Append new topic
            history.append(topic)
            
            # Save back
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.warning(f"Error saving topic to history: {e}")
    
    def _fallback_topic(self, available_topics: list) -> Dict[str, Any]:
        """Generate fallback topic if AI fails."""
        
        topic_category = random.choice(available_topics)
        
        return {
            'title': f"Interesting Facts About {topic_category.title()}",
            'topic': topic_category,
            'keywords': [topic_category, 'interesting', 'facts'],
            'description': f"A collection of interesting facts about {topic_category}",
            'timestamp': datetime.now().isoformat(),
            'target_duration': self.config['video']['target_duration_seconds']
        }
