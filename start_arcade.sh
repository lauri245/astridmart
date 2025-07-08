#!/bin/bash
# Arcade Game Launcher Startup Script

# Wait for display to be ready
sleep 5

# Set display (important for headless boot)
export DISPLAY=:0

# Change to game directory
cd /home/astrid/astridmart

# Start the arcade retail game in fullscreen mode
python3 main.py

# If game exits, restart after 3 seconds
sleep 3
exec "$0" 