#!/bin/bash

# Astrid Mart - Arcade Retail Game Installation Script
# For Raspberry Pi OS

echo "🛒 Installing Astrid Mart Arcade Game..."
echo "========================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install python3-pip python3-pygame git -y

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install -r requirements.txt

# Set permissions for the main script
chmod +x main.py

# Test the installation
echo "🧪 Testing installation..."
if python3 -c "import pygame, serial; print('Dependencies OK')"; then
    echo "✅ Installation successful!"
    echo ""
    echo "🎮 To run the game:"
    echo "   python3 main.py"
    echo ""
    echo "🔧 To run in windowed mode for testing:"
    echo "   python3 main.py --windowed --debug"
    echo ""
    echo "🚀 To set up autostart, run:"
    echo "   ./setup_autostart.sh"
else
    echo "❌ Installation failed. Please check dependencies."
    exit 1
fi 