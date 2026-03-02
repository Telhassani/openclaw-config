#!/bin/bash
# OpenClaw Memory System - Startup Script

# Start PostgreSQL
export PATH="/home/linuxbrew/.linuxbrew/opt/postgresql@16/bin:$PATH"
export LC_ALL="C.UTF-8"

# Check if PostgreSQL is running
if ! pg_isready -p 5432 >/dev/null 2>&1; then
    echo "Starting PostgreSQL..."
    pg_ctl -D /home/linuxbrew/.localbrew/var/postgresql@16 -l /home/linuxbrew/.localbrew/var/postgresql@16/logfile start
    sleep 3
fi

# Check if Redis is running
if ! redis-cli -p 6380 ping >/dev/null 2>&1; then
    echo "Starting Redis..."
    /home/linuxbrew/.linuxbrew/opt/redis/bin/redis-server --daemonize yes --port 6380
fi

echo "Memory system ready:"
echo "  PostgreSQL: $(pg_isready -p 5432 && echo 'OK' || echo 'FAIL')"
echo "  Redis: $(redis-cli -p 6380 ping 2>/dev/null && echo 'OK' || echo 'FAIL')"
