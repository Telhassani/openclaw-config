#!/usr/bin/env python3
"""
Google OAuth - extracts code from redirect URL manually
"""
import os, json, webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

creds = json.load(open(os.path.expanduser('~/.openclaw/google-credentials.json')))
conf = {
    'installed': {
        'client_id': creds['web']['client_id'],
        'client_secret': creds['web']['client_secret'],
        'redirect_uris': ['urn:ietf:wg:oauth:2.0:oob'],
        'auth_uri': creds['web']['auth_uri'],
        'token_uri': creds['web']['token_uri']
    }
}

flow = InstalledAppFlow.from_client_config(conf, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
url, _ = flow.authorization_url(prompt='consent')

print("="*50)
print("OPEN THIS URL IN YOUR BROWSER:")
print("="*50)
print(url)
print("="*50)
print("\nAfter granting access, you'll see a code on the screen.")
print("Copy that code and paste it below.\n")

code = input("Authorization code: ").strip()
flow.fetch_token(code=code)

open(os.path.expanduser('~/.openclaw/google-token.json'), 'w').write(flow.credentials.to_json())
print("\n✅ Done! Token saved to ~/.openclaw/google-token.json")
