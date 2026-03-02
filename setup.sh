#!/bin/bash

# OpenClaw Config Bootstrap Script
# Usage: ./setup.sh

echo "Setting up OpenClaw configuration..."

# Re-install skills from lock file (if exists)
if [ -f "skills-lock.json" ]; then
    echo "Installing skills..."
    npx skills install
fi

# Restart OpenClaw gateway
echo "Restarting OpenClaw gateway..."
openclaw gateway restart

echo "Done! OpenClaw config restored."
