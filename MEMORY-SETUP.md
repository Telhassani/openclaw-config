# OpenClaw Memory System

## Status: ✅ Active

- **PostgreSQL**: port 5432 (with pgvector)
- **Redis**: port 6380
- **Database**: `memory`

## Quick Start

### 1. Start Services
```bash
./scripts/start-memory.sh
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

## Integration

Updated `SOUL.md` to use memory in the Algorithm:

- **Phase 1 (OBSERVE)**: Recall relevant memories
- **Phase 6 (LEARN)**: Process new info + trigger decay/consolidate

## Notes

- No cron daemon on VPS → run maintenance manually or add to your Mac's crontab
- Embeddings use OpenAI (set `OPENAI_API_KEY` env var) or fall back to random vectors
