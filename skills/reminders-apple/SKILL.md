# SKILL.md — Apple Reminders Manager

**Purpose:** Manage Apple Reminders via SSH + AppleScript

## Connection

- **Host:** `100.82.80.22` (Tailscale IP)
- **User:** `tariq`
- **Method:** SSH + AppleScript

## Functions

### `list_reminders(listName?)`
List reminders from a list

**Parameters:**
- `listName` (optional): List name (default: "Reminders")

**Returns:** Array with id, name, due date, completed status

### `add_reminder(title, listName?, dueDate?)`
Add a new reminder

**Parameters:**
- `title`: Reminder text (required)
- `listName` (optional): List name (default: "Reminders")
- `dueDate` (optional): Due date (e.g., "tomorrow", "next Monday", "2026-02-28")

**Returns:** Confirmation with reminder ID

### `complete_reminder(name)`
Mark reminder as completed

**Parameters:**
- `name`: Reminder name or ID

**Returns:** Confirmation

### `delete_reminder(name)`
Delete a reminder

**Parameters:**
- `name`: Reminder name or ID

**Returns:** Confirmation

---

## SSH Command Template

```bash
ssh tariq@100.82.80.22 "osascript -e 'tell app \"Reminders\" ...'"
```

## AppleScript Commands

```applescript
-- List lists
get name of lists

-- List reminders in a list
get name of reminders in list "Reminders"

-- Add reminder
make new reminder in list "Reminders" with properties {name:"Task", due date:date "tomorrow"}

-- Complete reminder
set completed of reminder "Task" to true

-- Delete reminder
delete reminder "Task"
```

## Examples

```
User: "What's on my todo list?"
→ list_reminders()

User: "Remind me to call Ahmed tomorrow"
→ add_reminder(title: "Call Ahmed", dueDate: "tomorrow")

User: "Mark the meeting as done"
→ complete_reminder(name: "Meeting with team")

User: "Delete old reminder"
→ delete_reminder(name: "Old task")
```

## Notes

- Works with any Reminders list (iCloud, local, etc.)
- Natural language dates supported ("tomorrow", "next week")
- IDs are persistent across syncs
