# HEARTBEAT.md

> Minimal. Tasks only.

## Tasks

- [ ] Memory maintenance: when session has done significant work, or after /compact
  1. Run `ai-memory api compact` (archives session log, starts fresh)
  2. Verify ai-memory CLI is accessible (fall back to OpenClaw memory if down)
  3. Read last 3 ai-memory entries → distill 1-2 insights → MEMORY.md
  4. Prune: no-access >30d OR low-value

---

HEARTBEAT_OK if nothing needs attention.
