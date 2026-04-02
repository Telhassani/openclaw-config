#!/usr/bin/env python3
"""Apple Mail via SSH + AppleScript"""
import subprocess
import json
import re

HOST = "100.82.80.22"
USER = "tariq"

def ssh_run(script):
    cmd = ["ssh", f"{USER}@{HOST}", "osascript", "-e", script]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()

def list_emails(count=10):
    script = f'''
    tell application "Mail"
        set emailList to {{}}
        repeat with i from 1 to {count}
            try
                set msg to message i of inbox
                set msgSubject to subject of msg
                set msgSender to sender of msg
                set msgDate to date received of msg
                set end of emailList to (msgSubject & "|||" & msgSender & "|||" & (msgDate as string))
            end try
        end repeat
        return emailList
    end tell
    '''
    out, err = ssh_run(script)
    if err:
        return {"error": err}
    
    emails = []
    for line in out.split("\n"):
        if "|||" in line:
            parts = line.split("|||")
            emails.append({
                "index": len(emails) + 1,
                "subject": parts[0],
                "sender": parts[1],
                "date": parts[2] if len(parts) > 2 else ""
            })
    return {"emails": emails}

def get_email(index=1):
    script = f'''
    tell application "Mail"
        set msg to message {index} of inbox
        set msgSubject to subject of msg
        set msgSender to sender of msg
        set msgDate to date received of msg
        set msgContent to content of msg
        return msgSubject & "|||" & msgSender & "|||" & (msgDate as string) & "|||" & msgContent
    end tell
    '''
    out, err = ssh_run(script)
    if err:
        return {"error": err}
    
    parts = out.split("|||", 3)
    return {
        "subject": parts[0] if len(parts) > 0 else "",
        "sender": parts[1] if len(parts) > 1 else "",
        "date": parts[2] if len(parts) > 2 else "",
        "body": parts[3] if len(parts) > 3 else ""
    }

def search_emails(query):
    script = f'''
    tell application "Mail"
        set emailList to {{}}
        set msgCount to 0
        repeat with msg in (get messages of inbox)
            try
                set msgSubject to subject of msg
                if msgSubject contains "{query}" then
                    set msgSender to sender of msg
                    set msgDate to date received of msg
                    set end of emailList to (msgSubject & "|||" & msgSender & "|||" & (msgDate as string))
                    set msgCount to msgCount + 1
                    if msgCount > 10 then exit repeat
                end if
            end try
        end repeat
        return emailList
    end tell
    '''
    out, err = ssh_run(script)
    if err:
        return {"error": err}
    
    emails = []
    for line in out.split("\n"):
        if "|||" in line:
            parts = line.split("|||")
            emails.append({
                "subject": parts[0],
                "sender": parts[1],
                "date": parts[2] if len(parts) > 2 else ""
            })
    return {"emails": emails, "query": query}

def create_draft(to, subject, body):
    script = f'''
    tell application "Mail"
        set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{body}"}}
        tell newMessage
            make new to recipient at end of to recipients with properties {{address:"{to}"}}
        end tell
        return "Draft created"
    end tell
    '''
    out, err = ssh_run(script)
    return {"status": "success" if not err else err, "note": "Draft created - will NOT send automatically"}

if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "list"
    
    if action == "list":
        print(json.dumps(list_emails(int(sys.argv[2]) if len(sys.argv) > 2 else 10), indent=2))
    elif action == "get":
        print(json.dumps(get_email(int(sys.argv[2]) if len(sys.argv) > 2 else 1), indent=2))
    elif action == "search":
        print(json.dumps(search_emails(sys.argv[2] if len(sys.argv) > 2 else ""), indent=2))
    elif action == "draft":
        print(json.dumps(create_draft(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else ""), indent=2))
