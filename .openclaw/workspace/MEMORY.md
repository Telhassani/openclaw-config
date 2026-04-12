# 🧠 MEMORY.md — Long-Term Memory

**Last updated**: 2026-04-11

---

## Active Projects

| Project | Status | Notes |
|---------|--------|-------|
| **DermaAI** | Pending | Auth system (OAuth 2.0, MFA, RBAC) — DermaAI glassmorphism UI system |
| **Homelab** | Operational | n8n workflows, Ollama models, Cloudflare tunnels, Docker |
| **AI Pulse Tracker** | Production | YouTube AI/tech → Obsidian daily summaries, 9 AM cron |
| **aimem-dashboard** | Live (Phase 3) | Web app for ai-memory vault at https://aimem.tariqvps.com, Next.js 16 + Tremor v3 + shadcn/ui + Tailwind v4, glassmorphism dark theme, client-side rendering, search + write API |
| **Morning Brief** | Working | Daily email via Resend + Telegram |
| **video-summary** | Stable | Minimal (31KB), duration-based scaling, topic templates |
| **OpenClaw Config** | Active | GitHub backup repo for workspace config + skills |

---

## Infrastructure

| Component | Status | Notes |
|-----------|--------|-------|
| **VPS** | Hostinger, Docker | Port 55924, container: openclaw-xura-openclaw-1 |
| **Memory** | QMD + Active Memory | v2.1.0, indexes workspace + ai-memory-vault, recent mode, 5min refresh |
| **Ollama** | 120s timeout | Model: qwen3.5:397b-cloud |
| **aimem-dashboard** | Live (Phase 3) | Search + write API, 20 routes, https://aimem.tariqvps.com |
| **Cloudflare Tunnel (aimem)** | Connected | Tunnel ID `17bbdb24`, token `eyJh...fE2`, service `http://localhost:3000` |
| **QMD Memory Backend** | Active | v2.1.0, indexes workspace + ai-memory-vault, 5min refresh, query mode |
| **Active Memory Plugin** | Active | recent mode, balanced style, 15s timeout, agents: ["main"] |

---

## Key Decisions

- **2026-04-02**: Memory system rebuilt on OpenClaw builtin memory. Rejected custom memory_manager.py (4 unresolved issues, extra infrastructure, exposed credentials). Adopted SOUL.md Algorithm + ISC criteria from repo.
- **2026-04-12**: Resolved QMD Dashboard build loop. Fixed 'window is not defined' SSR crash via dynamic imports and corrected a port collision with the Gateway (55924 → 3000). Established 'Wipe and Rebuild' protocol for stable Next.js deployments.
- **2026-04-10**: aimem-dashboard deployed — prod build at localhost:3000, Cloudflare named tunnel connected to aimem.tariqvps.com. Key lesson: dev server (next dev) caused persistent 502s with named tunnel; production build (next start) fixed it. Tunnel config must use `http://` not `https://` for localhost service.
- **2026-03-10**: video-summary stabilized — stripped from 700KB bloat to 31KB minimal. Lesson: enhance thoughtfully, resist over-engineering.

---

## Lessons Learned

1. **"Code Before Prompts"** — If config fixes it, don't rewrite architecture. Go left: Goal → Code → CLI → Prompt → Agent.
2. **Verify API behavior against docs** — ScrapeCreators `/youtube/video` returns metadata only; `/youtube/video/transcript` is a separate call.
3. **Cleanup after testing** — Remove bloat immediately. Don't let artifacts accumulate.
4. **Builtin memory > external DB** — Gemini embeddings + sqlite-vec + FTS handles tiered memory without extra containers, API dependencies, or exposed credentials.
5. **Scaffold first, trim later** — Build the structure, then cut what doesn't earn its weight (video-summary 700KB→31KB pattern).
6. **Test after major modifications** — Always verify changes work immediately after applying them. Call the tool/endpoint/API, check the result. Applies to config changes, code changes, system modifications. Don't assume.
7. **No commits without explicit validation** — Never `git commit` or push code before the user has explicitly reviewed and approved it. Test first, show results, wait for approval.

---

## API Patterns & Fixes

| Service | Fix | Notes |
|---------|-----|-------|
| **ScrapeCreators** | `x-api-key` header, not `Authorization: Bearer` | Auth endpoint |
| **ScrapeCreators** | `url` param for transcript, not `video_id` | Transcript endpoint |
| **Ollama** | `qwen3.5:397b-cloud` native name | Model reference |
| **ScrapeCreators** | Channel returns dict `{title, handle, id, thumbnail}` | Template renders `channel['title']` |

---

*Memory is curated from daily notes (`memory/YYYY-MM-DD.md`) and significant interactions. Raw logs live in daily files. This is the distilled wisdom, not the timeline.*

---

## SSH Access & Infrastructure (2026-04-03)

### Connections established

| Target | Method | Details |
|--------|--------|---------|
| **Mac (Tariq's MacBook Pro)** | SSH | `ssh -o IdentitiesOnly=yes -i ~/.ssh/id_ed25519 tariq@100.82.80.22` — macOS 25.4.0, Apple Silicon T6000, OpenClaw 2026.4.2 running, Gateway on localhost:18789. **Must use `-o IdentitiesOnly=yes`** to avoid "Too many auth failures" |
| **VPS Container** | Direct exec | Linux 6.8.0, x86_64, container `0eefeda55440`, OpenClaw Gateway on localhost:18789, port 55924 exposed |
| **Mac public key** | — | `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOONvo0rCybW01dCRrAA3Acu9XwuftMjb2ZGkmT4Hyw8 elhassani.tariq@gmail.com` |
| **Container SSH key** | — | `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPgEVRBKj8z1+fIybN8/7bLivQbJAiLFU23/fCUg5Rzv openclaw-vps` |

### URLs

| Service | URL | Status |
|---------|-----|--------|
| **ZENITH (planned)** | https://zenith.tariqvps.com | Not built yet — Phase 0 only (PLAN.md deployed) |
| **PKOS Dashboard** | https://pkos.tariqvps.com | Live, Phase 1-8 complete |
| **PKOS MCP** | https://mcp.tariqvps.com/mcp | Live, 21 MCP tools |
| **aimem-dashboard** | https://aimem.tariqvps.com | Live, Cloudflare tunnel → localhost:3000 |
| **OpenClaw Control (container)** | http://localhost:55924 | Login page, port 55924 |

### Repos

| Repo | URL | Status |
|------|-----|--------|
| **ZENITH** | https://github.com/Telhassani/ZENITH | Phase 0 plan committed, PHASE1_IMPLEMENTATION_PLAN.md pushed (commit e76f78f) |
| **PKOS** | https://github.com/Telhassani/PKOS | Phase 1-8 complete, live |
| **aimem-dashboard** | https://github.com/Telhassani/aimem-dashboard | Live, commit b6b4af9 |
