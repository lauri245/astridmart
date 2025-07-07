#!/usr/bin/env python3
"""
Simple launcher script for the Arcade Retail Store Game
This script handles basic setup and runs the game
"""

import sys
import os
import subprocess

def check_pygame():
    """Check if pygame is installed"""
    try:
        import pygame
        return True
    except ImportError:
        return False

def install_pygame():
    """Try to install pygame"""
    print("Pygame not found. Attempting to install...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        print("Pygame installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install pygame automatically.")
        print("Please install pygame manually:")
        print("  pip install pygame")
        return False

def main():
    """Main launcher function"""
    print("🎮 ARCADE RETAIL STORE GAME LAUNCHER 🛒")
    print("=" * 50)
    
    # Check for command line arguments
    windowed = False
    if len(sys.argv) > 1:
        if '--windowed' in sys.argv or '-w' in sys.argv:
            windowed = True
            print("🖥️  Starting in WINDOWED mode (for testing)")
        elif '--help' in sys.argv or '-h' in sys.argv:
            print("Usage: python run_game.py [options]")
            print("Options:")
            print("  --windowed, -w    Run in windowed mode (for testing)")
            print("  --help, -h        Show this help message")
            print("")
            print("Default: Runs in fullscreen mode")
            print("In-game: F11 toggles fullscreen, ESC to quit")
            return
    
    if not windowed:
        print("🖥️  Starting in FULLSCREEN mode")
        print("   Press F11 in-game to toggle windowed mode")
        print("   Press ESC to quit")
    
    # Check if pygame is available
    if not check_pygame():
        if not install_pygame():
            input("Press Enter to exit...")
            return
    
    # Set environment variable for windowed mode
    if windowed:
        os.environ['ARCADE_WINDOWED'] = '1'
    
    # Import and run the game
    try:
        from main import ArcadeRetailGame
        print("🚀 Starting Arcade Retail Store Game...")
        print("=" * 50)
        game = ArcadeRetailGame()
        game.run()
    except Exception as e:
        print(f"❌ Error starting game: {e}")
        print("Make sure main.py is in the same directory")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main() 