# 🧠 MEMORY.md — Long-Term Memory

**Last updated**: 2026-04-02

---

## Active Projects

1. **Neo Setup** — Initial workspace configuration, memory system implementation
2. **openclaw-config repo analysis** — Reviewed Tariq's config repo, merged SOUL.md improvements, adopted heartbeat memory cadence

**Status**: Memory system rebuilt on builtin embeddings (gemini-embedding-001 + sqlite-vec + FTS). Daily notes structure created.

---

## Key Decisions

- **2026-03-16**: Workspace bootstrapped. Agent named **Neo** (Second Brain / Main Assistant). Vibe: professional.
- **2026-04-02**: Memory system rebuilt. Adopted SOUL.md "Algorithm" framework + ISC criteria + Code Before Prompts principle. Rejected custom PostgreSQL memory_manager.py in favor of builtin memory.

---

## Lessons Learned

- **"Code Before Prompts"** — If config fixes it, don't rewrite architecture. Go left: Goal → Code → CLI → Prompt → Agent.
- **Builtin memory > external DB** — Gemini embeddings + sqlite-vec + FTS handles tiered memory without extra Docker containers, API dependencies, or credential exposure.

---

## User Context

- Owner: **Tariq** (from GitHub username Telhassani)
- Connected via webchat
- Has homelab setup (Docker, n8n, Ollama, Cloudflare tunnels)
- Works on DermaAI project

---

*Memory is curated from daily notes and significant interactions. Raw logs live in `memory/YYYY-MM-DD.md`.*
