# SKILL.md — YouTube Research

**Purpose:** Fetch YouTube video transcripts, search videos, format for Obsidian

## API

- **Provider:** TranscriptAPI
- **Key:** `sk_2lJao1zz0r5orexegkLjxJSvxFaiHhNluB5q95PdU5s`
- **Base URL:** `https://transcriptapi.com/api/v2`

## Functions

### `research_video(video_url)`
Fetch transcript → format for Obsidian

**Parameters:**
- `video_url`: YouTube URL or video ID

**Returns:**
- `title`: Video title
- `channel`: Channel name
- `formatted_note`: Markdown ready for Obsidian
- `suggested_path`: Suggested vault path

### `search_youtube(query, limit?)`
Search YouTube videos

**Parameters:**
- `query`: Search term
- `limit` (optional): Max results (default 10)

**Returns:** Video results with title, channel, videoId

### `get_channel_latest(channel_handle)`
Get latest 15 videos from a channel

**Parameters:**
- `channel_handle`: @handle, URL, or channel ID

**Returns:** Latest videos with titles, IDs

---

## CLI Usage

```bash
python app.py research "https://youtube.com/watch?v=..."
python app.py search "AI tutorial" 5
python app.py latest "@TED"
```

---

## Output Format (Obsidian)

```markdown
---
title: "[Video Title]"
date: "2026-02-27"
tags: [youtube, research]
source: YouTube
channel: "[Channel]"
url: "https://youtube.com/watch?v=..."
---

# Title

## Summary
[AI summary]

## Key Takeaways
- [0:00]: Point 1
- [5:30]: Point 2
...
```

---

## Cost

| Endpoint | Credits |
|----------|---------|
| Transcript | 1 |
| Search | 1 |
| Channel Latest | Free |

---

## Implementation

- `api_client.py` — TranscriptAPI wrapper
- `app.py` — Skill functions
