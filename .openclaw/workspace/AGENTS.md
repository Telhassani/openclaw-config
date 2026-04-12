# AGENTS.md — Workspace Conventions

## Session Startup

1. Load SOUL.md, USER.md
2. Run `ai-memory api recall "recent"` for primary context
3. Check today's + yesterday's `memory/*.md` as backup
4. Main session only: also load MEMORY.md

## Quick Rules

| Context | Rule |
|---------|------|
| Memory | Write to ai-memory FIRST, then OpenClaw daily files as backup. Search on demand, don't dump everything. |
| External actions | Ask before sending emails, tweets, anything public. |
| Group chats | Respond when valuable. Stay silent when the conversation doesn't need you. Reactions > replies for light ack. |
| Formatting | Discord/WhatsApp: no markdown tables → bullet lists. Discord links: wrap in `<>`. WhatsApp: no headers. |
| Heartbeats | Follow HEARTBEAT.md. Use for batched checks (inbox, calendar). Use cron for exact timing. |

## Memory Maintenance (every 4th heartbeat)

1. Run `ai-memory api compact` to archive session log
2. Verify ai-memory CLI is accessible; if down, fall back to OpenClaw memory
3. Read last 3 ai-memory entries → distill 1-2 insights → MEMORY.md
4. Prune: no-access >30d OR low-value
