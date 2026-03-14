# AI Pulse Tracker Skill

Daily intelligence digest for AI/tech trends — scrapes YouTube, ranks by actionability, delivers Top 10 to Obsidian.

## Features

- **Topic-Focused:** 4 categories (Local LLM, Multi-Agent, Models, Infrastructure)
- **Credit-Optimized:** 30 credits/run (50% savings vs. naive approach)
- **Actionability Scoring:** Ranks by "can I build this?" not just views
- **Homelab-Friendly:** Flags what you can actually deploy locally
- **Daily Cron:** 9:00 AM Europe/Paris
- **Obsidian Integration:** Auto-saves to `~/Obsidian/AI-PULSE/YYYY-MM-DD.md`

## Architecture

```
skills/ai-pulse-tracker/
├── app.py              # Main orchestrator
├── config.json         # Search queries + API credentials
├── fetcher.py          # YouTube search + transcript retrieval
├── ranker.py           # Score + rank by relevance
├── summarizer.py       # Ollama-powered summaries
├── templates.py        # Markdown report renderer
└── logs/
    └── usage.jsonl     # API credit tracking
```

## Setup

### 1. Install Dependencies
```bash
cd skills/ai-pulse-tracker
pip install requests
```

### 2. Configure API Key
Edit `config.json`:
```json
{
  "api": {
    "provider": "scrapecreators",
    "key": "YOUR_KEY_HERE"
  }
}
```

### 3. Test Manually
```bash
python3 app.py --manual
```

### 4. Deploy Cron
```bash
# Gateway cron (9:00 AM daily)
0 9 * * * cd /data/.openclaw/workspace/skills/ai-pulse-tracker && python3 app.py >> logs/ai-pulse.log 2>&1
```

## Usage

### Manual Run
```bash
python3 app.py --manual
```

### Output
- **Report:** `~/Obsidian/AI-PULSE/YYYY-MM-DD.md`
- **Logs:** `skills/ai-pulse-tracker/logs/usage.jsonl`

## Search Queries (10-Day Rotation)

1. Local LLM workflow implementation 2026
2. Run LLM locally tutorial Ollama
3. Self-hosted LLM production deployment
4. Multi-agent AI system architecture
5. AI agents workflow automation
6. LLM agent framework comparison
7. New AI model release 2026 benchmark
8. Best open source LLM 2026
9. AI inference optimization production
10. RAG pipeline implementation tutorial

## Categories

| Category | Keywords |
|----------|----------|
| Local LLM | llama, ollama, local, self-hosted, quantization, workflow |
| Agents | agent, multi-agent, autonomous, workflow, crew, langgraph |
| Models | model, release, benchmark, MMLU, weights, open source |
| Infrastructure | RAG, inference, pipeline, deployment, production, optimization |

## API Credits

- **Per Run:** 30 credits (20 search + 10 transcripts)
- **Daily:** ~30 credits
- **Monthly:** ~900 credits
- **Cost:** ~$0.90–1.70/month (depending on plan)

## Report Structure

```markdown
# AI Pulse Report — 2026-03-12

## Top 10 AI Stories (Ranked)
### #1 — [Title]
- Category: Local LLM
- Source: [Channel]
- Actionability: 🔥 High
- TL;DR: [Summary]
- Link: [URL]

## Trending Topics (Today)
- Category breakdown
- Actionability distribution

## Category Highlights
- Local LLM
- Multi-Agent
- Models
- Infrastructure

## Sources Breakdown
- Credits used
- Videos processed
```

## License

ISC — Same as OpenClaw skills
