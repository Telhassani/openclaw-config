# SKILL.md — Apple Notes Manager

**Purpose:** Manage Apple Notes via SSH + AppleScript

## Connection

- **Host:** `100.82.80.22` (Tailscale IP)
- **User:** `tariq`
- **Method:** SSH + AppleScript

## Functions

###?, `list_notes(account folder?)`
List all notes

**Parameters:**
- `account` (optional): Account name (default: "iCloud")
- `folder` (optional): Folder name

**Returns:** Array with id, name, modification date

### `get_note(name)`
Get note content by name

**Parameters:**
- `name`: Note name

**Returns:** Note body content

### `get_note_by_id(id)`
Get note by ID

**Parameters:**
- `id`: Note ID

**Returns:** Note content

### `create_note(title, body, account?, folder?)`
Create a new note

**Parameters:**
- `title`: Note title (required)
- `body`: Note content (required)
- `account` (optional): Account name (default: "iCloud")
- `folder` (optional): Folder name

**Returns:** Confirmation with note ID

### `update_note(name, body)`
Update note content

**Parameters:**
- `name`: Note name
- `body`: New content

**Returns:** Confirmation

### `delete_note(name)`
Delete a note

**Parameters:**
- `name`: Note name

**Returns:** Confirmation

---

## SSH Command Template

```bash
ssh tariq@100.82.80.22 "osascript -e 'tell app \"Notes\" ...'"
```

## AppleScript Commands

```applescript
-- List accounts
get name of accounts

-- List notes
get name of notes in account "iCloud"

-- Get note content
get body of note "Note Title"

-- Create note
tell account "iCloud"
    make new note with properties {name:"Title", body:"Content"}
end tell

-- Delete note
delete note "Title"
```

## Examples

```
User: "List my notes"
→ list_notes()

User: "Show me the meeting notes"
→ get_note(name: "Meeting Notes")

User: "Create a note titled 'Ideas' with content 'Buy milk, call mom'"
→ create_note(title: "Ideas", body: "Buy milk, call mom")

User: "Delete the old note"
→ delete_note(name: "Old Note")
```

## Notes

- Works with iCloud, On My Mac, and other accounts
- Notes sync via iCloud automatically
- Body supports plain text (limited formatting)
