#!/usr/bin/env python3
"""Apple Notes via SSH + AppleScript"""
import subprocess
import json

HOST = "100.82.80.22"
USER = "tariq"

def ssh_run(script):
    cmd = ["ssh", f"{USER}@{HOST}", "osascript", "-e", script]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()

def list_notes(account="iCloud", folder=None):
    if folder:
        script = f'''
        tell application "Notes"
            set noteList to {{}}
            repeat with n in (get notes in folder "{folder}" in account "{account}")
                set nName to name of n
                set nMod to modification date of n
                set nId to id of n
                set end of noteList to (nName & "|||" & (nMod as string) & "|||" & nId)
            end repeat
            return noteList
        end tell
        '''
    else:
        script = f'''
        tell application "Notes"
            set noteList to {{}}
            repeat with n in (get notes in account "{account}")
                set nName to name of n
                set nMod to modification date of n
                set nId to id of n
                set end of noteList to (nName & "|||" & (nMod as string) & "|||" & nId)
            end repeat
            return noteList
        end tell
        '''
    out, err = ssh_run(script)
    if err:
        return {"error": err}
    
    notes = []
    for line in out.split("\n"):
        if "|||" in line:
            parts = line.split("|||")
            notes.append({
                "name": parts[0],
                "modified": parts[1] if len(parts) > 1 else "",
                "id": parts[2] if len(parts) > 2 else ""
            })
    return {"account": account, "notes": notes}

def get_note(name):
    script = f'''
    tell application "Notes"
        set n to note "{name}"
        return name of n & "|||" & body of n
    end tell
    '''
    out, err = ssh_run(script)
    if err:
        return {"error": err}
    
    parts = out.split("|||", 1)
    return {
        "name": parts[0] if len(parts) > 0 else "",
        "body": parts[1] if len(parts) > 1 else ""
    }

def create_note(title, body, account="iCloud", folder=None):
    if folder:
        script = f'''
        tell application "Notes"
            tell account "{account}"
                tell folder "{folder}"
                    make new note with properties {{name:"{title}", body:"{body}"}}
                end tell
            end tell
            return "Note created"
        end tell
        '''
    else:
        script = f'''
        tell application "Notes"
            tell account "{account}"
                make new note with properties {{name:"{title}", body:"{body}"}}
            end tell
            return "Note created"
        end tell
        '''
    out, err = ssh_run(script)
    return {"status": "success" if not err else err, "note": title}

def update_note(name, body):
    script = f'''
    tell application "Notes"
        set n to note "{name}"
        set body of n to "{body}"
        return "Note updated"
    end tell
    '''
    out, err = ssh_run(script)
    return {"status": "success" if not err else err, "note": name}

def delete_note(name):
    script = f'''
    tell application "Notes"
        delete note "{name}"
        return "Note deleted"
    end tell
    '''
    out, err = ssh_run(script)
    return {"status": "success" if not err else err, "note": name}

if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "list"
    
    if action == "list":
        acc = sys.argv[2] if len(sys.argv) > 2 else "iCloud"
        fol = sys.argv[3] if len(sys.argv) > 3 else None
        print(json.dumps(list_notes(acc, fol), indent=2))
    elif action == "get":
        print(json.dumps(get_note(sys.argv[2]), indent=2))
    elif action == "create":
        title = sys.argv[2]
        body = sys.argv[3] if len(sys.argv) > 3 else ""
        acc = sys.argv[4] if len(sys.argv) > 4 else "iCloud"
        print(json.dumps(create_note(title, body, acc), indent=2))
    elif action == "update":
        print(json.dumps(update_note(sys.argv[2], sys.argv[3]), indent=2))
    elif action == "delete":
        print(json.dumps(delete_note(sys.argv[2]), indent=2))
