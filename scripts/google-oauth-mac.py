#!/usr/bin/env python3
# google-oauth.py - Run this on your Mac
# Install: pip3 install google-auth google-auth-oauthlib google-api-python-client

import os, json
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
        'redirect_uris': ['http://localhost:18889/oauth/callback'],
        'auth_uri': creds['web']['auth_uri'],
        'token_uri': creds['web']['token_uri']
    }
}

flow = InstalledAppFlow.from_client_config(conf, SCOPES, redirect_uri='http://localhost:18889/oauth/callback')
url, _ = flow.authorization_url(prompt='consent')
print('Go to this URL:')
print(url)
print('\nAfter logging in, copy the CODE from the redirect URL (after "code=") and paste below:')
code = input('Code: ').strip()
flow.fetch_token(code=code)
open(os.path.expanduser('~/.openclaw/google-token.json'), 'w').write(flow.credentials.to_json())
print('\n✅ Done! Token saved.')
