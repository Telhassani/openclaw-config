#!/bin/bash
# OpenClaw backup — daily snapshot of memory index + session transcripts
# Saves to /data/backups/, keeps 7 days, pushes to openclaw-config repo if available

set -euo pipefail

BKP_DIR="/data/backups"
BACKUP_REPO="/data"
KEEP=7
TIMESTAMP=$(date +%Y-%m-%d)
ARCHIVE="${BKP_DIR}/backup-${TIMESTAMP}.tar.gz"

mkdir -p "$BKP_DIR"

# Compress memory index + session transcripts
tar czf "$ARCHIVE" \
  -C /data/.openclaw memory/main.sqlite \
  -C /data/.openclaw agents/main/sessions/

echo "Created $(du -h "$ARCHIVE" | cut -f1) ${ARCHIVE}"

# Rotate — keep only N most recent
cd "$BKP_DIR"
ls -t backup-*.tar.gz 2>/dev/null | tail -n +$((KEEP + 1)) | while read -r old; do
  echo "Removing old: $old"
  rm -f "$old"
done

# Force-add to git (ignored path) if repo exists
if [ -d "${BACKUP_REPO}/.git" ] && [ -n "$(git -C "$BACKUP_REPO" diff --cached --shortstat 2>/dev/null || true)" ]; then
  # Already staged, push
  git -C "$BACKUP_REPO" push origin main 2>/dev/null || echo "[backup] push failed — will retry next run"
elif [ -d "${BACKUP_REPO}/.git" ]; then
  git -C "$BACKUP_REPO" add -f backups/  2>/dev/null || true
  if [ -n "$(git -C "$BACKUP_REPO" diff --cached --shortstat 2>/dev/null | tr -d '[:space:]')" ]; then
    git -C "$BACKUP_REPO" commit -m "backup: memory + sessions ${TIMESTAMP}"
    git -C "$BACKUP_REPO" push origin main 2>/dev/null || echo "[backup] push failed — will retry next run"
  fi
fi

echo "Backup done — $(ls -lh "$ARCHIVE" | awk '{print $5}') at $(echo $ARCHIVE | wc -c | awk '{print "rotated to", '"$KEEP"', days"}')"
