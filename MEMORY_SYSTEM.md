# MEMORY_SYSTEM.md — DEPRECATED

**Status:** ⛔ Replaced 2026-04-02

---

This file documented the custom `memory_manager.py` + PostgreSQL + Redis memory system. It has been replaced by **OpenClaw's builtin memory** (gemini-embedding-001 + sqlite-vec + FTS), which provides the same functionality with zero extra infrastructure.

## Why It Was Replaced

1. **Extra infrastructure** — Required 2 Docker containers (memory-db, Redis) just for memory
2. **Unresolved issues** — Duplicate facts, no cron for decay/consolidation, Redis non-persistent, Telegram not auto-processed
3. **Exposed credentials** — `PGPASSWORD=memory2026` in environment + public repo
4. **Complexity overkill** — 6.4KB of documentation for what builtin memory handles natively

## What's Better Now

| | Custom System | Builtin Memory |
|---|---||---|---|
| **Storage** | PostgreSQL + Redis | sqlite-vec + FTS |
| **Embeddings** | Gemini REST API (custom patch) | Gemini gemini-embedding-001 (native) |
| **Setup** | 2 containers + env vars + Python script | One config line + memory/ directory |
| **Creds** | DB password in env + repo | None needed |
| **Issues** | 4 known unresolved | Works out of the box |

## What's Worth Keeping

The **tiered memory concept** (episodic + semantic + profile) was good architecture thinking. The Ebbinghaus decay curve idea is interesting for future enhancement. See MEMORY.md for active lessons learned from this iteration.

## Old CLI Reference

```bash
# No longer works — use OpenClaw builtin memory instead:
# openclaw memory status
# openclaw memory search "query"
# openclaw memory index
```

---

_Kept for historical reference. Active memory docs are in MEMORY.md and SOUL.md._
