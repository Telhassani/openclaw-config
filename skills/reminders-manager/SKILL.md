# SKILL.md — Apple Reminders Manager

**Purpose:** Manage Apple Reminders via SSH + CLI

## Connection

- **Host:** `100.82.80.22` (Tailscale IP)
- **User:** `tariq`
- **Method:** SSH + `reminders` CLI (macOS) or AppleScript

## Functions

### `list_reminders(listName?)`
List reminders

**Parameters:**
- `listName` (optional): Specific list name (default: all lists)

**Returns:** Array of reminders with id, title, due date, completed status

### `add_reminder(title, listName?, dueDate?, notes?)`
Add a new reminder

**Parameters:**
- `title`: Reminder text (required)
- `listName` (optional): List name (default: "Reminders")
- `dueDate` (optional): Due date ISO string
- `notes` (optional): Notes/comments

**Returns:** Created reminder with ID

### `complete_reminder(reminderId)`
Mark reminder as completed

**Parameters:**
- `reminderId`: The reminder ID

**Returns:** Confirmation

### `delete_reminder(reminderId)`
Delete a reminder

**Parameters:**
- `reminderId`: The reminder ID

**Returns:** Confirmation

### `update_reminder(reminderId, fields)`
Update reminder fields

**Parameters:**
- `reminderId`: The reminder ID
- `fields`: Object with fields to update (title, dueDate, notes)

**Returns:** Updated reminder

---

## macOS Commands

```bash
# List all reminders
ssh tariq@100.82.80.22 "reminders list"

# Add reminder
ssh tariq@100.82.80.22 "reminders add 'Buy milk' to 'Shopping'"

# Complete reminder
ssh tariq@100.82.80.22 "reminders complete <id>"

# Delete reminder
ssh tariq@100.82.80.22 "reminders delete <id>"
```

---

## Usage Examples

```
User: "What's on my todo list?"
→ list_reminders()

User: "Add a reminder to review DermaAI auth"
→ add_reminder(title: "Review DermaAI auth", listName: "Work", dueDate: "2026-02-28")

User: "Mark the meeting reminder as done"
→ complete_reminder(reminderId: "x-apple-reminder://...")

User: "Delete that old reminder"
→ delete_reminder(reminderId: "...")
```

---

## Implementation Notes

- Uses `reminders` CLI (macOS Sequoia+)
- Falls back to AppleScript if CLI unavailable
- Lists are created automatically if they don't exist
- Due dates support natural language ("tomorrow", "next Monday")
