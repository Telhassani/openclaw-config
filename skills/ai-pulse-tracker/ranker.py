#!/usr/bin/env python3
"""
Ranker module — Score and rank videos by relevance + actionability
"""

from datetime import datetime, timedelta
from typing import List, Dict
import re

def score_and_rank(
    videos: List[Dict],
    weights: Dict,
    categories: Dict
) -> List[Dict]:
    """
    Score each video and return sorted list (highest score first).
    
    Scoring factors:
    - recency: Upload date (last 48h weighted higher)
    - engagement: View velocity (not absolute count)
    - credibility: Verified creator signals
    - topic_relevance: Keyword match with focus categories
    """
    scored = []
    
    for video in videos:
        score = calculate_score(video, weights, categories)
        scored.append({**video, 'score': score})
    
    # Sort by score descending
    scored.sort(key=lambda x: x['score'], reverse=True)
    
    return scored

def calculate_score(
    video: Dict,
    weights: Dict,
    categories: Dict
) -> float:
    """Calculate composite score for a single video."""
    
    # Recency score (0-1) - API returns publishedTime or publish_date
    pub_date = video.get('publishedTime') or video.get('publishedTimeText') or video.get('publish_date', '')
    recency = score_recency(pub_date)
    
    # Engagement score (0-1) - API returns viewCountInt or view_count
    view_count = video.get('viewCountInt') or video.get('view_count', 0)
    engagement = score_engagement(view_count, pub_date)
    
    # Credibility score (0-1) - channel is now a dict {title, handle, id, thumbnail}
    channel_data = video.get('channel', {})
    channel_name = channel_data.get('title', '') if isinstance(channel_data, dict) else str(channel_data)
    credibility = score_credibility(channel_name)
    
    # Topic relevance score (0-1)
    topic_relevance = score_topic_relevance(
        video.get('title', '') + video.get('description', ''),
        categories
    )
    
    # Weighted sum
    total = (
        recency * weights['recency_weight'] +
        engagement * weights['engagement_weight'] +
        credibility * weights['credibility_weight'] +
        topic_relevance * weights['topic_relevance_weight']
    )
    
    return round(total, 3)

def score_recency(publish_date) -> float:
    """Score by upload recency (0-1, newer = higher).
    Handles both ISO dates and relative text ('2 hours ago', '1 year ago').
    """
    if not publish_date:
        return 0.0
    
    # If it's ISO format, parse it
    if isinstance(publish_date, str) and 'T' in publish_date:
        try:
            published = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
            now = datetime.now(published.tzinfo) if published.tzinfo else datetime.now()
            hours_ago = (now - published).total_seconds() / 3600
            
            if hours_ago <= 24:
                return 1.0
            elif hours_ago <= 48:
                return 0.5
            else:
                return 0.2
        except Exception:
            pass
    
    # If it's relative text ('2 hours ago', '1 year ago'), parse it
    if isinstance(publish_date, str):
        text_lower = publish_date.lower()
        
        # Extract number and unit
        import re
        match = re.match(r'(\d+)\s*(\w+)', text_lower)
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            
            if 'hour' in unit:
                hours_ago = value
            elif 'day' in unit:
                hours_ago = value * 24
            elif 'week' in unit:
                hours_ago = value * 168
            elif 'month' in unit:
                hours_ago = value * 720
            elif 'year' in unit:
                hours_ago = value * 8760
            else:
                hours_ago = 999999
            
            if hours_ago <= 24:
                return 1.0
            elif hours_ago <= 48:
                return 0.5
            elif hours_ago <= 168:  # 1 week
                return 0.3
            else:
                return 0.1
    
    return 0.0

def score_engagement(view_count: int, publish_date: str) -> float:
    """Score by view velocity (views per hour, not absolute)."""
    if not publish_date or view_count == 0:
        return 0.0
    
    try:
        published = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
        now = datetime.now(published.tzinfo) if published.tzinfo else datetime.now()
        
        hours_ago = max((now - published).total_seconds() / 3600, 1)
        views_per_hour = view_count / hours_ago
        
        # Normalize: 1000/hour = 1.0, 100/hour = 0.5
        if views_per_hour >= 1000:
            return 1.0
        elif views_per_hour >= 100:
            return 0.7
        elif views_per_hour >= 50:
            return 0.5
        else:
            return 0.3
    
    except Exception:
        return 0.0

def score_credibility(channel) -> float:
    """Score by creator credibility signals."""
    if not channel:
        return 0.0
    
    # Handle dict response from API (channel is {id, title, handle, thumbnail})
    if isinstance(channel, dict):
        channel_name = channel.get('title', '')
    else:
        channel_name = str(channel)
    
    if not channel_name:
        return 0.0
    
    channel_lower = channel_name.lower()
    
    # Verified AI researchers / institutions
    verified_signals = [
        'karpathy', 'hinton', 'lecun', 'altman', 'anthropic',
        'openai', 'deepmind', 'meta ai', 'stanford', 'mit',
        'berkeley', 'caltech', 'y combinator'
    ]
    
    # AI-focused channels (not general tech)
    ai_channel_signals = [
        'ai', 'ml', 'deep learning', 'neural', 'llm', 'nlp'
    ]
    
    score = 0.0
    
    # Check verified signals
    for signal in verified_signals:
        if signal in channel_lower:
            score += 0.5
            break
    
    # Check AI focus
    for signal in ai_channel_signals:
        if signal in channel_lower:
            score += 0.3
            break
    
    # Cap at 1.0
    return min(score, 1.0)

def score_topic_relevance(text: str, categories: Dict) -> float:
    """Score by keyword match with focus categories."""
    if not text:
        return 0.0
    
    text_lower = text.lower()
    
    # Count matches across all categories
    total_matches = 0
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text_lower:
                total_matches += 1
    
    # Normalize: 5+ matches = 1.0, 2-4 = 0.6, 0-1 = 0.2
    if total_matches >= 5:
        return 1.0
    elif total_matches >= 2:
        return 0.6
    elif total_matches >= 1:
        return 0.4
    else:
        return 0.2

def categorize_videos(
    videos: List[Dict],
    categories: Dict
) -> List[str]:
    """
    Assign each video to primary category based on keyword matching.
    Returns list of category names (same order as input videos).
    """
    result = []
    
    for video in videos:
        text = (video.get('title', '') + video.get('description', '')).lower()
        
        # Find best matching category
        best_category = "infrastructure"  # default
        best_score = 0
        
        for category, keywords in categories.items():
            matches = sum(1 for kw in keywords if kw in text)
            if matches > best_score:
                best_score = matches
                best_category = category
        
        result.append(best_category.replace('_', ' ').title())
    
    return result
