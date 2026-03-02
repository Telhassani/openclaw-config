# SKILL.md — Apple Mail Manager

**Purpose:** Read, search, and draft emails via Apple Mail on Mac

## Connection

- **Host:** `100.82.80.22` (Tailscale IP)
- **User:** `tariq`
- **Method:** SSH + AppleScript

## Functions

### `list_emails(count?)`
List recent emails from inbox

**Parameters:**
- `count` (optional): Number of emails (default 10)

**Returns:** Array with subject, sender, date, snippet

### `get_email(index)`
Get full email content by index

**Parameters:**
- `index`: Email number (1 = most recent)

**Returns:** Full email with subject, sender, date, body

### `search_emails(query)`
Search emails by subject/content

**Parameters:**
- `query`: Search term

**Returns:** Matching emails

### `create_draft(to, subject, body)`
Create email draft

**Parameters:**
- `to`: Recipient email
- `subject`: Email subject
- `body`: Email body

**Returns:** Confirmation (NEVER auto-send)

---

## SSH Command Template

```bash
ssh tariq@100.82.80.22 "osascript -e 'tell app \"Mail\" ...'"
```

## Implementation

Uses AppleScript to communicate with Mail app:
- `get messages of inbox` — list
- `get subject of message X` — subject
- `get sender of message X` — from
- `get content of message X` — body
- `make new outgoing message` — draft

## Important

- **NEVER send emails automatically** — always draft and get approval
- Read-only for now (no auto-send)
- Works with any email account configured in Apple Mail
