# SKILL.md — Obsidian Vault Manager

**Purpose:** Read, write, and search notes in Obsidian vault via SSH

## Connection

- **Host:** `100.82.80.22` (Tailscale IP)
- **User:** `tariq`
- **Vault Path:** `/Users/tariq/Obsidian/`

## Functions

### `list_notes(folder?)`
List all notes in vault or folder

**Parameters:**
- `folder` (optional): Subfolder name (e.g., "TOPICS/AI")

**Returns:** Array of note paths

### `read_note(note_path)`
Read a note's content

**Parameters:**
- `note_path`: Full path relative to vault root (e.g., "TOPICS/AI/notes.md")

**Returns:** Note content

### `write_note(note_path, content)`
Create or update a note

**Parameters:**
- `note_path`: Full path (e.g., "TOPICS/Research/new-note.md")
- `content`: Markdown content

**Returns:** Confirmation

### `create_folder(folder_path)`
Create a new folder

**Parameters:**
- `folder_path`: Path relative to vault root

**Returns:** Confirmation

### `search_vault(query)`
Search notes by content

**Parameters:**
- `query`: Search term

**Returns:** Matching note paths

---

## Example Usage

```
User: "What notes do we have about AI?"
→ search_vault("AI")

User: "Show me the DermaAI roadmap"
→ read_note("TOPICS/DermaAI/DermaAI Learning Roadmap - Module 1.md")

User: "Add a note about today's meeting"
→ write_note("TOPICS/Meetings/2026-02-27.md", "# Meeting Notes\n\n- ...")

User: "List notes in TOPICS folder"
→ list_notes("TOPICS")
```

---

## Note Format

Notes use standard Markdown with YAML frontmatter:

```markdown
---
title: "Note Title"
date: "2026-02-27"
tags: [tag1, tag2]
---

# Title

Content...
```

---

## Implementation

- SSH connection to Mac
- Base64 encoding for content transfer
- File operations via `cat`, `mkdir`, `grep`
