#!/bin/sh

echo "Setting up OpenClaw configuration..."

echo "Using local skills (no install needed)"

echo "Checking skills folder..."
ls -la skills 2>/dev/null || echo "No skills folder found"

echo "Setup complete."
