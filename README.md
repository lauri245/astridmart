# 🛒 Arcade Retail Store Game

A fun, kid-friendly arcade retail game designed for 4-year-olds! This game combines hardware (Raspberry Pi, arcade buttons, barcode scanner) and software to create an authentic shopping experience at home.

## ✨ Features

### 🛍️ Self-Checkout Mode
- **Visual Product Display**: Product images make shopping fun and engaging
- **Real Barcode Scanner Support**: Works with 1D barcode scanners
- **Kid-Friendly Interface**: No confusing SKU numbers shown to children
- **Shopping Cart**: Visual cart with product images, names, categories, and prices
- **Multi-Step Payment Process**: Realistic checkout experience
- **Receipt Generation**: Automatic receipt creation and saving
- **EUR Currency**: All prices displayed in Euros

### ⏰ Timer Mode
- **Fast-Paced Fun**: Find and scan products as quickly as possible
- **Score System**: Points for correct items, penalties for mistakes
- **Visual Feedback**: Large, clear displays of target items
- **Progressive Difficulty**: All items must be found to complete the game

### 🎮 Game Features
- **Fullscreen Support**: Optimized for TV/monitor display
- **Responsive Design**: Scales to any screen size
- **16-bit Arcade Aesthetics**: Colorful, retro-style graphics
- **Keyboard Testing**: Full keyboard controls for desktop development
- **Offline Operation**: No internet required

### 🔧 Product Management
- **Visual Product Database**: Support for product images
- **Price Management**: Easy price setting and bulk adjustments
- **CSV Import/Export**: Simple product management via spreadsheet
- **Image Management**: Built-in image status checking
- **Keyboard Shortcuts**: Assign number keys (0-9) to frequently used products

## 🎯 Game Modes

### 1. Self-Checkout Mode
Simulate a real grocery store experience:
- Scan products using a barcode scanner or number keys
- View products with images in your cart
- See running total in EUR
- Complete realistic payment process
- Get printed receipt

**Controls:**
- `0-9`: Scan products via keyboard shortcuts
- `P`: Start payment process
- `X`: Remove last item from cart
- `C`: Clear shopping cart
- `↑↓`: Scroll through cart items
- `ESC`: Return to main menu

### 2. Timer Mode
Fast-paced product finding game:
- Find target products as quickly as possible
- 60-second time limit
- Score points for correct items
- Track how many items you've found

**Controls:**
- `0-9`: Scan products via keyboard shortcuts
- `ESC`: Return to main menu

### 3. Product Manager
Manage your product database:
- Add, edit, and delete products
- Set prices in EUR
- Assign product images
- Import/export via CSV
- Manage keyboard shortcuts

## 🚀 Quick Start

### Prerequisites
- Python 3.6+
- Pygame library

### Installation
1. Clone or download the game files
2. Install dependencies:
   ```bash
   pip install pygame
   ```
3. Run the game:
   ```bash
   python3 main.py
   ```

### For Desktop Testing
Run in windowed mode:
```bash
python3 main.py --windowed
```

### Alternative Launcher
Use the launcher script that auto-installs dependencies:
```bash
python3 run_game.py
```

## 📁 File Structure

```
arcade-retail/
├── main.py              # Main game application
├── products.json        # Product database with SKUs and images
├── manage_products.py   # Command-line product manager
├── run_game.py         # Launcher script
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── images/            # Product images
    ├── bread.png
    ├── milk.png
    ├── apples.png
    └── ... (other product images)
```

## 🗂️ Product Database

Products are stored in `products.json` with the following structure:

```json
{
  "skus": {
    "4740489001247": {
      "name": "Fresh Eggs",
      "price": 3.20,
      "category": "Dairy",
      "description": "Fresh farm eggs (12 pack)",
      "image": "images/eggs.png"
    }
  },
  "keyboard_shortcuts": {
    "1": "4740489001247"
  }
}
```

**Default Products Included:**
- 🥚 Fresh Eggs (€3.20) - Barcode: 4740489001247 - Key 1
- 🍝 Italian Pasta (€2.50) - Barcode: 8076809521581 - Key 2  
- 🧵 Cooking String (€1.80) - Barcode: 8411922077827 - Key 3
- 🥜 Almond Butter (€5.90) - Barcode: 768563267062 - Key 4
- 💧 Mineral Water (€1.20) - Barcode: 4770405227093 - Key 5
- 🥤 Dr. Pepper (€2.40) - Barcode: 5902860417095 - Key 6
- 📖 Princess Magazine (€4.50) - Barcode: 9771736640006 - Key 7
- 📚 Pippi Longstocking (€12.90) - Barcode: 9789129721591 - Key 8

### Adding Your Own Products

#### Method 1: Product Manager Tool
```bash
python3 manage_products.py
```

#### Method 2: CSV Import/Export
1. Export current products: Choose option 8 in Product Manager
2. Edit `products.csv` in Excel or any spreadsheet application
3. Import updated products: Choose option 9 in Product Manager

#### Method 3: Direct JSON Editing
Edit `products.json` directly (not recommended for non-technical users)

## 🖼️ Product Images

### Image Requirements
- **Format**: PNG, JPG, or other pygame-supported formats
- **Size**: Any size (automatically scaled to 64x64 pixels)
- **Location**: Store in `images/` directory
- **Naming**: Use descriptive names (e.g., `bread.png`, `milk.png`)

### Adding Product Photos

**Where to Upload Photos:**

📁 Place all product photos in the `images/` directory with these exact filenames:

- `images/eggs.png` - Fresh Eggs (barcode: 4740489001247)
- `images/pasta.png` - Italian Pasta (barcode: 8076809521581)  
- `images/cooking_string.png` - Cooking String (barcode: 8411922077827)
- `images/almond_butter.png` - Almond Butter (barcode: 768563267062)
- `images/mineral_water.png` - Mineral Water (barcode: 4770405227093)
- `images/dr_pepper.png` - Dr. Pepper (barcode: 5902860417095)
- `images/princess_magazine.png` - Princess Magazine (barcode: 9771736640006)
- `images/pippi_book.png` - Pippi Longstocking Book (barcode: 9789129721591)

**Photo Requirements:**
- **Format**: PNG, JPG, or any image format
- **Size**: Any size (automatically scaled to 64x64 pixels in the cart)
- **Quality**: Clear, well-lit photos work best for kids
- **Background**: Any background is fine (will be scaled to fit)

**How to Add Photos:**
1. Take photos of your actual products
2. Save them with the exact filenames above  
3. Copy them to the `images/` directory
4. Restart the game to see your real product photos!

The game currently includes colorful placeholder images. Replace these with actual product photos for the most realistic shopping experience!

## 🎮 Hardware Setup

### Raspberry Pi Setup
1. Install Raspberry Pi OS
2. Install Python 3 and pygame
3. Copy game files to the Pi
4. Set up auto-start on boot (optional)

### Barcode Scanner
- **Scanner Type**: Use any USB HID barcode scanner (plug-and-play)
- **Setup**: No special drivers needed - scanner appears as keyboard input
- **Supported Barcodes**: 8-13 digit barcodes (EAN-8, EAN-13, UPC, etc.)
- **Speed Detection**: Game automatically detects fast scanner input vs. manual typing
- **Enter Key**: Many scanners send Enter after barcode - game handles this automatically

**Testing Your Scanner:**
```bash
python3 test_barcode.py
```

**Debug Mode:**
If your barcode scanner isn't working properly, enable debug mode to see what's happening:
```bash
python3 main.py --debug --windowed
```

This will show detailed information in the terminal about:
- Every key press received
- Barcode buffer contents
- Timing between keystrokes
- When barcodes are detected or rejected

**How It Works:**
1. Scanner sends barcode digits very quickly (< 100ms between keys)
2. Game detects this as scanner input and builds complete barcode
3. When Enter is pressed or barcode is complete, product is found automatically
4. Visual feedback shows scanning progress with 🔍 indicator

### Arcade Controls
- Connect arcade buttons to GPIO pins
- Map buttons to keyboard keys using Python GPIO libraries
- Recommended layout: 0-9 number keys for product shortcuts

## 🔧 Configuration

### Keyboard Shortcuts
Map number keys 0-9 to your most frequently used products:
- Use the Product Manager (option 5)
- Or edit the `keyboard_shortcuts` section in `products.json`

### Screen Settings
- **Fullscreen**: Press `F11` during gameplay
- **Windowed Mode**: Use `--windowed` flag for testing
- **Resolution**: Game automatically adapts to screen size

## 🎨 Customization

### Visual Themes
The game uses a 16-bit arcade aesthetic with:
- Bright, contrasting colors
- Decorative borders
- Large, readable fonts
- Kid-friendly interface elements

### Adding Sound Effects
While not included by default, you can add sound effects by:
1. Adding sound files to a `sounds/` directory
2. Loading sounds with `pygame.mixer.Sound()`
3. Playing sounds at appropriate game events

## 🐛 Troubleshooting

### Common Issues

**Game doesn't start:**
- Check that pygame is installed: `pip install pygame`
- Try running with Python 3: `python3 main.py`

**Images not showing:**
- Verify image files exist in `images/` directory
- Check file permissions
- Use the Product Manager to verify image paths

**Barcode scanner not working:**
- Ensure scanner is in HID keyboard mode
- Test scanner in a text editor first
- Run `python3 test_barcode.py` to test scanner output
- Enable debug mode: `python3 main.py --debug --windowed`
- Check that scanner sends alphanumeric codes (letters and numbers)
- Verify barcode matches one in your products.json file

**Performance issues:**
- Close other applications
- Try windowed mode for testing
- Ensure adequate RAM (especially on Raspberry Pi)

## 📝 Development

### For Developers
- **Language**: Python 3
- **Graphics**: Pygame
- **Architecture**: Single-file main game with modular components
- **Testing**: Full keyboard controls for desktop development

### Contributing
1. Fork the repository
2. Create a feature branch
3. Test thoroughly on both desktop and target hardware
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Support

For questions, issues, or suggestions:
1. Check the troubleshooting section above
2. Review the code comments for technical details
3. Test with the included sample products first

---

**Have fun shopping! 🛍️** 

*Perfect for kids who love playing store, learning about money, and having fun with technology!* 


## First products for testing


### Barcodes 
4740489001247 - eggs
8076809521581 - pasta
8411922077827 - cooking string
768563267062 - almond butter
4770405227093 - mineral water
5902860417095 - Dr. Pepper
9771736640006 - Princess magazine
9789129721591 - Pippi Longstocking book