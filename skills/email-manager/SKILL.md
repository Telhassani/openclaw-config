# SKILL.md — Gmail Manager

**Purpose:** Read, search, and draft emails via Gmail API

## Authentication

Uses OAuth 2.0 with credentials from `~/.openclaw/google-credentials.json`

**Scopes required:**
- `https://www.googleapis.com/auth/gmail.readonly` (read emails)
- `https://www.googleapis.com/auth/gmail.compose` (drafts)
- `https://www.googleapis.com/auth/gmail.send` (send - use with caution)

## Functions

### `list_emails(maxResults?, query?, labelIds?)`
List emails from inbox

**Parameters:**
- `maxResults` (optional): Number of emails (default 10)
- `query` (optional): Gmail search query (e.g., "is:unread", "from:john@example.com")
- `labelIds` (optional): Filter by labels (INBOX, SENT, DRAFT, SPAM, TRASH)

**Returns:** Array of email summaries (id, threadId, subject, from, snippet, date)

### `get_email(emailId)`
Get full email content

**Parameters:**
- `emailId`: The email ID (required)

**Returns:** Full email object with body (text/html), headers, labels

### `search_emails(query, maxResults?)`
Search emails

**Parameters:**
- `query`: Gmail search query (required)
- `maxResults` (optional): Number of results (default 10)

**Returns:** Array of matching email summaries

### `create_draft(to, subject, body, from?)`
Create an email draft

**Parameters:**
- `to`: Recipient email (required)
- `subject`: Email subject (required)
- `body`: Email body (required)
- `from` (optional): Sender email (default: primary account)

**Returns:** Draft object with draftId

### `send_email(to, subject, body, from?)`
Send an email (requires explicit user approval each time)

**Parameters:**
- `to`: Recipient email (required)
- `subject`: Email subject (required)
- `body`: Email body (required)
- `from` (optional): Sender email

**Returns:** Sent message object

---

## Usage Examples

```
User: "Any new emails?"
→ list_emails(maxResults: 5, labelIds: ["INBOX"])

User: "Search for emails from Amazon"
→ search_emails(query: "from:amazon.com")

User: "Show me that email about the project"
→ get_email(emailId: "abc123...")

User: "Draft a reply to Ahmed about the meeting"
→ create_draft(to: "ahmed@example.com", subject: "Re: Meeting", body: "Hi Ahmed,...")
```

---

## Important Rules

1. **NEVER send emails without explicit user approval** — always draft first
2. **Present drafts for review** before sending
3. Respect user privacy — don't store email contents permanently

---

## Implementation Notes

- Uses Gmail API v1
- OAuth token stored alongside calendar token after first auth
- Body returned as either text/plain or text/html (prefer text/plain for readability)
- Dates in RFC 3339 format
