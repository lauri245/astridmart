# 🎮 Arcade Retail Store Game Setup Guide

This guide explains how to set up the Arcade Retail Store Game for Raspberry Pi with automatic startup and safe shutdown capabilities.

## 🚀 System Overview

The arcade system consists of:
- **Main Game** (`main.py`) - Arcade retail simulation game
- **Products Database** (`products.json`) - Product catalog and configuration
- **Auto-start Service** - Boots directly to game
- **Safe Shutdown** - Red + Player 1 button combo for 3 seconds

## 📁 Directory Structure

```
/home/astrid/astridmart/
├── main.py                  # Main game application
├── products.json           # Product database
├── astridmart.service      # Systemd service file
├── start_arcade.sh         # Startup script
├── images/                 # Product images
└── sounds/                 # Sound effects
```

## 🔧 Installation Steps

### 1. Copy Files to Raspberry Pi
```bash
# Copy all files to your Pi
scp main.py products.json astridmart.service start_arcade.sh astrid@raspberrypi.local:~/astridmart/
scp -r images/ sounds/ astrid@raspberrypi.local:~/astridmart/
```

### 2. Set Permissions
```bash
# On your Pi
chmod +x ~/astridmart/start_arcade.sh
chmod +x ~/astridmart/main.py
```

### 3. Install Dependencies
```bash
# Install required packages
sudo apt update
sudo apt install python3-pygame python3-serial
```

### 4. Install Systemd Service
```bash
# Copy service file
sudo cp ~/astridmart/astridmart.service /etc/systemd/system/

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable astridmart.service
sudo systemctl start astridmart.service
```

### 5. Test the Game
```bash
# Test manually first
cd ~/astridmart
python3 main.py --windowed --debug
```

## 🎮 Controls

### Arcade Button Mapping:
- **🟢 Green (K1)** - Checkout / Confirm / Start
- **🔵 Blue (K2)** - Remove item / Previous / Secondary action
- **🟡 Yellow (K3)** - Clear cart / Next / Utility action
- **🔴 Red (K4)** - Exit / Cancel / Back to menu
- **⚫ Player 1** - Used for shutdown combo

### Safe Shutdown:
- **🔴 Red + ⚫ Player 1** - Hold both buttons for 3 seconds to safely shutdown the Pi

### Keyboard Controls (for development):
- **1-9, 0** - Quick product selection
- **G, B, Y, R** - Green, Blue, Yellow, Red button equivalents
- **ESC** - Exit/Back
- **F11** - Toggle fullscreen

## 🛒 Game Modes

### 1. Retail Mode (Self-Checkout)
- Scan products with barcode scanner or use keyboard shortcuts
- Items are added to cart with running total
- Use Green button to proceed to checkout
- Complete payment simulation

### 2. Learning Mode (Timed Challenge)
- Products are displayed one at a time
- Find and scan the correct product as quickly as possible
- Score based on correct answers and speed
- Randomized product order each time

### 3. Product Manager
- Export products to CSV for editing
- Import products from CSV
- Manage product database

## 🛠️ Service Management

### Control Commands
```bash
# Start game
sudo systemctl start astridmart.service

# Stop game  
sudo systemctl stop astridmart.service

# Restart game
sudo systemctl restart astridmart.service

# Check status
sudo systemctl status astridmart.service

# View logs
sudo journalctl -u astridmart.service -f

# Disable auto-start
sudo systemctl disable astridmart.service
```

## 🔧 Hardware Setup

### Required Hardware:
- Raspberry Pi (3B+ or 4 recommended)
- Arcade buttons (K1-K4) + Player 1 button
- USB arcade controller (DragonRise compatible)
- Barcode scanner (USB HID or Serial)
- Monitor/TV with HDMI input

### Button Wiring:
```
Button 0 (Green)  → K1 - Primary actions
Button 1 (Blue)   → K2 - Secondary actions  
Button 2 (Yellow) → K3 - Utility actions
Button 3 (Red)    → K4 - Exit/Cancel actions
Button 4 (Black)  → Player 1 - Shutdown combo
```

## 📦 Product Management

### Adding Products:
1. Edit `products.json` directly:
```json
{
  "skus": {
    "1234567890123": {
      "name": "Product Name",
      "price": 2.99,
      "category": "Category",
      "description": "Product description",
      "image": "images/product.png"
    }
  }
}
```

2. Or use the in-game Product Manager:
   - Export to CSV
   - Edit in spreadsheet
   - Import back to game

### Product Images:
- Place images in `images/` directory
- Recommended size: 200x200 pixels
- Supported formats: PNG, JPG, GIF
- Use descriptive filenames

## 🔧 Troubleshooting

### Game Won't Start
```bash
# Check service status
sudo systemctl status astridmart.service

# Check logs
sudo journalctl -u astridmart.service -n 50

# Test manually
cd ~/astridmart && python3 main.py --windowed --debug
```

### Controller Issues
```bash
# List input devices
ls /dev/input/

# Test joystick
jstest /dev/input/js0

# Check button mappings in debug mode
python3 main.py --debug --windowed
```

### Barcode Scanner Issues
```bash
# Check serial ports
ls /dev/cu.* /dev/tty*

# Test scanner in debug mode
python3 main.py --debug --windowed
```

### Display Issues
```bash
# Check display environment
echo $DISPLAY

# Set display manually
export DISPLAY=:0

# Test display
python3 main.py --windowed
```

## 🔒 Security & Safety

### Safe Shutdown:
- **NEVER** just pull the power plug
- Always use the Red + Player 1 combo (3 seconds)
- This ensures:
  - Product data is saved
  - System files are not corrupted
  - Clean shutdown process

### Sudo Configuration (for shutdown):
```bash
# Allow shutdown without password
sudo visudo
# Add line: astrid ALL=(ALL) NOPASSWD: /sbin/shutdown
```

## 📝 Configuration Options

### Command Line Options:
```bash
python3 main.py --help
python3 main.py --windowed      # Windowed mode (testing)
python3 main.py --debug         # Debug mode (barcode info)
```

### Environment Variables:
```bash
export ARCADE_DEBUG=1           # Enable debug mode
export DISPLAY=:0               # Set display
```

## 🎨 Customization

### Changing Colors:
Edit color constants in `main.py`:
```python
# Arcade color scheme
BRIGHT_GREEN = (0, 255, 0)
BRIGHT_BLUE = (0, 100, 255)
BRIGHT_YELLOW = (255, 255, 0)
BRIGHT_RED = (255, 0, 0)
```

### Adding Sounds:
1. Place sound files in `sounds/` directory
2. Load in `main.py`:
```python
scan_sound = pygame.mixer.Sound("sounds/scan.wav")
```

### Custom Storefront:
- Add `images/storefront.png` for custom banner
- Image will be scaled to full width
- Recommended size: 1024x400 pixels

## 🔄 Maintenance

### Regular Tasks:
- Check system logs: `sudo journalctl -u astridmart.service`
- Update product database as needed
- Backup configuration files
- Clean product images directory

### Updates:
```bash
# Backup current setup
cp -r ~/astridmart ~/astridmart.backup

# Update files
# ... copy new files ...

# Restart service
sudo systemctl restart astridmart.service
```

## 🆘 Support

If you encounter issues:
1. Check the logs: `sudo journalctl -u astridmart.service -f`
2. Test in debug mode: `python3 main.py --debug --windowed`
3. Verify hardware connections
4. Check file permissions and paths
5. Ensure all dependencies are installed

### Common Issues:
- **No display**: Check DISPLAY environment variable
- **Controller not working**: Verify joystick device and button mapping
- **Scanner not working**: Check serial port permissions and connections
- **Game crashes**: Check logs for Python errors

---

**🎮 Happy Gaming! Your arcade cabinet is ready for retail fun! 🛒** 