"""
Advanced YouTube SEO Optimizer

Automatically improves YouTube SEO with:
- Keyword research and trending topics
- SEO scoring (0-100) with actionable recommendations
- Title A/B testing with multiple variants
- Long-tail keyword generation
- Keyword density optimization
- Search intent matching
- Competitor analysis insights
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from openai import OpenAI, OpenAIError
import time


@dataclass
class SEOScore:
    """SEO quality score with breakdown."""
    overall_score: int  # 0-100
    title_score: int
    description_score: int
    tags_score: int
    hashtags_score: int
    keyword_density_score: int
    recommendations: List[str]
    strengths: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'overall_score': self.overall_score,
            'title_score': self.title_score,
            'description_score': self.description_score,
            'tags_score': self.tags_score,
            'hashtags_score': self.hashtags_score,
            'keyword_density_score': self.keyword_density_score,
            'recommendations': self.recommendations,
            'strengths': self.strengths
        }


@dataclass
class KeywordResearch:
    """Keyword research results."""
    primary_keywords: List[str]      # Main topic keywords
    secondary_keywords: List[str]    # Related keywords
    long_tail_keywords: List[str]    # Specific search phrases
    trending_keywords: List[str]     # Currently trending
    competitor_keywords: List[str]   # From top videos
    search_volume_estimate: Dict[str, str]  # High/Medium/Low


class YouTubeSEOOptimizer:
    """
    Advanced YouTube SEO optimizer with automatic enhancements.
    
    Analyzes and improves metadata for maximum discoverability.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7
    ):
        """
        Initialize SEO Optimizer.
        
        Args:
            api_key: OpenAI API key
            model: AI model to use
            temperature: Creativity level
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.logger = logging.getLogger(__name__)
    
    def research_keywords(
        self,
        topic: str,
        category: str = "kids",
        language: str = "en"
    ) -> KeywordResearch:
        """
        Research optimal keywords for the topic.
        
        Args:
            topic: Video topic
            category: Content category (kids/tech/science)
            language: Target language
            
        Returns:
            KeywordResearch: Comprehensive keyword data
        """
        self.logger.info(f"🔍 Researching keywords for: {topic}")
        
        prompt = f"""You are a YouTube SEO expert. Research and provide comprehensive keyword data for this video:

TOPIC: {topic}
CATEGORY: {category}
LANGUAGE: {language}
TARGET AUDIENCE: Parents searching for kids educational content + Kids searching directly

Provide detailed keyword research:

1. PRIMARY KEYWORDS (3-5 main keywords):
   - Core topic keywords that define the video
   - High search volume, highly relevant
   
2. SECONDARY KEYWORDS (5-8 related keywords):
   - Supporting keywords that expand reach
   - Medium search volume, relevant
   
3. LONG-TAIL KEYWORDS (5-10 specific phrases):
   - Exact phrases parents/kids would search
   - Examples: "why do leaves change color for kids", "butterfly life cycle explained simple"
   - Lower competition, high conversion
   
4. TRENDING KEYWORDS (3-5 current trends):
   - Currently popular keywords in this category
   - Seasonal or viral trends related to topic
   
5. COMPETITOR KEYWORDS (5-8 from top videos):
   - Keywords used by successful videos in this niche
   - Proven to drive views and engagement
   
6. SEARCH VOLUME ESTIMATES:
   - Classify each primary keyword as: High, Medium, or Low search volume

Return JSON only:
{{
  "primary_keywords": ["keyword1", "keyword2", "keyword3"],
  "secondary_keywords": ["keyword4", "keyword5", "keyword6", "keyword7", "keyword8"],
  "long_tail_keywords": ["exact search phrase 1", "exact search phrase 2", "exact search phrase 3"],
  "trending_keywords": ["trend1", "trend2", "trend3"],
  "competitor_keywords": ["competitor1", "competitor2", "competitor3"],
  "search_volume_estimate": {{
    "keyword1": "High",
    "keyword2": "Medium",
    "keyword3": "Low"
  }}
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a YouTube SEO research expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()
            
            import json
            data = json.loads(content)
            
            result = KeywordResearch(
                primary_keywords=data.get('primary_keywords', []),
                secondary_keywords=data.get('secondary_keywords', []),
                long_tail_keywords=data.get('long_tail_keywords', []),
                trending_keywords=data.get('trending_keywords', []),
                competitor_keywords=data.get('competitor_keywords', []),
                search_volume_estimate=data.get('search_volume_estimate', {})
            )
            
            self.logger.info(f"✓ Found {len(result.primary_keywords)} primary keywords")
            self.logger.info(f"✓ Found {len(result.long_tail_keywords)} long-tail keywords")
            self.logger.info(f"✓ Found {len(result.trending_keywords)} trending keywords")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Keyword research failed: {e}")
            # Return basic fallback
            return KeywordResearch(
                primary_keywords=[topic],
                secondary_keywords=["kids education", "learning for kids"],
                long_tail_keywords=[f"{topic.lower()} for kids"],
                trending_keywords=["educational videos"],
                competitor_keywords=["kids learning"],
                search_volume_estimate={topic: "Medium"}
            )
    
    def optimize_title(
        self,
        topic: str,
        keywords: KeywordResearch,
        generate_variants: int = 5
    ) -> Tuple[str, List[str], Dict[str, int]]:
        """
        Generate and optimize title with A/B testing.
        
        Args:
            topic: Video topic
            keywords: Keyword research data
            generate_variants: Number of variants to generate
            
        Returns:
            Tuple of (best_title, all_variants, scores)
        """
        self.logger.info(f"📝 Generating {generate_variants} optimized title variants")
        
        # Build keyword context
        keyword_context = f"""
PRIMARY KEYWORDS: {', '.join(keywords.primary_keywords[:3])}
LONG-TAIL KEYWORDS: {', '.join(keywords.long_tail_keywords[:3])}
TRENDING: {', '.join(keywords.trending_keywords[:2])}
"""
        
        prompt = f"""Generate {generate_variants} optimized YouTube title variants for kids educational content.

TOPIC: {topic}

{keyword_context}

TITLE REQUIREMENTS:
- 40-70 characters (optimal for mobile + desktop)
- Include primary keyword in first 40 characters
- Clear, descriptive, click-worthy
- NO emojis, NO clickbait
- Appeal to both kids AND parents
- Natural, easy to read

OPTIMIZATION STRATEGIES:
1. Keyword-first: Start with main keyword
2. Question format: "Why Do...", "How Does...", "What Is..."
3. List format: Include "5 Facts", "Amazing Things"
4. Benefit-focused: "Learn About...", "Discover..."
5. Curiosity-driven: Create intrigue while staying educational

Return {generate_variants} diverse variants with SEO scores (0-100):

{{
  "variants": [
    {{"title": "Title 1", "seo_score": 85, "strategy": "keyword-first"}},
    {{"title": "Title 2", "seo_score": 90, "strategy": "question-format"}},
    {{"title": "Title 3", "seo_score": 80, "strategy": "list-format"}},
    {{"title": "Title 4", "seo_score": 88, "strategy": "benefit-focused"}},
    {{"title": "Title 5", "seo_score": 82, "strategy": "curiosity-driven"}}
  ]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a YouTube SEO title optimization expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # Higher creativity for variants
                max_tokens=800
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()
            
            import json
            data = json.loads(content)
            
            variants_data = data.get('variants', [])
            
            # Extract titles and scores
            all_variants = []
            scores = {}
            
            for v in variants_data:
                title = v.get('title', '')
                if title:
                    all_variants.append(title)
                    scores[title] = v.get('seo_score', 50)
            
            # Pick best variant (highest score)
            if all_variants:
                best_title = max(all_variants, key=lambda t: scores.get(t, 0))
                self.logger.info(f"✓ Best title (score: {scores[best_title]}): {best_title}")
            else:
                best_title = topic[:70]
                all_variants = [best_title]
                scores = {best_title: 50}
            
            return best_title, all_variants, scores
            
        except Exception as e:
            self.logger.error(f"Title optimization failed: {e}")
            fallback = topic[:70]
            return fallback, [fallback], {fallback: 50}
    
    def score_seo_quality(
        self,
        title: str,
        description: str,
        tags: List[str],
        hashtags: List[str],
        keywords: KeywordResearch
    ) -> SEOScore:
        """
        Analyze and score SEO quality with recommendations.
        
        Args:
            title: Video title
            description: Video description
            tags: Video tags
            hashtags: Video hashtags
            keywords: Keyword research data
            
        Returns:
            SEOScore: Comprehensive SEO analysis
        """
        self.logger.info("📊 Analyzing SEO quality...")
        
        strengths = []
        recommendations = []
        
        # Score title (0-100)
        title_score = 0
        title_lower = title.lower()
        
        # Length check (40-70 chars optimal)
        if 40 <= len(title) <= 70:
            title_score += 30
            strengths.append("Title length is optimal (40-70 chars)")
        elif len(title) < 40:
            title_score += 15
            recommendations.append(f"Title is short ({len(title)} chars). Expand to 40-70 chars for better SEO")
        else:
            title_score += 20
            recommendations.append(f"Title is long ({len(title)} chars). Shorten to 40-70 chars")
        
        # Keyword presence
        keyword_in_title = any(kw.lower() in title_lower for kw in keywords.primary_keywords[:3])
        if keyword_in_title:
            title_score += 40
            strengths.append("Primary keyword found in title")
        else:
            recommendations.append("Include primary keyword in title for better ranking")
        
        # Keyword position (early is better)
        if keywords.primary_keywords and keywords.primary_keywords[0].lower() in title_lower[:40]:
            title_score += 30
            strengths.append("Keyword appears early in title (first 40 chars)")
        
        # Cap at 100
        title_score = min(title_score, 100)
        
        # Score description (0-100)
        description_score = 0
        description_lower = description.lower()
        
        # Length check (200-400 optimal for kids content)
        if 200 <= len(description) <= 400:
            description_score += 25
            strengths.append("Description length is optimal")
        elif len(description) < 200:
            description_score += 15
            recommendations.append(f"Description is short ({len(description)} chars). Expand to 200-400 chars")
        else:
            description_score += 20
        
        # Keyword mentions (3-5 times optimal)
        keyword_count = sum(kw.lower() in description_lower for kw in keywords.primary_keywords)
        if 2 <= keyword_count <= 5:
            description_score += 35
            strengths.append(f"Good keyword density ({keyword_count} mentions)")
        elif keyword_count == 0:
            description_score += 0
            recommendations.append("Add primary keywords to description (2-5 times)")
        elif keyword_count > 5:
            description_score += 20
            recommendations.append(f"Keyword density too high ({keyword_count} times). Reduce to 3-5 mentions")
        else:
            description_score += 25
        
        # Paragraph structure
        paragraphs = [p.strip() for p in description.split('\n\n') if p.strip()]
        if len(paragraphs) >= 2:
            description_score += 20
            strengths.append("Good paragraph structure (2+ paragraphs)")
        else:
            recommendations.append("Split description into 2 paragraphs for readability")
        
        # Long-tail keywords
        longtail_in_desc = any(kw.lower() in description_lower for kw in keywords.long_tail_keywords[:3])
        if longtail_in_desc:
            description_score += 20
            strengths.append("Long-tail keywords included in description")
        
        description_score = min(description_score, 100)
        
        # Score tags (0-100)
        tags_score = 0
        
        # Tag count (12-20 optimal)
        if 12 <= len(tags) <= 20:
            tags_score += 30
            strengths.append(f"Optimal tag count ({len(tags)} tags)")
        elif len(tags) < 12:
            tags_score += 15
            recommendations.append(f"Add more tags (current: {len(tags)}, optimal: 12-20)")
        else:
            tags_score += 25
        
        # Tag diversity (mix of keywords)
        tags_lower = [t.lower() for t in tags]
        primary_in_tags = sum(1 for kw in keywords.primary_keywords if kw.lower() in ' '.join(tags_lower))
        secondary_in_tags = sum(1 for kw in keywords.secondary_keywords[:5] if kw.lower() in ' '.join(tags_lower))
        
        if primary_in_tags >= 2:
            tags_score += 35
            strengths.append("Primary keywords well-represented in tags")
        else:
            recommendations.append("Include more primary keywords as tags")
        
        if secondary_in_tags >= 2:
            tags_score += 20
        
        # Long-tail tags
        longtail_in_tags = any(kw.lower() in ' '.join(tags_lower) for kw in keywords.long_tail_keywords[:3])
        if longtail_in_tags:
            tags_score += 15
            strengths.append("Long-tail keywords used in tags")
        
        tags_score = min(tags_score, 100)
        
        # Score hashtags (0-100)
        hashtags_score = 0
        
        # Hashtag count (8-15 optimal)
        if 8 <= len(hashtags) <= 15:
            hashtags_score += 40
            strengths.append(f"Optimal hashtag count ({len(hashtags)} hashtags)")
        elif len(hashtags) < 8:
            hashtags_score += 20
            recommendations.append(f"Add more hashtags (current: {len(hashtags)}, optimal: 8-15)")
        else:
            hashtags_score += 30
        
        # Trending hashtags
        trending_in_hashtags = any(kw.replace(' ', '') in ''.join(hashtags).lower() 
                                   for kw in keywords.trending_keywords)
        if trending_in_hashtags:
            hashtags_score += 30
            strengths.append("Trending keywords included as hashtags")
        else:
            recommendations.append("Add current trending keywords as hashtags")
        
        # Category hashtags
        category_hashtags = ['KidsEducation', 'LearningForKids', 'EducationalVideos']
        has_category = any(h in hashtags for h in category_hashtags)
        if has_category:
            hashtags_score += 30
        else:
            recommendations.append("Add category-specific hashtags (e.g., KidsEducation)")
        
        hashtags_score = min(hashtags_score, 100)
        
        # Keyword density score (0-100)
        total_text = f"{title} {description} {' '.join(tags)}".lower()
        total_keywords = sum(kw.lower() in total_text for kw in 
                           keywords.primary_keywords + keywords.secondary_keywords[:5])
        
        if total_keywords >= 8:
            keyword_density_score = 100
            strengths.append("Excellent keyword coverage across all metadata")
        elif total_keywords >= 5:
            keyword_density_score = 75
            strengths.append("Good keyword coverage")
        elif total_keywords >= 3:
            keyword_density_score = 50
            recommendations.append("Increase keyword usage across title, description, and tags")
        else:
            keyword_density_score = 25
            recommendations.append("Low keyword density. Add more relevant keywords throughout metadata")
        
        # Overall score (weighted average)
        overall_score = int(
            title_score * 0.30 +           # 30% weight
            description_score * 0.25 +      # 25% weight
            tags_score * 0.20 +             # 20% weight
            hashtags_score * 0.15 +         # 15% weight
            keyword_density_score * 0.10    # 10% weight
        )
        
        return SEOScore(
            overall_score=overall_score,
            title_score=title_score,
            description_score=description_score,
            tags_score=tags_score,
            hashtags_score=hashtags_score,
            keyword_density_score=keyword_density_score,
            recommendations=recommendations,
            strengths=strengths
        )
    
    def enhance_metadata_with_keywords(
        self,
        metadata: Dict[str, Any],
        keywords: KeywordResearch
    ) -> Dict[str, Any]:
        """
        Enhance existing metadata with researched keywords.
        
        Args:
            metadata: Current metadata (title, description, tags, hashtags)
            keywords: Keyword research data
            
        Returns:
            Dict: Enhanced metadata
        """
        self.logger.info("🚀 Enhancing metadata with researched keywords...")
        
        enhanced = metadata.copy()
        
        # Enhance tags with long-tail keywords
        current_tags = set(t.lower() for t in enhanced.get('tags', []))
        
        # Add long-tail keywords as tags (if not too long)
        for longtail in keywords.long_tail_keywords:
            if len(longtail) <= 30 and longtail.lower() not in ' '.join(current_tags):
                enhanced['tags'].append(longtail)
        
        # Add trending keywords as tags
        for trending in keywords.trending_keywords:
            if len(trending) <= 30 and trending.lower() not in ' '.join(current_tags):
                enhanced['tags'].append(trending)
        
        # Limit to 20 tags
        enhanced['tags'] = enhanced['tags'][:20]
        
        # Enhance hashtags with trending keywords
        current_hashtags = set(h.lower() for h in enhanced.get('hashtags', []))
        
        for trending in keywords.trending_keywords:
            hashtag = trending.replace(' ', '').replace('-', '')
            if len(hashtag) <= 30 and hashtag.lower() not in current_hashtags:
                enhanced['hashtags'].append(hashtag)
        
        # Add competitor keywords as hashtags
        for comp in keywords.competitor_keywords[:3]:
            hashtag = comp.replace(' ', '').replace('-', '')
            if len(hashtag) <= 30 and hashtag.lower() not in current_hashtags:
                enhanced['hashtags'].append(hashtag)
        
        # Limit to 15 hashtags
        enhanced['hashtags'] = enhanced['hashtags'][:15]
        
        self.logger.info(f"✓ Enhanced: {len(enhanced['tags'])} tags, {len(enhanced['hashtags'])} hashtags")
        
        return enhanced


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def optimize_youtube_seo(
    topic: str,
    metadata: Dict[str, Any],
    category: str = "kids",
    language: str = "en",
    api_key: str = None
) -> Tuple[Dict[str, Any], SEOScore, KeywordResearch]:
    """
    Comprehensive SEO optimization for YouTube metadata.
    
    Args:
        topic: Video topic
        metadata: Current metadata dict
        category: Content category
        language: Target language  
        api_key: OpenAI API key
        
    Returns:
        Tuple of (optimized_metadata, seo_score, keyword_research)
    """
    optimizer = YouTubeSEOOptimizer(api_key=api_key)
    
    # Research keywords
    keywords = optimizer.research_keywords(topic, category, language)
    
    # Optimize title
    best_title, variants, scores = optimizer.optimize_title(topic, keywords)
    metadata['title'] = best_title
    metadata['title_variants'] = variants
    metadata['title_scores'] = scores
    
    # Enhance with keywords
    enhanced_metadata = optimizer.enhance_metadata_with_keywords(metadata, keywords)
    
    # Score SEO quality
    seo_score = optimizer.score_seo_quality(
        title=enhanced_metadata['title'],
        description=enhanced_metadata['description'],
        tags=enhanced_metadata['tags'],
        hashtags=enhanced_metadata['hashtags'],
        keywords=keywords
    )
    
    return enhanced_metadata, seo_score, keywords


if __name__ == "__main__":
    """Test SEO optimizer"""
    import os
    
    logging.basicConfig(level=logging.INFO)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY environment variable")
        exit(1)
    
    # Test with example
    test_topic = "Why Do Leaves Change Colors in Fall"
    test_metadata = {
        'title': "Leaves Changing Colors",
        'description': "Learn about leaves and colors in this fun video for kids!",
        'tags': ["leaves", "colors", "fall", "autumn"],
        'hashtags': ["KidsLearning"]
    }
    
    print("=" * 80)
    print("SEO OPTIMIZER TEST")
    print("=" * 80)
    
    optimized, score, keywords = optimize_youtube_seo(
        topic=test_topic,
        metadata=test_metadata,
        api_key=api_key
    )
    
    print(f"\n📊 SEO SCORE: {score.overall_score}/100")
    print(f"\n✓ STRENGTHS:")
    for s in score.strengths:
        print(f"  • {s}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for r in score.recommendations:
        print(f"  • {r}")
    
    print(f"\n🎯 PRIMARY KEYWORDS: {', '.join(keywords.primary_keywords)}")
    print(f"📈 TRENDING: {', '.join(keywords.trending_keywords)}")
    
    print(f"\n✨ OPTIMIZED TITLE: {optimized['title']}")
    print(f"🏷️  TAGS ({len(optimized['tags'])}): {', '.join(optimized['tags'][:5])}...")
    print(f"#️⃣  HASHTAGS ({len(optimized['hashtags'])}): {', '.join(['#'+h for h in optimized['hashtags'][:5]])}...")
