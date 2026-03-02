#!/usr/bin/env python3
"""
Simple background loop for memory maintenance
Runs decay and consolidation periodically
"""

import time
import sys
import os

# Add workspace to path
sys.path.insert(0, '/data/.openclaw/workspace')

from memory_manager import MemoryManager

INTERVAL_HOURS = 24  # Run once per day
USER_ID = "tariq"

def run_maintenance():
    """Run memory maintenance"""
    print(f"[{datetime.now().isoformat()}] Running memory maintenance...")
    
    memory = MemoryManager(user_id=USER_ID)
    
    # Apply decay
    memory.apply_decay()
    print("  ✓ Decay applied")
    
    # Consolidate
    memory.consolidate_to_longterm()
    print("  ✓ Consolidation complete")
    
    print(f"[{datetime.now().isoformat()}] Maintenance done")

def main():
    from datetime import datetime
    print(f"Memory maintenance loop started. Running every {INTERVAL_HOURS} hours.")
    
    while True:
        try:
            run_maintenance()
        except Exception as e:
            print(f"Error: {e}")
        
        # Sleep for the interval
        time.sleep(INTERVAL_HOURS * 3600)

if __name__ == "__main__":
    main()
