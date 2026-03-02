#!/usr/bin/env python3
"""
Google OAuth Authentication Script for OpenClaw
Usage: python3 google-oauth.py
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
]

CREDS_PATH = os.path.expanduser('~/.openclaw/google-credentials.json')
TOKEN_PATH = os.path.expanduser('~/.openclaw/google-token.json')

def main():
    print("🔐 Google OAuth Authentication")
    print("=" * 50)
    
    # Load client secrets
    if not os.path.exists(CREDS_PATH):
        print(f"❌ Credentials file not found: {CREDS_PATH}")
        return
    
    with open(CREDS_PATH, 'r') as f:
        client_config = json.load(f)
    
    # Convert to installed app format
    installed_config = {
        "installed": {
            "client_id": client_config["web"]["client_id"],
            "client_secret": client_config["web"]["client_secret"],
            "redirect_uris": ["http://localhost:18889/oauth/callback"],
            "auth_uri": client_config["web"]["auth_uri"],
            "token_uri": client_config["web"]["token_uri"]
        }
    }
    
    # Create flow
    flow = InstalledAppFlow.from_client_config(
        installed_config,
        SCOPES,
        redirect_uri='http://localhost:18889/oauth/callback'
    )
    
    # Get authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent')
    
    print("\n🌐 COPY THE URL BELOW AND OPEN IT IN YOUR BROWSER:")
    print("=" * 50)
    print(auth_url)
    print("=" * 50)
    print("\n1. Sign in to your Google account")
    print("2. Grant permissions for Gmail, Calendar, and Drive")
    print("3. After redirect, copy the CODE from the URL")
    print("   (It will look like: http://localhost:18889/oauth/callback?code=XXXX&state=YYYY)")
    print("\nPaste the code below:\n")
    
    code = input("Authorization code: ").strip()
    
    # Exchange code for token
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Save token
    with open(TOKEN_PATH, 'w') as f:
        f.write(credentials.to_json())
    
    print(f"\n✅ Token saved to: {TOKEN_PATH}")
    print("\n📋 Enabled APIs:")
    for scope in SCOPES:
        print(f"   • {scope}")

if __name__ == '__main__':
    main()
