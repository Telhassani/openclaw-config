# 🧠 OpenClaw Dynamic Memory

## Latest Update: 2026-03-10

### Skill: Video-Summary Fix
- **Fixed**: Config (API key, Ollama endpoint, model)
- **Added**: `call_ollama_summary()` (30 lines in app.py)
- **Removed**: Over-engineered bloat (zettelkasten, backlinks, test artifacts)
- **Size**: 31KB (was 25KB original, bloated to ~700KB, now minimal again)

### Disk Space:
- **Freed**: ~1.4GB (gcc@12, binutils, caches, node_modules)
- **Current**: 1.1GB free (was 760MB)

### Lesson:
> "Code Before Prompts" — If config fixes it, don't rewrite architecture. Cleanup immediately after testing.

---

## Active Projects:
1. **DermaAI** — Auth system (OAuth, MFA, RBAC)
2. **Homelab** — n8n, Ollama, Cloudflare tunnels
3. **Morning Brief** — Daily email via Resend + Telegram
4. **video-summary** — Fixed, working (minimal now)

---

**Last updated**: 2026-03-10 19:32

---

## Latest Update: 2026-03-13 03:38 UTC

### Skill: AI Pulse Tracker — Production Complete
- **Built**: Full YouTube AI/tech scraper → rank → summarize → Obsidian pipeline
- **Architecture**: Python skill, 10 rotating search queries, 4 categories (Local LLM, Agents, Models, Infra)
- **Credit optimization**: 30 credits/run (20 search + 10 transcripts)
- **Ollama timeout**: 120s (eliminates 500 errors)
- **Output**: `~/Obsidian/AI-PULSE/YYYY-MM-DD.md` daily at 9:00 AM Europe/Paris
- **Test run**: 26 videos fetched → 10 transcripts → 10 summaries → SSH to Mac ✅
- **Cron**: Installed for 9 AM daily (isolated session)

### API Fixes (ScrapeCreators)
- **Auth**: `x-api-key` header (not `Authorization: Bearer`)
- **Transcript**: `url` param (not `video_id`)
- **Model**: `qwen3.5:397b-cloud` (native Ollama name)
- **Channel format**: API returns dict `{title, handle, id, thumbnail}` — template renders `channel['title']`

---

## Latest Update: 2026-03-13 20:02 UTC

### Heartbeat #122 — Memory Maintenance Cycle

**Distilled Insights:**
1. **Video-summary API fix (03-06)**: ScrapeCreators `/youtube/video` returns metadata only; must call `/youtube/video/transcript` separately for transcript text. Pattern: Always verify API behavior against docs.
2. **Video-summary enhancement trajectory (03-09 → 03-10)**: Added duration-based scaling (3 tiers) + 6 topic templates → then bloated to 700KB → trimmed back to 31KB. Lesson: Enhance thoughtfully, but resist over-engineering. "Code Before Prompts" validated.

**Active Projects Status:**
- **DermaAI**: Auth system (OAuth, MFA, RBAC) — pending implementation
- **Homelab**: n8n, Ollama, Cloudflare tunnels — operational
- **Morning Brief**: Resend + Telegram pipeline — installed, tested, working
- **AI Pulse Tracker**: YouTube AI/tech scraper → Obsidian — production complete (9 AM daily cron)
- **video-summary**: Duration scaling + templates + minimal (31KB) — stable

**Next Maintenance**: Heartbeat #126

---

