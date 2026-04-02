# 🧠 MEMORY.md — Long-Term Memory

**Last updated**: 2026-04-02

---

## Active Projects

| Project | Status | Notes |
|---------|--------|-------|
| **DermaAI** | Pending | Auth system (OAuth 2.0, MFA, RBAC) — DermaAI glassmorphism UI system |
| **Homelab** | Operational | n8n workflows, Ollama models, Cloudflare tunnels, Docker |
| **AI Pulse Tracker** | Production | YouTube AI/tech → Obsidian daily summaries, 9 AM cron |
| **Morning Brief** | Working | Daily email via Resend + Telegram |
| **video-summary** | Stable | Minimal (31KB), duration-based scaling, topic templates |
| **OpenClaw Config** | Active | GitHub backup repo for workspace config + skills |

---

## Infrastructure

| Component | Status | Notes |
|-----------|--------|-------|
| **VPS** | Hostinger, Docker | Port 55924, container: openclaw-xura-openclaw-1 |
| **Memory** | Builtin (replaced custom system) | gemini-embedding-001 + sqlite-vec + FTS |
| **Ollama** | 120s timeout | Model: qwen3.5:397b-cloud |

---

## Key Decisions

- **2026-04-02**: Memory system rebuilt on OpenClaw builtin memory. Rejected custom memory_manager.py (4 unresolved issues, extra infrastructure, exposed credentials). Adopted SOUL.md Algorithm + ISC criteria from repo.
- **2026-03-13**: AI Pulse Tracker deployed — 10 rotating YouTube searches, 4 categories, 30 credits/run, SSH to Mac for Obsidian output.
- **2026-03-10**: video-summary stabilized — stripped from 700KB bloat to 31KB minimal. Lesson: enhance thoughtfully, resist over-engineering.

---

## Lessons Learned

1. **"Code Before Prompts"** — If config fixes it, don't rewrite architecture. Go left: Goal → Code → CLI → Prompt → Agent.
2. **Verify API behavior against docs** — ScrapeCreators `/youtube/video` returns metadata only; `/youtube/video/transcript` is a separate call.
3. **Cleanup after testing** — Remove bloat immediately. Don't let artifacts accumulate.
4. **Builtin memory > external DB** — Gemini embeddings + sqlite-vec + FTS handles tiered memory without extra containers, API dependencies, or exposed credentials.
5. **Scaffold first, trim later** — Build the structure, then cut what doesn't earn its weight (video-summary 700KB→31KB pattern).

---

## API Patterns & Fixes

| Service | Fix | Notes |
|---------|-----|-------|
| **ScrapeCreators** | `x-api-key` header, not `Authorization: Bearer` | Auth endpoint |
| **ScrapeCreators** | `url` param for transcript, not `video_id` | Transcript endpoint |
| **Ollama** | `qwen3.5:397b-cloud` native name | Model reference |
| **ScrapeCreators** | Channel returns dict `{title, handle, id, thumbnail}` | Template: `channel['title']` |

---

*This is distilled wisdom, not a timeline. Raw logs → `memory/YYYY-MM-DD.md`*
