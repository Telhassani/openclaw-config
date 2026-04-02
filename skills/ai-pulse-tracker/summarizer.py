#!/usr/bin/env python3
"""
Summarizer module — Generate structured summaries via Ollama
Reuses patterns from video-summary skill
"""

import requests
import json
from typing import Dict, List

def summarize_video(
    transcript: str,
    metadata: Dict,
    config: Dict
) -> Dict:
    """
    Generate structured summary using Ollama.
    Returns dict with: tl_dr, key_insights, actionability_score, category_tags
    """
    
    # Truncate transcript if too long (Ollama context limits)
    max_chars = 5000
    if len(transcript) > max_chars:
        transcript = transcript[:max_chars] + "..."
    
    # Build prompt
    prompt = build_prompt(transcript, metadata)
    
    # Call Ollama with configurable timeout
    response = call_ollama(
        prompt=prompt,
        model=config.get('model', 'qwen3.5:397b-cloud'),
        endpoint=config.get('endpoint', 'http://localhost:11434/api/chat'),
        timeout=config.get('timeout', 120)
    )
    
    # Parse response
    summary = parse_summary(response)
    
    return summary

def build_prompt(transcript: str, metadata: Dict) -> str:
    """Build structured prompt for Ollama."""
    
    return f"""You are an AI tech analyst. Summarize this video transcript with focus on:
1. Implementation details (code, architecture, tools)
2. Actionability (can the viewer build this?)
3. Technical depth (not just hype)

Video: {metadata.get('title', 'Unknown')}
Channel: {metadata.get('channel', 'Unknown')}
URL: {metadata.get('url', '')}

Transcript:
{transcript}

Output in JSON format:
{{
    "tl_dr": "2-sentence summary",
    "key_insights": ["insight 1", "insight 2", "insight 3"],
    "actionability": "high/medium/low",
    "has_code": true/false,
    "has_architecture": true/false,
    "category_tags": ["local llm", "agents", "models", "infrastructure"],
    "homelab_friendly": true/false
}}
"""

def call_ollama(
    prompt: str,
    model: str,
    endpoint: str,
    timeout: int = 120
) -> str:
    """Call Ollama chat API."""
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(endpoint, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        # Extract response content
        content = data.get('message', {}).get('content', '')
        return content
    
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Ollama call failed: {e}")
        return json.dumps({"tl_dr": "Summary unavailable", "key_insights": [], "actionability": "low"})

def parse_summary(response: str) -> Dict:
    """Parse JSON response from Ollama."""
    
    try:
        # Find JSON in response (may have markdown wrapper)
        json_start = response.find('{')
        json_end = response.rfind('}')
        
        if json_start == -1 or json_end == -1:
            return {
                "tl_dr": "Parse error",
                "key_insights": [],
                "actionability": "unknown",
                "has_code": False,
                "has_architecture": False,
                "category_tags": [],
                "homelab_friendly": False
            }
        
        json_str = response[json_start:json_end + 1]
        parsed = json.loads(json_str)
        
        return {
            "tl_dr": parsed.get('tl_dr', 'No summary'),
            "key_insights": parsed.get('key_insights', []),
            "actionability": parsed.get('actionability', 'medium'),
            "has_code": parsed.get('has_code', False),
            "has_architecture": parsed.get('has_architecture', False),
            "category_tags": parsed.get('category_tags', []),
            "homelab_friendly": parsed.get('homelab_friendly', False)
        }
    
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parse failed: {e}")
        return {
            "tl_dr": response[:200] if response else "No summary",
            "key_insights": [],
            "actionability": "unknown",
            "has_code": False,
            "has_architecture": False,
            "category_tags": [],
            "homelab_friendly": False
        }
