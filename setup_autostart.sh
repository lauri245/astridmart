#!/bin/bash

# Astrid Mart - Autostart Setup Script
# Sets up the game to launch automatically on Raspberry Pi boot

echo "🚀 Setting up Astrid Mart autostart..."
echo "======================================"

# Get the current directory
GAME_DIR=$(pwd)
GAME_SCRIPT="$GAME_DIR/main.py"

# Check if main.py exists
if [ ! -f "$GAME_SCRIPT" ]; then
    echo "❌ Error: main.py not found in current directory"
    echo "Please run this script from the astridmart directory"
    exit 1
fi

# Create autostart directory if it doesn't exist
mkdir -p ~/.config/autostart

# Create the autostart desktop file
cat > ~/.config/autostart/astridmart.desktop << EOF
[Desktop Entry]
Name=Astrid Mart
Comment=Arcade Retail Game
Type=Application
Exec=/usr/bin/python3 $GAME_SCRIPT
Terminal=false
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

echo "✅ Autostart configured!"
echo ""
echo "The game will now launch automatically when the Pi boots."
echo ""
echo "To disable autostart:"
echo "  rm ~/.config/autostart/astridmart.desktop"
echo ""
echo "To test autostart without rebooting:"
echo "  python3 $GAME_SCRIPT"
echo ""
echo "🔄 Reboot your Pi to test autostart:"
echo "  sudo reboot" 