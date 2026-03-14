#!/usr/bin/env python3
"""
Fetcher module — YouTube search + transcript retrieval
Uses ScrapeCreators API for all operations
"""

import requests
from typing import List, Dict, Optional

def fetch_search_results(
    query: str,
    limit: int = 20,
    api_key: str = "",
    base_url: str = "https://api.scrapecreators.com/v1"
) -> List[Dict]:
    """
    Fetch YouTube search results via ScrapeCreators API.
    Returns list of video metadata (title, channel, views, publishDate, etc.)
    """
    endpoint = f"{base_url}/youtube/search"
    params = {
        "query": query,
        "limit": limit,
        "sort_by": "relevance",  # Could also be "date" or "views"
        "upload_date": "48h"     # Only last 48 hours
    }
    
    headers = {"x-api-key": api_key}
    
    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extract video list (adapt to actual API response structure)
        videos = data.get('videos', [])
        
        # Normalize fields
        normalized = []
        for v in videos:
            normalized.append({
                'video_id': v.get('id', ''),
                'title': v.get('title', ''),
                'channel': v.get('channel', ''),
                'description': v.get('description', ''),
                'view_count': v.get('views', 0),
                'publish_date': v.get('publishedAt', ''),
                'duration': v.get('duration', ''),
                'thumbnail': v.get('thumbnail', ''),
                'url': f"https://youtube.com/watch?v={v.get('id', '')}"
            })
        
        return normalized
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Search API failed: {e}")
        return []

def fetch_transcripts(
    videos: List[Dict],
    api_key: str = "",
    base_url: str = "https://api.scrapecreators.com/v1"
) -> List[str]:
    """
    Fetch transcripts for a list of videos.
    Returns list of transcript texts (same order as input videos).
    """
    endpoint = f"{base_url}/youtube/video/transcript"
    headers = {"x-api-key": api_key}
    
    transcripts = []
    
    for video in videos:
        video_url = video.get('url', '')
        if not video_url:
            transcripts.append("")
            continue
        
        params = {"url": video_url}
        
        try:
            response = requests.get(endpoint, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Extract transcript text - API returns array of {text, startMs, endMs}
            transcript_items = data.get('transcript', [])
            # Concatenate all text segments
            transcript_text = ''.join(item.get('text', '') for item in transcript_items)
            transcripts.append(transcript_text)
        
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Transcript fetch failed: {e}")
            transcripts.append("")
    
    return transcripts
