#!/usr/bin/env python3
"""Apple Reminders via SSH + AppleScript"""
import subprocess
import json
import re

HOST = "100.82.80.22"
USER = "tariq"

def ssh_run(script):
    cmd = ["ssh", f"{USER}@{HOST}", "osascript", "-e", script]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()

def list_reminders(list_name="Reminders"):
    script = f'''
    tell application "Reminders"
        set remList to {{}}
        try
            repeat with r in (get reminders in list "{list_name}")
                set rName to name of r
                set rDue to due date of r
                set rComplete to completed of r
                set rId to id of r
                set end of remList to (rName & "|||" & (rDue as string) & "|||" & rComplete & "|||" & rId)
            end repeat
        end try
        return remList
    end tell
    '''
    out, err = ssh_run(script)
    if err:
        return {"error": err}
    
    reminders = []
    for line in out.split("\n"):
        if "|||" in line:
            parts = line.split("|||")
            reminders.append({
                "name": parts[0],
                "due": parts[1] if len(parts) > 1 else "",
                "completed": parts[2] == "true" if len(parts) > 2 else False,
                "id": parts[3] if len(parts) > 3 else ""
            })
    return {"list": list_name, "reminders": reminders}

def list_lists():
    script = '''
    tell application "Reminders"
        return name of lists
    end tell
    '''
    out, err = ssh_run(script)
    if err:
        return {"error": err}
    return {"lists": out.split("\n") if out else []}

def add_reminder(title, list_name="Reminders", due_date=None):
    if due_date:
        script = f'''
        tell application "Reminders"
            tell list "{list_name}"
                make new reminder with properties {{name:"{title}", due date:date "{due_date}"}}
            end tell
            return "Reminder added"
        end tell
        '''
    else:
        script = f'''
        tell application "Reminders"
            tell list "{list_name}"
                make new reminder with properties {{name:"{title}"}}
            end tell
            return "Reminder added"
        end tell
        '''
    out, err = ssh_run(script)
    return {"status": "success" if not err else err, "reminder": title, "list": list_name}

def complete_reminder(name):
    script = f'''
    tell application "Reminders"
        set r to reminder "{name}"
        set completed of r to true
        return "Completed"
    end tell
    '''
    out, err = ssh_run(script)
    return {"status": "success" if not err else err, "reminder": name}

def delete_reminder(name):
    script = f'''
    tell application "Reminders"
        delete reminder "{name}"
        return "Deleted"
    end tell
    '''
    out, err = ssh_run(script)
    return {"status": "success" if not err else err, "reminder": name}

if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "list"
    
    if action == "list":
        print(json.dumps(list_lists(), indent=2))
    elif action == "reminders":
        print(json.dumps(list_reminders(sys.argv[2] if len(sys.argv) > 2 else "Reminders"), indent=2))
    elif action == "add":
        due = sys.argv[3] if len(sys.argv) > 3 else None
        print(json.dumps(add_reminder(sys.argv[2], due_date=due), indent=2))
    elif action == "complete":
        print(json.dumps(complete_reminder(sys.argv[2]), indent=2))
    elif action == "delete":
        print(json.dumps(delete_reminder(sys.argv[2]), indent=2))
