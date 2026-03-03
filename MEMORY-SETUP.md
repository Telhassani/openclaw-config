# OpenClaw Memory System

## Status: ✅ Active

- **PostgreSQL**: port 5433 (with pgvector, container: memory-db)
- **Redis**: port 6379 (container: redis-redis-on-hstgr-1)
- **Database**: `memory`

## Quick Start

### 1. Start Services
```bash
cd ~/homelab/memory && docker compose up -d
```

### 2. Use Memory

**Recall** (get context):
```bash
python3 memory_manager.py recall --user tariq --query "What is Tariq working on?"
```

**Store** (remember):
```bash
python3 memory_manager.py process --user tariq --message "Remember: Tariq prefers dark mode IDE."
```

**Maintenance** (run periodically):
```bash
python3 memory_manager.py decay --user tariq
python3 memory_manager.py consolidate --user tariq
```

## Docker CLI Reference

```bash
# Store a memory
docker exec openclaw-xura-openclaw-1 python3 /data/memory_manager.py process --user tariq --message "Remember: <fact>"

# Recall memories
docker exec openclaw-xura-openclaw-1 python3 /data/memory_manager.py recall --user tariq --query "<topic>"

# Apply memory decay
docker exec openclaw-xura-openclaw-1 python3 /data/memory_manager.py decay --user tariq

# Consolidate episodic → semantic
docker exec openclaw-xura-openclaw-1 python3 /data/memory_manager.py consolidate --user tariq
```

## Integration

Updated `SOUL.md` to use memory in the Algorithm:

- **Phase 1 (OBSERVE)**: Recall relevant memories
- **Phase 6 (LEARN)**: Process new info + trigger decay/consolidate

## Configuration

### Environment Variables

```env
PG_HOST=172.17.0.1
PG_PORT=5433
PG_DB=memory
PG_USER=tariq
PGPASSWORD=memory2026

REDIS_HOST=172.19.0.3
REDIS_PORT=6379

GEMINI_API_KEY=<your-gemini-key>
```

### Embeddings

- **Provider**: Google Gemini
- **Model**: `gemini-embedding-001`
- **Dimensions**: 3072

## Notes

- No cron daemon on VPS → run maintenance manually or add to your Mac's crontab
- See `MEMORY_SYSTEM.md` for full documentation
