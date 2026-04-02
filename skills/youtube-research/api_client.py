#!/usr/bin/env python3
"""
YouTube Research - TranscriptAPI Client
"""
import requests
import json
import os
import sys

API_KEY = "sk_2lJao1zz0r5orexegkLjxJSvxFaiHhNluB5q95PdU5s"
BASE_URL = "https://transcriptapi.com/api/v2"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

def get_transcript(video_url, include_timestamp=True, include_metadata=False):
    """Fetch transcript from YouTube video"""
    params = {
        "video_url": video_url,
        "include_timestamp": "true" if include_timestamp else "false",
        "include_metadata": "true" if include_metadata else "false"
    }
    
    response = requests.get(
        f"{BASE_URL}/youtube/transcript",
        headers=HEADERS,
        params=params
    )
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        return {"error": "Transcript not available", "detail": response.json().get("detail", "")}
    elif response.status_code == 402:
        return {"error": "Insufficient credits"}
    else:
        return {"error": f"API error {response.status_code}", "detail": response.text}

def get_transcript_text(video_url):
    """Fetch transcript as plain text"""
    params = {
        "video_url": video_url,
        "format": "text",
        "include_timestamp": "false"
    }
    
    response = requests.get(
        f"{BASE_URL}/youtube/transcript",
        headers=HEADERS,
        params=params
    )
    
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: {response.status_code}"

def search_videos(query, limit=10, result_type="video"):
    """Search YouTube videos"""
    params = {
        "q": query,
        "type": result_type,
        "limit": limit
    }
    
    response = requests.get(
        f"{BASE_URL}/youtube/search",
        headers=HEADERS,
        params=params
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"API error {response.status_code}"}

def get_channel_latest(channel, limit=15):
    """Get latest videos from a channel"""
    params = {
        "channel": channel,
        "limit": limit
    }
    
    response = requests.get(
        f"{BASE_URL}/youtube/channel/latest",
        headers=HEADERS,
        params=params
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"API error {response.status_code}"}

def resolve_channel(input_str):
    """Resolve @handle/URL to channel ID"""
    params = {"input": input_str}
    
    response = requests.get(
        f"{BASE_URL}/youtube/channel/resolve",
        headers=HEADERS,
        params=params
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"API error {response.status_code}"}

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "transcript"
    
    if action == "transcript":
        url = sys.argv[2] if len(sys.argv) > 2 else ""
        if not url:
            print("Usage: python app.py transcript <video_url>")
            sys.exit(1)
        result = get_transcript(url, include_metadata=True)
        print(json.dumps(result, indent=2))
    
    elif action == "text":
        url = sys.argv[2] if len(sys.argv) > 2 else ""
        if not url:
            print("Usage: python app.py text <video_url>")
            sys.exit(1)
        print(get_transcript_text(url))
    
    elif action == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        if not query:
            print("Usage: python app.py search <query> [limit]")
            sys.exit(1)
        print(json.dumps(search_videos(query, limit), indent=2))
    
    elif action == "latest":
        channel = sys.argv[2] if len(sys.argv) > 2 else ""
        if not channel:
            print("Usage: python app.py latest <@handle or channel_url>")
            sys.exit(1)
        print(json.dumps(get_channel_latest(channel), indent=2))
    
    elif action == "resolve":
        channel = sys.argv[2] if len(sys.argv) > 2 else ""
        if not channel:
            print("Usage: python app.py resolve <@handle or channel_url>")
            sys.exit(1)
        print(json.dumps(resolve_channel(channel), indent=2))
    
    else:
        print(f"Unknown action: {action}")
        print("Usage: python app.py <transcript|text|search|latest|resolve> [args]")
