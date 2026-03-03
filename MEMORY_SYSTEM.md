# OpenClaw Memory System
## Implementation Documentation

**Status:** ✅ Live
**Implemented:** 2026-03-03
**Author:** Tariq (with Claude)

---

## What This Is

A persistent, tiered memory system for OpenClaw that allows it to remember information across conversations — including from Telegram. Before this implementation, every conversation started from zero. Now OpenClaw accumulates knowledge over time.

---

## Architecture

```
User (Telegram / Web UI)
  ↓
OpenClaw (Docker: openclaw-xura-openclaw-1, port 55924)
  ↓
memory_manager.py (/data/memory_manager.py inside container)
  ↓
  ↓
PostgreSQL + pgvector          Redis
(memory-db, port 5433)         (redis-redis-on-hstgr-1, port 6379)
  ↓                              ↓
Episodic + Semantic memory    Working memory (session state)
```

---

## Memory Tiers

| Tier | Storage | Purpose | TTL |
|------|---------|---------|-----|
| Tier 0 | In-context | Last 3–5 exchanges | Ephemeral |
| Tier 1 | Redis | Session state, active topics | 1 hour |
| Tier 2 | PostgreSQL | Episodic memory (events) | 90 days with decay |
| Tier 3 | PostgreSQL + pgvector | Semantic memory (facts + embeddings) | Indefinite |
| Tier 4 | PostgreSQL | User profile (archival) | Indefinite |

---

## Infrastructure

### Container: memory-db

```yaml
# ~/homelab/memory/docker-compose.yml
services:
  memory-db:
    image: pgvector/pgvector:pg16
    container_name: memory-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: memory
      POSTGRES_USER: tariq
      POSTGRES_PASSWORD: memory2026
    ports:
      - "5433:5432"
    volumes:
      - memory_postgres_data:/var/lib/postgresql/data
```

### Database Tables

```sql
-- Episodic memory: what happened
CREATE TABLE episodic_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  event_summary TEXT NOT NULL,
  entities_involved TEXT[],
  emotional_valence TEXT DEFAULT 'neutral',
  importance_score FLOAT DEFAULT 0.5,
  decay_rate FLOAT DEFAULT 1.0,
  tags TEXT[],
  raw_content_hash TEXT,
  session_id TEXT,
  user_id TEXT,
  consolidated BOOLEAN DEFAULT FALSE
);

-- Semantic memory: facts + vector embeddings
CREATE TABLE semantic_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  fact TEXT NOT NULL,
  category TEXT,
  confidence FLOAT DEFAULT 0.5,
  source_episodes UUID[],
  last_confirmed TIMESTAMPTZ DEFAULT NOW(),
  embedding vector(3072) -- Gemini text-embedding-004 dimensions
);

-- User profile: archival
CREATE TABLE user_profile (
  user_id TEXT PRIMARY KEY,
  name TEXT,
  communication_style TEXT,
  key_facts JSONB DEFAULT '{}',
  recurring_themes TEXT[],
  preferences JSONB DEFAULT '{}',
  session_count INT DEFAULT 0,
  total_interactions INT DEFAULT 0,
  last_summarized TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Key Files

| File | Location | Purpose |
|------|----------|---------|
| `memory_manager.py` | `/data/memory_manager.py` | Core memory engine |
| `SOUL.md` | `/data/.openclaw/workspace/SOUL.md` | OpenClaw brain — already had memory hooks |
| `.env` | `/docker/openclaw-xura/.env` | Environment variables |
| `docker-compose.yml` | `~/homelab/memory/docker-compose.yml` | memory-db container |

---

## Environment Variables

```env
# Added to /docker/openclaw-xura/.env
PG_HOST=172.17.0.1
PG_PORT=5433
PG_DB=memory
PG_USER=tariq
PGPASSWORD=memory2026
GEMINI_API_KEY=<your-gemini-key>

REDIS_HOST=172.19.0.3
REDIS_PORT=6379
```

---

## Embeddings

**Provider:** Google Gemini
**Model:** `gemini-embedding-001`
**Dimensions:** 3072
**Cost:** Free tier

Gemini was chosen over OpenAI because the API key was already available in the OpenClaw `.env`. The `memory_manager.py` was patched to replace the OpenAI embedding call with a direct Gemini REST call using `urllib`.

---

## How Memory Works

### Writing (after each message)

```bash
python3 /data/memory_manager.py process --user tariq --message "<text>"
```

1. Extracts entities from message
2. Scores importance (0.0–1.0)
3. If importance >= 0.3 → writes to episodic memory
4. If message contains a fact → generates embedding → writes to semantic memory
5. Updates Redis working memory

### Reading (before each LLM call)

```bash
python3 /data/memory_manager.py recall --user tariq --query "<topic>"
```

Returns formatted context block:

```markdown
## User Profile
## Known Facts
## Recent Memory
## Current Session Goal
```

### Importance Scoring

| Signal | Score Added |
|--------|-------------|
| New information (not in memory) | +0.3 |
| Entity density (per entity) | +0.1 (max 0.3) |
| Emotional markers (urgent, critical) | +0.2 |
| Explicit "Remember:" prefix | +0.4 |
| Threshold to store | >= 0.3 |

### Memory Decay (Ebbinghaus Forgetting Curve)

```
R = e^(-t/S)
t = days since stored
S = importance_score × 30 (stability in days)
```

Memories below 20% retention are either compressed to semantic facts (if importance > 0.8) or deleted.

---

## CLI Reference

```bash
# Store a memory
docker exec openclaw-xura-openclaw-1 python3 /data/memory_manager.py \
  process --user tariq --message "Remember: <fact>"

# Recall memories
docker exec openclaw-xura-openclaw-1 python3 /data/memory_manager.py \
  recall --user tariq --query "<topic>"

# Apply memory decay
docker exec openclaw-xura-openclaw-1 python3 /data/memory_manager.py \
  decay --user tariq

# Consolidate episodic → semantic
docker exec openclaw-xura-openclaw-1 python3 /data/memory_manager.py \
  consolidate --user tariq
```

---

## Known Issues & Future Work

| Issue | Status | Fix |
|-------|--------|-----|
| Duplicate facts stored | Minor | Add semantic deduplication check before insert |
| No cron for decay/consolidation | Open | Add to Mac crontab or n8n scheduled workflow |
| Redis not persistent across reboots | Open | Add `docker network connect` to startup script |
| Telegram messages not auto-processed | Open | OpenClaw SOUL.md hooks trigger on agent judgment, not automatically |

---

## Maintenance

```bash
# Check memory-db is running
docker ps | grep memory-db

# View stored memories
docker exec memory-db psql -U tariq -d memory \
  -c "SELECT event_summary, importance_score FROM episodic_memory ORDER BY timestamp DESC LIMIT 10;"

# View semantic facts
docker exec memory-db psql -U tariq -d memory \
  -c "SELECT fact, confidence, category FROM semantic_memory;"

# Restart memory-db if needed
cd ~/homelab/memory && docker compose restart
```
