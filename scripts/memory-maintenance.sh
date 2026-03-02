#!/bin/bash
# Memory maintenance: decay + consolidation
# Run daily via cron

cd /data/.openclaw/workspace

# Decay old memories
python3 memory_manager.py decay --user default 2>/dev/null

# Consolidate sessions
python3 memory_manager.py consolidate --user default 2>/dev/null

echo "$(date): Memory maintenance complete"
