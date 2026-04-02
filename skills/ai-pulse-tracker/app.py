#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════╗
║   AI PULSE TRACKER — Daily Intelligence     ║
║   Scrapes YouTube AI/tech content            ║
║   Ranks by relevance + actionability         ║
║   Delivers Top 10 to Obsidian                ║
╚══════════════════════════════════════════════╝

Usage: python3 app.py [--manual]
Cron:  0 9 * * * (daily at 9 AM Europe/Paris)
"""

import json
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

from fetcher import fetch_search_results, fetch_transcripts
from ranker import score_and_rank, categorize_videos
from summarizer import summarize_video
from templates import render_report

# ─── CONFIG ────────────────────────────────────────────────────
CONFIG_PATH = Path(__file__).parent / "config.json"
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

CONFIG = load_config()

def log(msg):
    ts = datetime.now().isoformat()
    print(f"[{ts}] {msg}")

# ─── MAIN WORKFLOW ─────────────────────────────────────────────
def run():
    log("🌅 AI Pulse Tracker starting...")
    
    # 1. Determine which search query to use (rotate daily)
    day_of_year = int(datetime.now().strftime('%j'))
    query_index = day_of_year % len(CONFIG['search']['queries'])
    search_query = CONFIG['search']['queries'][query_index]
    
    log(f"🔍 Search query: {search_query}")
    
    # 2. Fetch search results from YouTube (20 videos)
    videos = fetch_search_results(
        query=search_query,
        limit=CONFIG['search']['results_per_query'],
        api_key=CONFIG['api']['key'],
        base_url=CONFIG['api']['base_url']
    )
    
    if not videos:
        log("❌ No videos fetched — exiting")
        return
    
    log(f"✅ Fetched {len(videos)} videos")
    
    # 3. Score and rank using search metadata
    ranked_videos = score_and_rank(
        videos,
        weights=CONFIG['ranking'],
        categories=CONFIG['categories']
    )
    
    log(f"✅ Ranked {len(ranked_videos)} videos")
    
    # 4. Take Top 10 and fetch transcripts
    top_10 = ranked_videos[:10]
    transcripts = fetch_transcripts(
        videos=top_10,
        api_key=CONFIG['api']['key'],
        base_url=CONFIG['api']['base_url']
    )
    
    log(f"✅ Fetched {len(transcripts)} transcripts")
    
    # 5. Categorize each video
    categorized = categorize_videos(top_10, CONFIG['categories'])
    
    # 6. Summarize each video (via Ollama)
    summaries = []
    for i, video in enumerate(top_10):
        if i < len(transcripts):
            transcript = transcripts[i]
            summary = summarize_video(
                transcript=transcript,
                metadata=video,
                config=CONFIG['summarizer']
            )
            summaries.append({
                **video,
                'category': categorized[i],
                'summary': summary
            })
        else:
            # Fallback: metadata-only summary
            summaries.append({
                **video,
                'category': categorized[i],
                'summary': {'tl_dr': video.get('title', 'No summary')}
            })
    
    log(f"✅ Summarized {len(summaries)} videos")
    
    # 7. Generate daily report
    report = render_report(
        summaries=summaries,
        date=datetime.now().strftime('%Y-%m-%d'),
        search_query=search_query
    )
    
    # 8. Save to Obsidian via SSH
    save_to_obsidian(report, CONFIG['obsidian'])
    
    # 9. Log usage stats
    log_usage(query_index, search_query, len(videos), len(transcripts))
    
    log("🎉 AI Pulse Tracker complete")

# ─── OBSIDIAN SAVE (SSH) ──────────────────────────────────────
def save_to_obsidian(report, obsidian_config):
    """Save report to Obsidian vault via SSH."""
    import subprocess
    import time
    
    folder = f"{obsidian_config['vault_path']}/{obsidian_config['default_folder']}"
    filename = f"{datetime.now().strftime('%Y-%m-%d')}.md"
    
    # Write to temp file
    temp_path = f"/tmp/ai-pulse-{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(temp_path, 'w') as f:
        f.write(report)
    
    # SSH + mkdir + scp with timeout
    try:
        log(f"📁 Connecting to {obsidian_config['ssh_host']}...")
        subprocess.run(
            f"ssh -o ConnectTimeout=10 {obsidian_config['ssh_user']}@{obsidian_config['ssh_host']} mkdir -p '{folder}'",
            shell=True, check=True, capture_output=True, timeout=15
        )
        log(f"📤 Copying report...")
        subprocess.run(
            f"scp -o ConnectTimeout=10 '{temp_path}' {obsidian_config['ssh_user']}@{obsidian_config['ssh_host']}:'{folder}/{filename}'",
            shell=True, check=True, capture_output=True, timeout=15
        )
        log(f"✅ Saved to Obsidian: {folder}/{filename}")
    except subprocess.TimeoutExpired as e:
        log(f"⚠️  SSH timeout: {e}")
        # Fallback: save locally
        local_path = Path(__file__).parent / "obsidian" / filename
        local_path.parent.mkdir(exist_ok=True)
        with open(local_path, 'w') as f:
            f.write(report)
        log(f"✅ Saved locally: {local_path}")
    except subprocess.CalledProcessError as e:
        log(f"⚠️  SSH save failed: {e}")
        # Fallback: save locally
        local_path = Path(__file__).parent / "obsidian" / filename
        local_path.parent.mkdir(exist_ok=True)
        with open(local_path, 'w') as f:
            f.write(report)
        log(f"✅ Saved locally: {local_path}")
    
    # Cleanup temp
    try:
        os.remove(temp_path)
    except:
        pass

# ─── USAGE LOGGING ────────────────────────────────────────────
def log_usage(query_index, query, videos_fetched, transcripts_fetched):
    """Append usage stats to JSONL log."""
    log_entry = {
        "run_date": datetime.now().isoformat(),
        "credits_used": 30,  # 20 search + 10 transcripts
        "query_index": query_index,
        "search_query": query,
        "videos_fetched": videos_fetched,
        "transcripts_fetched": transcripts_fetched
    }
    
    log_path = LOG_DIR / "usage.jsonl"
    with open(log_path, 'a') as f:
        f.write(json.dumps(log_entry) + "\n")

# ─── CLI ──────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        log("Running manual test...")
    run()
