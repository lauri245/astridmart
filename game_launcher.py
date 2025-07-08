#!/usr/bin/env python3
"""
Arcade Game Launcher
A multi-game selection system for the arcade cabinet
"""

import pygame
import sys
import os
import subprocess
import json
import time
from pathlib import Path

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRIGHT_GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

class GameLauncher:
    def __init__(self):
        # Screen setup
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("Arcade Game Launcher")
        
        # Fonts
        self.font_huge = pygame.font.Font(None, int(self.height * 0.08))
        self.font_large = pygame.font.Font(None, int(self.height * 0.06))
        self.font_medium = pygame.font.Font(None, int(self.height * 0.04))
        self.font_small = pygame.font.Font(None, int(self.height * 0.03))
        
        # Game state
        self.selected_game = 0
        self.running = True
        self.clock = pygame.time.Clock()
        
        # Load games configuration
        self.games = self.load_games()
        
        # Joystick setup
        self.setup_joystick()
        
        print("🎮 Arcade Game Launcher started")
        print(f"📺 Screen resolution: {self.width}x{self.height}")
        print(f"🎯 Found {len(self.games)} games")
        
    def load_games(self):
        """Load available games from configuration file"""
        config_file = "games.json"
        games = []
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    
                # Load enabled games
                for game in config.get("games", []):
                    if game.get("enabled", True):
                        games.append(game)
                        
                # Add coming soon placeholder if enabled
                if config.get("settings", {}).get("show_coming_soon", True):
                    games.append({
                        "name": "Coming Soon",
                        "description": "More games will be added here",
                        "script": None,
                        "icon": "🎮",
                        "working_dir": None
                    })
                        
            else:
                # Fallback to hardcoded games if no config file
                games = [
                    {
                        "name": "Astrid Mart",
                        "description": "Shopping adventure with barcode scanner",
                        "script": "main.py",
                        "icon": "🛒",
                        "working_dir": "/home/astrid/astridmart"
                    },
                    {
                        "name": "Coming Soon",
                        "description": "More games will be added here",
                        "script": None,
                        "icon": "🎮",
                        "working_dir": None
                    }
                ]
                
        except Exception as e:
            print(f"⚠️  Error loading games config: {e}")
            # Fallback to basic configuration
            games = [{
                "name": "Astrid Mart",
                "description": "Shopping adventure with barcode scanner",
                "script": "main.py",
                "icon": "🛒",
                "working_dir": "/home/astrid/astridmart"
            }]
            
        return games
        
    def setup_joystick(self):
        """Setup joystick/arcade controller"""
        pygame.joystick.init()
        self.joystick = None
        self.joystick_button_mapping = {0: 'green', 1: 'blue', 2: 'yellow', 3: 'red'}
        
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"🕹️  Joystick detected: {self.joystick.get_name()}")
        else:
            print("🕹️  No joystick detected - using keyboard controls")
            
    def handle_button_press(self, button_color):
        """Handle arcade button press"""
        if button_color == 'green':  # K1 - Select/Launch game
            self.launch_selected_game()
        elif button_color == 'blue':  # K2 - Previous game
            self.selected_game = (self.selected_game - 1) % len(self.games)
        elif button_color == 'yellow':  # K3 - Next game
            self.selected_game = (self.selected_game + 1) % len(self.games)
        elif button_color == 'red':  # K4 - Shutdown system
            self.shutdown_system()
            
    def launch_selected_game(self):
        """Launch the currently selected game"""
        game = self.games[self.selected_game]
        
        if game["script"] is None:
            print(f"⚠️  Game '{game['name']}' is not available yet")
            return
            
        print(f"🚀 Launching game: {game['name']}")
        
        try:
            # Change to game directory and run the script
            old_cwd = os.getcwd()
            if game["working_dir"] and os.path.exists(game["working_dir"]):
                os.chdir(game["working_dir"])
                
            # Run the game and wait for it to complete
            result = subprocess.run([sys.executable, game["script"]], 
                                  capture_output=False, text=True)
            
            # Return to original directory
            os.chdir(old_cwd)
            
            print(f"🎮 Game '{game['name']}' exited with code: {result.returncode}")
            
        except Exception as e:
            print(f"❌ Error launching game '{game['name']}': {e}")
            
    def shutdown_system(self):
        """Safely shutdown the system"""
        print("🔌 Shutting down system...")
        try:
            subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Could not shutdown system")
            
    def scale(self, value):
        """Scale value for responsive design"""
        return int(value * self.height / 768)
        
    def draw_background(self):
        """Draw the launcher background"""
        # Gradient background
        for y in range(self.height):
            color_intensity = int(20 + (y / self.height) * 30)
            color = (color_intensity, color_intensity, color_intensity)
            pygame.draw.line(self.screen, color, (0, y), (self.width, y))
            
    def draw_title(self):
        """Draw the main title"""
        title = self.font_huge.render("🎮 ARCADE GAMES", True, BRIGHT_GREEN)
        title_rect = title.get_rect(center=(self.width//2, self.height * 0.15))
        
        # Title background
        bg_rect = pygame.Rect(title_rect.x - 20, title_rect.y - 10, 
                             title_rect.width + 40, title_rect.height + 20)
        pygame.draw.rect(self.screen, DARK_GRAY, bg_rect)
        pygame.draw.rect(self.screen, BRIGHT_GREEN, bg_rect, 3)
        
        self.screen.blit(title, title_rect)
        
    def draw_games(self):
        """Draw the list of available games"""
        start_y = self.height * 0.35
        game_height = self.height * 0.12
        
        for i, game in enumerate(self.games):
            y = start_y + (i * game_height)
            
            # Game selection box
            game_rect = pygame.Rect(self.width * 0.1, y, self.width * 0.8, game_height * 0.8)
            
            # Highlight selected game
            if i == self.selected_game:
                pygame.draw.rect(self.screen, BRIGHT_GREEN, game_rect)
                pygame.draw.rect(self.screen, WHITE, game_rect, 4)
                text_color = BLACK
            else:
                pygame.draw.rect(self.screen, DARK_GRAY, game_rect)
                pygame.draw.rect(self.screen, GRAY, game_rect, 2)
                text_color = WHITE
                
            # Game icon
            icon_text = self.font_large.render(game["icon"], True, text_color)
            icon_rect = icon_text.get_rect(center=(game_rect.x + 60, game_rect.centery))
            self.screen.blit(icon_text, icon_rect)
            
            # Game name
            name_text = self.font_large.render(game["name"], True, text_color)
            name_rect = name_text.get_rect(midleft=(game_rect.x + 120, game_rect.centery - 15))
            self.screen.blit(name_text, name_rect)
            
            # Game description
            desc_text = self.font_small.render(game["description"], True, text_color)
            desc_rect = desc_text.get_rect(midleft=(game_rect.x + 120, game_rect.centery + 15))
            self.screen.blit(desc_text, desc_rect)
            
            # Availability indicator
            if game["script"] is None:
                status_text = self.font_small.render("Coming Soon", True, YELLOW)
                status_rect = status_text.get_rect(midright=(game_rect.right - 20, game_rect.centery))
                self.screen.blit(status_text, status_rect)
                
    def draw_controls(self):
        """Draw control instructions"""
        controls_y = self.height * 0.85
        
        controls = [
            ("🟢 SELECT", "Launch Game"),
            ("🔵 PREV", "Previous Game"),
            ("🟡 NEXT", "Next Game"),
            ("🔴 POWER", "Shutdown System")
        ]
        
        control_width = self.width // len(controls)
        
        for i, (button, action) in enumerate(controls):
            x = i * control_width + control_width // 2
            
            # Button indicator
            button_text = self.font_small.render(button, True, WHITE)
            button_rect = button_text.get_rect(center=(x, controls_y))
            self.screen.blit(button_text, button_rect)
            
            # Action text
            action_text = self.font_small.render(action, True, GRAY)
            action_rect = action_text.get_rect(center=(x, controls_y + 25))
            self.screen.blit(action_text, action_rect)
            
    def draw(self):
        """Main drawing function"""
        self.draw_background()
        self.draw_title()
        self.draw_games()
        self.draw_controls()
        
        pygame.display.flip()
        
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                # Keyboard controls for development
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_x:  # Green button
                    self.handle_button_press('green')
                elif event.key == pygame.K_p:  # Blue button
                    self.handle_button_press('blue')
                elif event.key == pygame.K_c:  # Yellow button
                    self.handle_button_press('yellow')
                elif event.key == pygame.K_q:  # Red button
                    self.handle_button_press('red')
                elif event.key == pygame.K_UP:
                    self.handle_button_press('blue')
                elif event.key == pygame.K_DOWN:
                    self.handle_button_press('yellow')
                elif event.key == pygame.K_RETURN:
                    self.handle_button_press('green')
                    
            elif event.type == pygame.JOYBUTTONDOWN and self.joystick:
                # Joystick button press
                button_color = self.joystick_button_mapping.get(event.button)
                if button_color:
                    print(f"🕹️  Joystick button {event.button} pressed ({button_color})")
                    self.handle_button_press(button_color)
                    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

def main():
    """Main function"""
    try:
        launcher = GameLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\n🔄 Launcher interrupted by user")
        pygame.quit()
        sys.exit()
    except Exception as e:
        print(f"❌ Error in launcher: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main() 