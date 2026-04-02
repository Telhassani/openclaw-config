# SKILL.md — Google Calendar Manager

**Purpose:** CRUD operations on Google Calendar via Google Calendar API v3

## Authentication

Uses OAuth 2.0 with credentials from `~/.openclaw/google-credentials.json`

**Scopes required:**
- `https://www.googleapis.com/auth/calendar` (full access)
- `https://www.googleapis.com/auth/calendar.events`

## Functions

### `list_events(maxResults?, timeMin?, timeMax?, q?)`
List calendar events

**Parameters:**
- `maxResults` (optional): Number of events (default 10)
- `timeMin` (optional): Start time ISO string (default: now)
- `timeMax` (optional): End time ISO string
- `q` (optional): Search query

**Returns:** Array of event objects with id, summary, start, end, description

### `create_event(summary, startTime, endTime, description?, location?, attendees?)`
Create a new calendar event

**Parameters:**
- `summary`: Event title (required)
- `startTime`: Start ISO 8601 (required)
- `endTime`: End ISO 8601 (required)
- `description` (optional): Event description
- `location` (optional): Location string
- `attendees` (optional): Array of email strings

**Returns:** Created event object

### `update_event(eventId, fields)`
Update an existing event

**Parameters:**
- `eventId`: The event ID (required)
- `fields`: Object with fields to update (summary, startTime, endTime, description, location)

**Returns:** Updated event object

### `delete_event(eventId)`
Delete an event

**Parameters:**
- `eventId`: The event ID to delete

**Returns:** Success confirmation

### `get_event(eventId)`
Get a single event by ID

**Parameters:**
- `eventId`: The event ID

**Returns:** Event object

---

## Usage Examples

```
User: "What's on my calendar today?"
→ list_events(timeMin: "2026-02-27T00:00:00Z", timeMax: "2026-02-27T23:59:59Z")

User: "Schedule a meeting with Ahmed tomorrow at 3pm for 1 hour"
→ create_event(summary: "Meeting with Ahmed", startTime: "2026-02-28T15:00:00Z", endTime: "2026-02-28T16:00:00Z")

User: "Cancel the dentist appointment"
→ delete_event(eventId: "abc123...")
```

---

## Implementation Notes

- Uses Google Calendar API v3
- OAuth token stored in `~/.openclaw/credentials/google-calendar.json` after first auth
- Time zones handled automatically (user is Europe/Paris)
- Uses 'primary' calendar by default
