#!/usr/bin/env bash
# sync-vault.sh — Sync ai-memory vault from Mac to local mirror
# Uses scp since rsync is not available in this environment
set -euo pipefail

SSH_KEY="$HOME/.ssh/id_ed25519"
SSH_HOST="tariq@100.82.80.22"
SSH_OPTS="-o IdentitiesOnly=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no"
REMOTE_PATH="/Users/tariq/Obsidian/ai-memory"
LOCAL_PATH="/data/ai-memory-vault"

mkdir -p "$LOCAL_PATH"

# Try SSH connection first
if ! ssh $SSH_OPTS -i "$SSH_KEY" "$SSH_HOST" "echo ok" >/dev/null 2>&1; then
  echo "Mac unreachable, skipping sync"
  exit 0
fi

# Create temp tar on remote, download, extract
REMOTE_TAR="/tmp/ai-memory-vault-sync-$$.tar.gz"
ssh $SSH_OPTS -i "$SSH_KEY" "$SSH_HOST" \
  "cd '$REMOTE_PATH' && tar czf '$REMOTE_TAR' --exclude='.git' --exclude='node_modules' ." 2>/dev/null

scp $SSH_OPTS -i "$SSH_KEY" "$SSH_HOST:$REMOTE_TAR" "$LOCAL_PATH/../vault-sync.tar.gz" 2>/dev/null

# Extract to mirror
tar xzf "$LOCAL_PATH/../vault-sync.tar.gz" -C "$LOCAL_PATH" 2>/dev/null
rm -f "$LOCAL_PATH/../vault-sync.tar.gz"

# Cleanup remote temp
ssh $SSH_OPTS -i "$SSH_KEY" "$SSH_HOST" "rm -f '$REMOTE_TAR'" 2>/dev/null || true

echo "Vault synced successfully"
echo "Files synced:"
find "$LOCAL_PATH" -name "*.md" -not -path "*/.git/*" | head -20