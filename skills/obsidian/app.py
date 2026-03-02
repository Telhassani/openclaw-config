#!/usr/bin/env python3
"""
Obsidian Vault Manager - SSH-based
"""
import subprocess
import json
import os
import sys
import base64

HOST = "100.82.80.22"
USER = "tariq"
VAULT_PATH = "/Users/tariq/Obsidian"

def ssh_run(cmd):
    """Run command via SSH"""
    result = subprocess.run(
        ["ssh", f"{USER}@{HOST}", cmd],
        capture_output=True,
        text=True
    )
    return result.stdout.strip(), result.stderr.strip()

def list_notes(folder=None):
    """List all notes in vault or folder"""
    if folder:
        path = f"{VAULT_PATH}/{folder}"
    else:
        path = VAULT_PATH
    
    cmd = f"find '{path}' -name '*.md' -type f 2>/dev/null | head -50"
    out, err = ssh_run(cmd)
    
    notes = []
    for line in out.split("\n"):
        if line.strip():
            rel_path = line.replace(VAULT_PATH + "/", "")
            notes.append(rel_path)
    
    return {"vault_path": VAULT_PATH, "notes": notes}

def read_note(note_path):
    """Read a note's content"""
    if not note_path.endswith(".md"):
        note_path += ".md"
    
    full_path = f"{VAULT_PATH}/{note_path}"
    cmd = f"cat '{full_path}'"
    
    out, err = ssh_run(cmd)
    
    if err and "No such file" in err:
        return {"error": f"Note not found: {note_path}", "path": note_path}
    
    return {"path": note_path, "content": out}

def write_note(note_path, content):
    """Create or update a note using base64 to avoid shell escaping issues"""
    if not note_path.endswith(".md"):
        note_path += ".md"
    
    full_path = f"{VAULT_PATH}/{note_path}"
    
    # Create directory if needed
    dir_path = os.path.dirname(full_path)
    ssh_run(f"mkdir -p '{dir_path}'")
    
    # Encode content as base64 to avoid escaping issues
    content_b64 = base64.b64encode(content.encode('utf-8')).decode('ascii')
    
    # Decode and write on remote
    cmd = f"echo '{content_b64}' | base64 -d > '{full_path}'"
    out, err = ssh_run(cmd)
    
    if err:
        return {"status": "error", "error": err, "path": note_path}
    
    return {"status": "success", "path": note_path, "message": "Note saved"}

def create_folder(folder_path):
    """Create a folder in vault"""
    full_path = f"{VAULT_PATH}/{folder_path}"
    cmd = f"mkdir -p '{full_path}'"
    
    out, err = ssh_run(cmd)
    
    if err:
        return {"status": "error", "error": err}
    
    return {"status": "success", "folder": folder_path}

def search_vault(query):
    """Search notes by content"""
    cmd = f"grep -r -l -i '{query}' {VAULT_PATH} 2>/dev/null | head -20"
    
    out, err = ssh_run(cmd)
    
    files = []
    for line in out.split("\n"):
        if line.strip():
            rel_path = line.replace(VAULT_PATH + "/", "")
            files.append(rel_path)
    
    return {"query": query, "results": files}

def get_folders():
    """List top-level folders in vault"""
    cmd = f"ls -d {VAULT_PATH}/*/ 2>/dev/null"
    out, err = ssh_run(cmd)
    
    folders = []
    for line in out.split("\n"):
        if line.strip():
            folder = line.replace(VAULT_PATH + "/", "").replace("/", "")
            folders.append(folder)
    
    return {"folders": folders}

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "list"
    
    if action == "list":
        folder = sys.argv[2] if len(sys.argv) > 2 else None
        result = list_notes(folder)
        print(json.dumps(result, indent=2))
    
    elif action == "read":
        path = sys.argv[2] if len(sys.argv) > 2 else ""
        if not path:
            print("Usage: python app.py read <note_path>")
            sys.exit(1)
        result = read_note(path)
        print(json.dumps(result, indent=2))
    
    elif action == "write":
        path = sys.argv[2] if len(sys.argv) > 2 else ""
        if not path:
            print("Usage: python app.py write <path>")
            sys.exit(1)
        # Read content from stdin if path provided
        result = write_note(path, "Test content from @scholar")
        print(json.dumps(result, indent=2))
    
    elif action == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        if not query:
            print("Usage: python app.py search <query>")
            sys.exit(1)
        result = search_vault(query)
        print(json.dumps(result, indent=2))
    
    elif action == "folders":
        result = get_folders()
        print(json.dumps(result, indent=2))
    
    elif action == "mkdir":
        folder = sys.argv[2] if len(sys.argv) > 2 else ""
        if not folder:
            print("Usage: python app.py mkdir <folder>")
            sys.exit(1)
        result = create_folder(folder)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown action: {action}")
        print("Usage: python app.py <list|read|write|search|folders|mkdir> [args]")
