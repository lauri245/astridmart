import pygame
import json
import random
import time
import os
import csv
import threading
import queue
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("pyserial not available - serial barcode scanners won't work")

# Initialize Pygame
pygame.init()

# Get display info for fullscreen
display_info = pygame.display.Info()
SCREEN_WIDTH = display_info.current_w
SCREEN_HEIGHT = display_info.current_h
FPS = 60

# For desktop testing, use a smaller windowed mode
WINDOWED_WIDTH = 1024
WINDOWED_HEIGHT = 768

# Colors (16-bit arcade style)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
DARK_BLUE = (0, 0, 139)
BRIGHT_GREEN = (50, 205, 50)
HOT_PINK = (255, 20, 147)
LIGHT_GRAY = (200, 200, 200)

# Game states
MENU = 0
RETAIL_MODE = 1
TIMER_MODE = 2
GAME_OVER = 3
PRODUCT_MANAGER = 4
PAYMENT_MODE = 5

class ArcadeRetailGame:
    def __init__(self):
        # Check if running in desktop mode (for testing)
        self.desktop_mode = '--windowed' in os.sys.argv or os.environ.get('ARCADE_WINDOWED', '0') == '1'
        
        if self.desktop_mode:
            self.screen = pygame.display.set_mode((WINDOWED_WIDTH, WINDOWED_HEIGHT))
            self.width = WINDOWED_WIDTH
            self.height = WINDOWED_HEIGHT
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
            self.width = SCREEN_WIDTH
            self.height = SCREEN_HEIGHT
            
        pygame.display.set_caption("ASTRID MART - Kids' Shopping Adventure")
        self.clock = pygame.time.Clock()
        
        # Relative font sizes based on screen height
        self.font_huge = pygame.font.Font(None, int(self.height * 0.12))     # 12% of screen height
        self.font_large = pygame.font.Font(None, int(self.height * 0.08))    # 8% of screen height
        self.font_medium = pygame.font.Font(None, int(self.height * 0.05))   # 5% of screen height
        self.font_small = pygame.font.Font(None, int(self.height * 0.035))   # 3.5% of screen height
        
        # Game state
        self.state = MENU
        self.running = True
        
        # Load products and SKUs
        self.products_data = self.load_products()
        self.skus = self.products_data.get('skus', {})
        self.keyboard_shortcuts = self.products_data.get('keyboard_shortcuts', {})
        
        # Load product images
        self.product_images = {}
        self.load_product_images()
        
        # Load storefront banner
        self.storefront_banner = None
        self.load_storefront_banner()
        
        # Barcode scanning
        self.barcode_buffer = ""
        self.barcode_input_time = 0
        self.barcode_timeout = 1000  # 1 second to complete barcode input (scanners are fast)
        self.last_key_time = 0
        self.scanner_speed_threshold = 100  # milliseconds between keystrokes for scanner detection
        
        # Retail mode variables
        self.cart = {}  # Changed to dict to group identical items
        self.total_price = 0.0
        self.scanned_item = ""
        self.receipt = []
        self.cart_scroll_offset = 0  # For scrolling through cart items
        
        # Payment variables
        self.payment_amount = 0.0
        self.payment_step = 0  # 0: amount, 1: paying, 2: change, 3: complete
        self.payment_start_time = 0
        
        # Timer mode variables (now learning mode)
        self.timer_score = 0
        self.timer_correct = 0
        self.timer_start_time = 0
        self.timer_duration = 60  # 60 seconds (not used in learning mode)
        self.current_target = None
        self.timer_items_found = []
        self.learning_current_index = 0  # Track progress through products
        
        # Input handling
        self.last_scan_time = 0
        self.scan_cooldown = 1000  # 1 second cooldown
        
        # Debug mode
        self.debug_mode = '--debug' in os.sys.argv or os.environ.get('ARCADE_DEBUG', '0') == '1'
        if self.debug_mode:
            print("DEBUG MODE ENABLED - Barcode scanner debugging information will be displayed")
            print("To disable debug mode, remove --debug from command line or set ARCADE_DEBUG=0")
        
        # Serial barcode scanner support
        self.serial_scanner = None
        self.serial_queue = queue.Queue()
        self.serial_thread = None
        self.serial_running = False
        self.setup_serial_scanner()
        
        # Joystick support for arcade controllers
        pygame.joystick.init()
        self.joystick = None
        self.joystick_button_mapping = {
            # Default mapping for common arcade controllers
            # These can be adjusted based on your specific controller
            0: 'green',  # K1 - GREEN button (Start/Go actions)
            1: 'blue',   # K2 - BLUE button (Primary/Educational actions)
            2: 'yellow', # K3 - YELLOW button (Management/Utility actions)
            3: 'red',    # K4 - RED button (Stop/Exit actions)
            4: 'player1' # Player 1 button (for shutdown combo)
        }
        self.setup_joystick()
        
        # Shutdown combo tracking
        self.shutdown_combo_start_time = None
        self.shutdown_combo_active = False
        self.SHUTDOWN_COMBO_DURATION = 3.0  # 3 seconds
        
    def scale(self, value):
        """Scale a value relative to screen height for responsive design"""
        return int(value * self.height / 768)  # 768 is our base height
    
    def scale_width(self, value):
        """Scale a value relative to screen width for responsive design"""
        return int(value * self.width / 1024)  # 1024 is our base width
        
    def load_products(self):
        """Load products from JSON file"""
        try:
            with open('products.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default products if file doesn't exist
            default_data = {
                "skus": {
                    "7501234567890": {"name": "White Bread", "price": 2.20, "category": "Bakery", "description": "Fresh white bread loaf", "image": "images/bread.png"},
                    "7501234567891": {"name": "Whole Milk", "price": 2.80, "category": "Dairy", "description": "1 liter whole milk", "image": "images/milk.png"},
                    "7501234567892": {"name": "Red Apples", "price": 1.50, "category": "Produce", "description": "Fresh red apples per kg", "image": "images/apples.png"},
                    "7501234567893": {"name": "Spaghetti Pasta", "price": 1.30, "category": "Pantry", "description": "500g spaghetti pasta", "image": "images/pasta.png"},
                    "7501234567894": {"name": "Cheddar Cheese", "price": 3.90, "category": "Dairy", "description": "Sharp cheddar cheese block", "image": "images/cheese.png"},
                    "7501234567895": {"name": "Bananas", "price": 0.80, "category": "Produce", "description": "Fresh bananas per kg", "image": "images/bananas.png"},
                    "7501234567896": {"name": "Corn Flakes", "price": 4.50, "category": "Breakfast", "description": "Large box corn flakes cereal", "image": "images/cereal.png"},
                    "7501234567897": {"name": "Greek Yogurt", "price": 2.60, "category": "Dairy", "description": "Plain Greek yogurt 500g", "image": "images/yogurt.png"},
                    "7501234567898": {"name": "Wheat Crackers", "price": 2.90, "category": "Snacks", "description": "Whole wheat crackers", "image": "images/crackers.png"},
                    "7501234567899": {"name": "Orange Juice", "price": 2.40, "category": "Beverages", "description": "Fresh orange juice 1L", "image": "images/juice.png"}
                },
                "keyboard_shortcuts": {
                    "1": "7501234567890", "2": "7501234567891", "3": "7501234567892", "4": "7501234567893", "5": "7501234567894",
                    "6": "7501234567895", "7": "7501234567896", "8": "7501234567897", "9": "7501234567898", "0": "7501234567899"
                }
            }
            self.save_products(default_data)
            return default_data
    
    def load_product_images(self):
        """Load all product images at original resolution to preserve quality"""
        print("Loading product images...")
        for sku, product in self.skus.items():
            image_path = product.get('image', '')
            if image_path and os.path.exists(image_path):
                try:
                    # Load image at original resolution - don't scale here!
                    image = pygame.image.load(image_path)
                    self.product_images[sku] = image
                    print(f"Loaded image for {product['name']}")
                except pygame.error as e:
                    print(f"Could not load image for {product['name']}: {e}")
                    self.product_images[sku] = self.create_placeholder_image(product['name'])
            else:
                print(f"Image not found for {product['name']}, using placeholder")
                self.product_images[sku] = self.create_placeholder_image(product['name'])
    
    def create_placeholder_image(self, product_name):
        """Create a simple placeholder image at higher resolution"""
        surface = pygame.Surface((200, 200))
        surface.fill(LIGHT_GRAY)
        pygame.draw.rect(surface, BLACK, (0, 0, 200, 200), 3)
        
        # Add first letter of product name - bigger font
        font = pygame.font.Font(None, 150)
        letter = product_name[0] if product_name else "?"
        text = font.render(letter, True, BLACK)
        text_rect = text.get_rect(center=(100, 100))
        surface.blit(text, text_rect)
        
        return surface
    
    def load_storefront_banner(self):
        """Load the storefront banner image"""
        banner_path = "images/storefront.png"
        if os.path.exists(banner_path):
            try:
                # Load the banner and scale it to full width
                banner = pygame.image.load(banner_path)
                # Scale to full width while maintaining aspect ratio
                banner_width = self.width
                banner_height = int(banner.get_height() * (banner_width / banner.get_width()))
                self.storefront_banner = pygame.transform.scale(banner, (banner_width, banner_height))
                print(f"Loaded storefront banner: {banner_width}x{banner_height}")
            except pygame.error as e:
                print(f"Could not load storefront banner: {e}")
                self.storefront_banner = None
        else:
            print("Storefront banner not found")
            self.storefront_banner = None
    
    def save_products(self, products_data):
        """Save products to JSON file"""
        with open('products.json', 'w') as f:
            json.dump(products_data, f, indent=2)
    
    def export_products_csv(self):
        """Export products to CSV for easy editing"""
        try:
            with open('products.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['SKU', 'Name', 'Price', 'Category', 'Description', 'Image'])
                for sku, product in self.skus.items():
                    writer.writerow([sku, product['name'], product['price'], product['category'], product.get('description', ''), product.get('image', '')])
            return True
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return False
    
    def import_products_csv(self):
        """Import products from CSV"""
        try:
            with open('products.csv', 'r') as f:
                reader = csv.DictReader(f)
                new_skus = {}
                for row in reader:
                    new_skus[row['SKU']] = {
                        'name': row['Name'],
                        'price': float(row['Price']),
                        'category': row['Category'],
                        'description': row.get('Description', ''),
                        'image': row.get('Image', '')
                    }
                self.skus = new_skus
                self.products_data['skus'] = new_skus
                self.save_products(self.products_data)
                self.load_product_images()  # Reload images
            return True
        except Exception as e:
            print(f"Error importing CSV: {e}")
            return False
    
    def setup_serial_scanner(self):
        """Setup serial barcode scanner if available"""
        if not SERIAL_AVAILABLE:
            return
        
        try:
            # List all available serial ports
            ports = serial.tools.list_ports.comports()
            scanner_port = None
            
            # Look for common barcode scanner patterns
            for port in ports:
                port_name = port.device.lower()
                if self.debug_mode:
                    print(f"DEBUG: Found serial port: {port.device} - {port.description}")
                
                # Check for USB modem patterns (like your scanner)
                if 'usbmodem' in port_name or 'usb' in port.description.lower():
                    scanner_port = port.device
                    if self.debug_mode:
                        print(f"DEBUG: Potential scanner port: {scanner_port}")
                    break
            
            if scanner_port:
                # Try to open the scanner
                self.serial_scanner = serial.Serial(
                    port=scanner_port,
                    baudrate=115200,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=0.1
                )
                print(f"🔍 Serial barcode scanner connected: {scanner_port}")
                
                # Start reading thread
                self.serial_running = True
                self.serial_thread = threading.Thread(target=self.read_serial_scanner, daemon=True)
                self.serial_thread.start()
            else:
                if self.debug_mode:
                    print("DEBUG: No serial barcode scanner found")
                    
        except Exception as e:
            if self.debug_mode:
                print(f"DEBUG: Serial scanner setup failed: {e}")
    
    def read_serial_scanner(self):
        """Read data from serial barcode scanner"""
        if not self.serial_scanner:
            return
        
        barcode_buffer = ""
        
        while self.serial_running:
            try:
                if self.serial_scanner.in_waiting > 0:
                    # Read available data
                    data = self.serial_scanner.read(self.serial_scanner.in_waiting)
                    text = data.decode('utf-8', errors='ignore').strip()
                    
                    if text:
                        if self.debug_mode:
                            print(f"DEBUG: Serial scanner received: '{text}'")
                        
                        # Check if this looks like a complete barcode
                        if len(text) >= 8 and text.isalnum():
                            # Put complete barcode in queue
                            self.serial_queue.put(text)
                            if self.debug_mode:
                                print(f"DEBUG: Serial scanner queued barcode: '{text}'")
                        else:
                            # Handle partial data
                            barcode_buffer += text
                            if len(barcode_buffer) >= 8 and barcode_buffer.isalnum():
                                self.serial_queue.put(barcode_buffer)
                                if self.debug_mode:
                                    print(f"DEBUG: Serial scanner queued buffered barcode: '{barcode_buffer}'")
                                barcode_buffer = ""
                
                time.sleep(0.01)  # Small delay to prevent busy waiting
                
            except Exception as e:
                if self.debug_mode:
                    print(f"DEBUG: Serial scanner read error: {e}")
                time.sleep(0.1)
    
    def check_serial_scanner(self):
        """Check for serial scanner input"""
        try:
            while not self.serial_queue.empty():
                barcode = self.serial_queue.get_nowait()
                if self.debug_mode:
                    print(f"DEBUG: Processing serial barcode: '{barcode}'")
                
                # Process the barcode based on current state
                if self.state == RETAIL_MODE:
                    self.scan_item(barcode)
                elif self.state == TIMER_MODE:
                    self.scan_timer_item(barcode)
                    
        except queue.Empty:
            pass
        except Exception as e:
            if self.debug_mode:
                print(f"DEBUG: Serial scanner check error: {e}")
    
    def setup_joystick(self):
        """Setup joystick/arcade controller if available"""
        joystick_count = pygame.joystick.get_count()
        
        if joystick_count > 0:
            # Use the first joystick
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            
            if self.debug_mode:
                print(f"DEBUG: Joystick connected: {self.joystick.get_name()}")
                print(f"DEBUG: Joystick buttons: {self.joystick.get_numbuttons()}")
                print(f"DEBUG: Button mapping: {self.joystick_button_mapping}")
            
            print(f"🕹️  Arcade controller connected: {self.joystick.get_name()}")
        else:
            if self.debug_mode:
                print("DEBUG: No joystick/arcade controller detected")
    
    def process_barcode_input(self, key_char):
        """Process barcode character input from scanner or keyboard"""
        current_time = pygame.time.get_ticks()
        
        # Reset buffer if timeout exceeded
        if current_time - self.barcode_input_time > self.barcode_timeout:
            if self.debug_mode and self.barcode_buffer:
                print(f"DEBUG: Barcode buffer timeout, clearing: '{self.barcode_buffer}'")
            self.barcode_buffer = ""
        
        # Detect if this is scanner input (very fast keystrokes)
        time_since_last_key = current_time - self.last_key_time
        is_scanner_speed = time_since_last_key < self.scanner_speed_threshold
        
        if self.debug_mode:
            print(f"DEBUG: Time since last key: {time_since_last_key}ms, is_scanner_speed: {is_scanner_speed}")
        
        # Add character to buffer (accept alphanumeric characters)
        if key_char.isalnum():
            # If this is the first character or we're getting scanner-speed input
            if not self.barcode_buffer or is_scanner_speed:
                self.barcode_buffer += key_char
                self.barcode_input_time = current_time
                self.last_key_time = current_time
                
                # Show scanning feedback
                if len(self.barcode_buffer) > 0:
                    self.scanned_item = f"🔍 Scanning: {self.barcode_buffer}"
                
                if self.debug_mode:
                    print(f"DEBUG: Added to buffer: '{key_char}', buffer now: '{self.barcode_buffer}'")
                
                # Check if we have a complete barcode (8-13 characters for various barcode types)
                if len(self.barcode_buffer) >= 8:  # Accept shorter barcodes too
                    # For our specific products, check if this matches any SKU
                    if self.barcode_buffer in self.skus:
                        barcode = self.barcode_buffer
                        self.barcode_buffer = ""
                        if self.debug_mode:
                            print(f"DEBUG: Found matching SKU: '{barcode}'")
                        return barcode
                    # Standard 13-character barcode
                    elif len(self.barcode_buffer) >= 13:
                        barcode = self.barcode_buffer
                        self.barcode_buffer = ""
                        if self.debug_mode:
                            print(f"DEBUG: Complete 13-char barcode: '{barcode}'")
                        return barcode
            else:
                # Manual keyboard input - reset buffer for single key presses
                if self.debug_mode:
                    print(f"DEBUG: Manual input detected, resetting buffer to: '{key_char}'")
                self.barcode_buffer = key_char
                self.barcode_input_time = current_time
                self.last_key_time = current_time
        
        return None
    
    def process_barcode_complete(self, complete_barcode):
        """Process a complete barcode string (from Enter key or other completion signal)"""
        if complete_barcode and len(complete_barcode) >= 8:
            # Clean the barcode (keep only alphanumeric characters)
            clean_barcode = ''.join(filter(str.isalnum, complete_barcode))
            if clean_barcode in self.skus:
                self.barcode_buffer = ""
                return clean_barcode
        return None
    
    def lookup_product(self, barcode_or_key):
        """Look up product by barcode or keyboard shortcut"""
        # First check if it's a keyboard shortcut
        if barcode_or_key in self.keyboard_shortcuts:
            sku = self.keyboard_shortcuts[barcode_or_key]
            return self.skus.get(sku)
        
        # Then check if it's a direct SKU lookup
        return self.skus.get(barcode_or_key)
    
    def add_to_cart(self, product, sku):
        """Add product to cart and update receipt"""
        if sku in self.cart:
            # Item already in cart, increase quantity
            self.cart[sku]['quantity'] += 1
            self.cart[sku]['total_price'] += product['price']
        else:
            # New item, add to cart
            self.cart[sku] = {
                'sku': sku,
                'name': product['name'],
                'price': product['price'],
                'quantity': 1,
                'total_price': product['price'],
                'category': product['category'],
                'description': product.get('description', ''),
                'image_path': product.get('image', ''),
                'first_added': time.time()
            }
        
        self.total_price += product['price']
        
        # Update receipt
        self.receipt.append({
            'item': product['name'],
            'price': product['price'],
            'timestamp': time.strftime('%H:%M:%S')
        })
        
        quantity = self.cart[sku]['quantity']
        return f"Added: {product['name']} (€{product['price']:.2f}) [Qty: {quantity}]"
    
    def generate_receipt(self):
        """Generate a formatted receipt"""
        if not self.cart:
            return []
        
        receipt_lines = []
        receipt_lines.append("=" * 40)
        receipt_lines.append("     ARCADE RETAIL STORE")
        receipt_lines.append("=" * 40)
        receipt_lines.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        receipt_lines.append("-" * 40)
        
        for sku, item in self.cart.items():
            if item['quantity'] > 1:
                receipt_lines.append(f"{item['name']} x{item['quantity']:<16} €{item['total_price']:.2f}")
                receipt_lines.append(f"  (€{item['price']:.2f} each)")
            else:
                receipt_lines.append(f"{item['name']:<25} €{item['price']:.2f}")
        
        receipt_lines.append("-" * 40)
        total_items = sum(item['quantity'] for item in self.cart.values())
        receipt_lines.append(f"Total Items: {total_items}")
        receipt_lines.append(f"{'TOTAL:':<25} €{self.total_price:.2f}")
        receipt_lines.append("=" * 40)
        receipt_lines.append("    Thank you for shopping!")
        receipt_lines.append("=" * 40)
        
        return receipt_lines
    
    def draw_border_box(self, rect, color, thickness=3):
        """Draw a decorative border box"""
        pygame.draw.rect(self.screen, color, rect, thickness)
        # Add corner decorations
        corner_size = thickness * 2
        pygame.draw.rect(self.screen, color, (rect.x, rect.y, corner_size, corner_size))
        pygame.draw.rect(self.screen, color, (rect.x + rect.width - corner_size, rect.y, corner_size, corner_size))
        pygame.draw.rect(self.screen, color, (rect.x, rect.y + rect.height - corner_size, corner_size, corner_size))
        pygame.draw.rect(self.screen, color, (rect.x + rect.width - corner_size, rect.y + rect.height - corner_size, corner_size, corner_size))
    
    def draw_cart_item(self, item, item_bg, cart_area, is_compact=False):
        """Draw a single cart item - supports both regular and compact layouts"""
        # Adjust sizes based on layout type - responsive sizing
        if is_compact:
            image_size = self.scale(75)  # Responsive image size for compact layout
            font_name = self.font_small
            font_price = self.font_small
            font_qty = self.font_large
        else:
            image_size = self.scale(90)  # Responsive image size for single column
            font_name = self.font_medium
            font_price = self.font_medium
            font_qty = self.font_huge
        
        # Product image - prominent and clean - responsive padding
        padding = self.scale(8)
        image_rect = pygame.Rect(item_bg.x + padding, item_bg.y + padding, image_size, image_size)
        if item['sku'] in self.product_images:
            # White background with subtle border for prominence
            pygame.draw.rect(self.screen, WHITE, image_rect)
            pygame.draw.rect(self.screen, (200, 200, 200), image_rect, 2)
            
            # Scale original image to cart size - responsive border
            border = self.scale(4)
            image = self.product_images[item['sku']]
            image_scaled = pygame.transform.scale(image, (image_size - border, image_size - border))
            image_center = (image_rect.centerx - (image_size - border)//2, image_rect.centery - (image_size - border)//2)
            self.screen.blit(image_scaled, image_center)
        
        # Product details - simple text - responsive spacing
        text_x = image_rect.right + self.scale(15)
        
        # Product name - truncate if too long for compact layout
        name = item['name']
        if is_compact and len(name) > 15:
            name = name[:12] + "..."
        
        name_text = font_name.render(name, True, WHITE)
        self.screen.blit(name_text, (text_x, item_bg.y + padding))
        
        # Price - responsive spacing
        price_text = font_price.render(f"€{item['price']:.2f}", True, YELLOW)
        price_y = item_bg.y + padding + (self.scale(30) if not is_compact else self.scale(22))
        self.screen.blit(price_text, (text_x, price_y))
        
        # Quantity - HUGE for kids, clean design - responsive sizing
        if item['quantity'] > 1:
            qty_text = font_qty.render(f"x{item['quantity']}", True, BLACK)
            qty_rect = qty_text.get_rect()
            qty_rect.topright = (item_bg.right - self.scale(10), item_bg.y + padding)
            
            # Simple quantity background - responsive padding
            qty_bg = pygame.Rect(qty_rect.x - self.scale(8), qty_rect.y - self.scale(4), 
                                qty_rect.width + self.scale(16), qty_rect.height + self.scale(8))
            pygame.draw.rect(self.screen, HOT_PINK, qty_bg)
            self.screen.blit(qty_text, qty_rect)
    
    def handle_events(self):
        """Handle keyboard and other events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                # ESC or F11 to toggle fullscreen/quit
                if event.key == pygame.K_ESCAPE:
                    if self.state == MENU:
                        self.running = False
                    elif self.state == PAYMENT_MODE:
                        self.state = RETAIL_MODE  # Cancel payment
                    else:
                        self.state = MENU
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                
                elif self.state == MENU:
                    # Keyboard controls for testing (hidden from UI)
                    if event.key == pygame.K_1:
                        self.start_retail_mode()
                    elif event.key == pygame.K_2:
                        self.start_timer_mode()
                    elif event.key == pygame.K_3:
                        self.state = PRODUCT_MANAGER
                    elif event.key == pygame.K_q:
                        self.running = False
                    # Arcade colored buttons for actual game
                    elif event.key == pygame.K_x:  # GREEN button (K1) - Self-checkout
                        self.start_retail_mode()
                    elif event.key == pygame.K_p:  # BLUE button (K2) - Learning mode
                        self.start_timer_mode()
                    elif event.key == pygame.K_c:  # YELLOW button (K3) - Product manager
                        self.state = PRODUCT_MANAGER
                    elif event.key == pygame.K_ESCAPE:  # RED button (K4) - Quit game
                        self.running = False
                
                elif self.state == RETAIL_MODE:
                    if event.key == pygame.K_x:  # GREEN button (K1) - Checkout
                        self.start_payment()
                    elif event.key == pygame.K_p:  # BLUE button (K2) - Remove last item
                        self.remove_last_item()
                    elif event.key == pygame.K_c:  # YELLOW button (K3) - Clear cart
                        self.clear_cart()
                    elif event.key == pygame.K_r:  # Print receipt (keyboard only)
                        self.print_receipt()
                    elif event.key == pygame.K_UP:  # Scroll up in cart
                        if self.cart_scroll_offset > 0:
                            self.cart_scroll_offset -= 1
                    elif event.key == pygame.K_DOWN:  # Scroll down in cart
                        # Dynamic scrolling based on cart size
                        total_items = len(self.cart)
                        max_displayable = 4 if total_items <= 4 else 8
                        if total_items > max_displayable:
                            max_scroll = total_items - max_displayable
                            if self.cart_scroll_offset < max_scroll:
                                self.cart_scroll_offset += 1
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:  # Enter key (barcode completion)
                        if self.barcode_buffer:
                            if self.debug_mode:
                                print(f"DEBUG: Enter pressed, processing barcode: '{self.barcode_buffer}'")
                            complete_barcode = self.process_barcode_complete(self.barcode_buffer)
                            if complete_barcode:
                                if self.debug_mode:
                                    print(f"DEBUG: Barcode accepted: '{complete_barcode}'")
                                self.scan_item(complete_barcode)
                            else:
                                if self.debug_mode:
                                    print(f"DEBUG: Barcode rejected: '{self.barcode_buffer}'")
                                self.scanned_item = f"Unknown barcode: {self.barcode_buffer}"
                            self.barcode_buffer = ""
                    # Handle ALL alphanumeric input (not just digits) for barcode scanning
                    else:
                        # Convert pygame key to character
                        key_char = None
                        if event.key >= pygame.K_0 and event.key <= pygame.K_9:
                            key_char = str(event.key - pygame.K_0)
                        elif event.key >= pygame.K_a and event.key <= pygame.K_z:
                            key_char = chr(event.key)
                        elif event.key >= pygame.K_KP0 and event.key <= pygame.K_KP9:
                            key_char = str(event.key - pygame.K_KP0)
                        
                        if key_char:
                            # Debug output
                            if self.debug_mode:
                                print(f"DEBUG: Key pressed: '{key_char}' (buffer: '{self.barcode_buffer}')")
                            
                            # Try barcode input first
                            barcode = self.process_barcode_input(key_char)
                            if barcode:
                                if self.debug_mode:
                                    print(f"DEBUG: Complete barcode detected: '{barcode}'")
                                self.scan_item(barcode)
                            elif key_char.isdigit():
                                # For manual keyboard input, use as shortcut only for digits
                                if self.debug_mode:
                                    print(f"DEBUG: Using as keyboard shortcut: '{key_char}'")
                                self.scan_item(key_char)
                
                elif self.state == PAYMENT_MODE:
                    if event.key == pygame.K_p:  # BLUE button (K2) - advance payment
                        self.advance_payment()
                
                elif self.state == TIMER_MODE:
                    # Same barcode handling as retail mode
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:  # Enter key (barcode completion)
                        if self.barcode_buffer:
                            complete_barcode = self.process_barcode_complete(self.barcode_buffer)
                            if complete_barcode:
                                self.scan_timer_item(complete_barcode)
                            else:
                                self.scanned_item = f"Unknown barcode: {self.barcode_buffer}"
                            self.barcode_buffer = ""
                    # Handle ALL alphanumeric input (not just digits) for barcode scanning
                    else:
                        # Convert pygame key to character
                        key_char = None
                        if event.key >= pygame.K_0 and event.key <= pygame.K_9:
                            key_char = str(event.key - pygame.K_0)
                        elif event.key >= pygame.K_a and event.key <= pygame.K_z:
                            key_char = chr(event.key)
                        elif event.key >= pygame.K_KP0 and event.key <= pygame.K_KP9:
                            key_char = str(event.key - pygame.K_KP0)
                        
                        if key_char:
                            # Try barcode input first
                            barcode = self.process_barcode_input(key_char)
                            if barcode:
                                self.scan_timer_item(barcode)
                            elif key_char.isdigit():
                                # For manual keyboard input, use as shortcut only for digits
                                self.scan_timer_item(key_char)
                
                elif self.state == PRODUCT_MANAGER:
                    if event.key == pygame.K_e:  # Export to CSV
                        self.export_products_csv()
                        self.scanned_item = "Products exported to products.csv"
                    elif event.key == pygame.K_i:  # Import from CSV
                        if self.import_products_csv():
                            self.scanned_item = "Products imported from products.csv"
                        else:
                            self.scanned_item = "Error importing products.csv"
                
                elif self.state == GAME_OVER:
                    # RED button to return to menu
                    if event.key == pygame.K_ESCAPE:  # RED button (K4) - Return to menu
                        self.state = MENU
            
            # Handle joystick button events
            elif event.type == pygame.JOYBUTTONDOWN:
                if self.joystick:
                    button_num = event.button
                    button_color = self.joystick_button_mapping.get(button_num, 'unknown')
                    
                    if self.debug_mode:
                        print(f"DEBUG: Joystick button {button_num} pressed ({button_color})")
                    
                    # Check for shutdown combo (red + player1 buttons)
                    if button_color in ['red', 'player1']:
                        self.check_shutdown_combo()
                    
                    # Handle button actions based on color and current state
                    if self.state == MENU:
                        if button_color == 'green':  # K1 - Self-checkout (Start/Go action)
                            self.start_retail_mode()
                        elif button_color == 'blue':  # K2 - Learning mode (Educational action)
                            self.start_timer_mode()
                        elif button_color == 'yellow':  # K3 - Product manager (Management action)
                            self.state = PRODUCT_MANAGER
                        elif button_color == 'red':  # K4 - Quit game (Stop/Exit action)
                            self.running = False
                    
                    elif self.state == RETAIL_MODE:
                        if button_color == 'green':  # K1 - Checkout (go/start action)
                            self.start_payment()
                        elif button_color == 'blue':  # K2 - Remove last item (undo action)
                            self.remove_last_item()
                        elif button_color == 'yellow':  # K3 - Clear cart (utility action)
                            self.clear_cart()
                        elif button_color == 'red':  # K4 - Home/Exit (stop action)
                            self.state = MENU
                    
                    elif self.state == PAYMENT_MODE:
                        if button_color == 'blue':  # K2 - Advance payment (primary action)
                            self.advance_payment()
                        elif button_color == 'red':  # K4 - Cancel payment (stop action)
                            self.state = RETAIL_MODE
                    
                    elif self.state == TIMER_MODE:
                        if button_color == 'red':  # K4 - Exit to menu (stop action)
                            self.state = MENU
                    
                    elif self.state == PRODUCT_MANAGER:
                        if button_color == 'red':  # K4 - Exit to menu (stop action)
                            self.state = MENU
                    
                    elif self.state == GAME_OVER:
                        if button_color == 'red':  # K4 - Return to menu (stop action)
                            self.state = MENU
            
            # Handle joystick button release events
            elif event.type == pygame.JOYBUTTONUP:
                if self.joystick:
                    button_num = event.button
                    button_color = self.joystick_button_mapping.get(button_num, 'unknown')
                    
                    # Reset shutdown combo if either button is released
                    if button_color in ['red', 'player1']:
                        self.shutdown_combo_start_time = None
                        self.shutdown_combo_active = False
    
    def check_shutdown_combo(self):
        """Check if both red and player1 buttons are currently pressed"""
        if not self.joystick:
            return
            
        # Check if both buttons are currently pressed
        red_pressed = self.joystick.get_button(3)  # Red button
        player1_pressed = self.joystick.get_button(4)  # Player1 button
        
        if red_pressed and player1_pressed:
            # Both buttons are pressed
            current_time = pygame.time.get_ticks()
            
            if not self.shutdown_combo_active:
                # Start the combo timer
                self.shutdown_combo_start_time = current_time
                self.shutdown_combo_active = True
                if self.debug_mode:
                    print("DEBUG: Shutdown combo started - hold for 3 seconds")
            else:
                # Check if held long enough
                hold_time = (current_time - self.shutdown_combo_start_time) / 1000.0
                if hold_time >= self.SHUTDOWN_COMBO_DURATION:
                    self.initiate_shutdown()
        else:
            # Reset if not both buttons pressed
            self.shutdown_combo_start_time = None
            self.shutdown_combo_active = False
    
    def initiate_shutdown(self):
        """Safely shutdown the system"""
        print("🔴 SHUTDOWN COMBO DETECTED - Shutting down system...")
        
        # Save any important data
        self.save_products(self.products_data)
        
        # Close serial connection
        if hasattr(self, 'serial_scanner') and self.serial_scanner:
            self.serial_scanner.close()
        
        # Close pygame
        pygame.quit()
        
        # Import subprocess here to avoid import at module level
        import subprocess
        
        # Shutdown the system
        try:
            subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=True)
        except subprocess.CalledProcessError:
            print("Failed to shutdown system - you may need to configure sudo permissions")
            # Fallback to just exiting the game
            import sys
            sys.exit(0)
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        if self.desktop_mode:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
            self.width = SCREEN_WIDTH
            self.height = SCREEN_HEIGHT
            self.desktop_mode = False
        else:
            self.screen = pygame.display.set_mode((WINDOWED_WIDTH, WINDOWED_HEIGHT))
            self.width = WINDOWED_WIDTH
            self.height = WINDOWED_HEIGHT
            self.desktop_mode = True
        
        # Recreate fonts for new screen size
        self.font_huge = pygame.font.Font(None, int(self.height * 0.12))
        self.font_large = pygame.font.Font(None, int(self.height * 0.08))
        self.font_medium = pygame.font.Font(None, int(self.height * 0.05))
        self.font_small = pygame.font.Font(None, int(self.height * 0.035))
    
    def start_retail_mode(self):
        """Initialize retail mode"""
        self.state = RETAIL_MODE
        self.cart = {}
        self.total_price = 0.0
        self.scanned_item = ""
        self.receipt = []
        self.barcode_buffer = ""
        self.barcode_input_time = 0
        self.last_key_time = 0
        self.cart_scroll_offset = 0
    
    def start_payment(self):
        """Start payment process"""
        if not self.cart:
            self.scanned_item = "Cart is empty!"
            return
        
        self.state = PAYMENT_MODE
        self.payment_amount = self.total_price
        self.payment_step = 0
        self.payment_start_time = pygame.time.get_ticks()
    
    def advance_payment(self):
        """Advance through payment steps"""
        self.payment_step += 1
        if self.payment_step >= 4:
            # Complete payment
            receipt = self.generate_receipt()
            with open(f"receipt_{int(time.time())}.txt", "w") as f:
                f.write("\n".join(receipt))
            self.clear_cart()
            self.state = RETAIL_MODE
            self.scanned_item = "Payment complete! Thank you!"
    
    def start_timer_mode(self):
        """Initialize learning mode with randomized product order"""
        self.state = TIMER_MODE
        self.timer_score = 0
        self.timer_correct = 0
        self.timer_start_time = pygame.time.get_ticks()
        self.timer_items_found = []
        self.learning_current_index = 0
        self.scanned_item = ""
        
        # Reset barcode input state
        self.barcode_buffer = ""
        self.barcode_input_time = 0
        self.last_key_time = 0
        
        # Randomize product order for different experience each time
        all_items = list(self.skus.values())
        random.shuffle(all_items)
        self.learning_product_order = all_items
        
        self.generate_new_target()
    
    def scan_item(self, barcode_or_key):
        """Process scanned item in retail mode"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_scan_time < self.scan_cooldown:
            return
        
        self.last_scan_time = current_time
        
        product = self.lookup_product(barcode_or_key)
        if product:
            # Use the actual SKU for cart item
            sku = barcode_or_key
            if barcode_or_key in self.keyboard_shortcuts:
                sku = self.keyboard_shortcuts[barcode_or_key]
            
            self.scanned_item = self.add_to_cart(product, sku)
        else:
            self.scanned_item = f"Product not found!"
    
    def scan_timer_item(self, barcode_or_key):
        """Process scanned item in learning mode - move to next product on wrong scans"""
        if self.debug_mode:
            print(f"DEBUG: Learning mode scan attempt: '{barcode_or_key}', target: '{self.current_target['name'] if self.current_target else 'None'}'")
        
        if not self.current_target:
            if self.debug_mode:
                print("DEBUG: No current target in learning mode")
            return
        
        # Apply scan cooldown like retail mode
        current_time = pygame.time.get_ticks()
        if current_time - self.last_scan_time < self.scan_cooldown:
            if self.debug_mode:
                print(f"DEBUG: Scan cooldown active, {current_time - self.last_scan_time}ms since last scan")
            return
        
        self.last_scan_time = current_time
        
        product = self.lookup_product(barcode_or_key)
        if self.debug_mode:
            print(f"DEBUG: Product lookup result: {product['name'] if product else 'None'}")
        
        if product:
            if product['name'] == self.current_target['name']:
                # Correct item!
                self.timer_correct += 1
                self.timer_score += 1
                self.timer_items_found.append(product['name'])
                self.scanned_item = f"✓ Correct! That's {product['name']}!"
                if self.debug_mode:
                    print(f"DEBUG: CORRECT! Score now: {self.timer_correct}")
                self.generate_new_target()
            else:
                # Wrong item - move to next product automatically
                self.scanned_item = f"That's {product['name']}. Moving to next product!"
                if self.debug_mode:
                    print(f"DEBUG: Wrong item: got '{product['name']}', expected '{self.current_target['name']}'")
                self.generate_new_target()
        else:
            # Invalid barcode - move to next product
            self.scanned_item = f"Product not found. Moving to next product!"
            if self.debug_mode:
                print(f"DEBUG: Product not found for: '{barcode_or_key}'")
            self.generate_new_target()
    
    def generate_new_target(self):
        """Generate a new target item for learning mode using randomized order"""
        if self.learning_current_index < len(self.learning_product_order):
            self.current_target = self.learning_product_order[self.learning_current_index]
            self.learning_current_index += 1
        else:
            # All products have been shown
            self.current_target = None
    
    def print_receipt(self):
        """Print current receipt"""
        if self.cart:
            receipt = self.generate_receipt()
            print("\n".join(receipt))
            self.scanned_item = "Receipt printed to console"
        else:
            self.scanned_item = "Cart is empty - no receipt to print"
    
    def clear_cart(self):
        """Clear the shopping cart"""
        self.cart = {}
        self.total_price = 0.0
        self.receipt = []
        self.cart_scroll_offset = 0
        self.scanned_item = "Cart cleared!"
    
    def remove_last_item(self):
        """Remove the last added item from cart"""
        if not self.cart:
            self.scanned_item = "Cart is empty!"
            return
        
        # Find the most recently added item
        last_item_sku = None
        last_time = 0
        
        for sku, item in self.cart.items():
            if item['first_added'] > last_time:
                last_time = item['first_added']
                last_item_sku = sku
        
        if last_item_sku:
            item = self.cart[last_item_sku]
            
            # Remove one quantity
            if item['quantity'] > 1:
                item['quantity'] -= 1
                item['total_price'] -= item['price']
                self.total_price -= item['price']
                self.scanned_item = f"Removed one {item['name']} [Qty: {item['quantity']}]"
            else:
                # Remove item completely
                self.total_price -= item['price']
                removed_name = item['name']
                del self.cart[last_item_sku]
                self.scanned_item = f"Removed {removed_name} from cart"
                
                            # Adjust scroll if needed
                total_items = len(self.cart)
                max_displayable = 4 if total_items <= 4 else 8
                if self.cart_scroll_offset > 0 and total_items <= max_displayable:
                    self.cart_scroll_offset = 0
    
    def draw_menu(self):
        """Draw the main menu with storefront banner"""
        self.screen.fill(BLACK)
        
        # Display storefront banner at top of screen
        banner_height = 0
        if self.storefront_banner:
            # Draw banner at full width against top edge
            self.screen.blit(self.storefront_banner, (0, 0))
            banner_height = self.storefront_banner.get_height()
        
        # Add tagline below banner - responsive spacing
        tagline_spacing = self.scale(20)
        tagline_y = banner_height + tagline_spacing if banner_height > 0 else self.height * 0.25
        tagline = self.font_medium.render("~ Kids' Shopping Adventure ~", True, WHITE)
        tagline_rect = tagline.get_rect(center=(self.width//2, tagline_y))
        self.screen.blit(tagline, tagline_rect)
        
        # Menu options with more intuitive colored buttons
        options = [
            ("SELF-CHECKOUT", BRIGHT_GREEN),  # GREEN = Start/Go action
            ("LEARNING MODE", BLUE),          # BLUE = Educational/Primary action
            ("PRODUCT MANAGER", YELLOW),      # YELLOW = Settings/Management
            ("QUIT GAME", RED)                # RED = Stop/Exit action
        ]
        
        # Calculate start position based on banner height - responsive spacing
        menu_spacing = self.scale(60)
        start_y = tagline_y + menu_spacing if banner_height > 0 else self.height * 0.48
        for i, (text, color) in enumerate(options):
            option_y = start_y + i * self.height * 0.08
            
            # White text for readability
            option_text = self.font_medium.render(text, True, WHITE)
            option_rect = option_text.get_rect(center=(self.width//2, option_y))
            
            # Option background box with colored border - responsive padding
            bg_padding_x = self.scale(30)
            bg_padding_y = self.scale(10)
            option_bg = pygame.Rect(option_rect.x - bg_padding_x, option_rect.y - bg_padding_y, 
                                  option_rect.width + 2*bg_padding_x, option_rect.height + 2*bg_padding_y)
            self.draw_border_box(option_bg, color, 3)  # Colored border
            
            # Draw colored circle AFTER text, positioned to the right - responsive positioning
            circle_offset = self.scale(30)
            circle_radius = self.scale(18)
            circle_x = option_bg.right + circle_offset
            circle_y = option_y
            pygame.draw.circle(self.screen, color, (circle_x, circle_y), circle_radius)
            pygame.draw.circle(self.screen, BLACK, (circle_x, circle_y), circle_radius, 3)  # Black border
            
            self.screen.blit(option_text, option_rect)
        
        # Instructions at bottom - positioned well below menu buttons - responsive spacing
        instructions = [
            "Use colored buttons to navigate | Scan barcodes to add items",
            "Press colored buttons matching the menu options above"
        ]
        
        # Calculate where menu buttons end and position instructions well below - responsive padding
        button_padding = self.scale(40)
        last_button_y = start_y + (len(options) - 1) * self.height * 0.08 + button_padding
        instructions_start_y = max(last_button_y + button_padding, self.height * 0.88)
        
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, CYAN)
            text_rect = text.get_rect(center=(self.width//2, instructions_start_y + i * self.height * 0.025))
            self.screen.blit(text, text_rect)
    
    def draw_retail_mode(self):
        """Draw self-checkout mode screen - Clean and simple for kids"""
        self.screen.fill(BLACK)
        
        # Simple title
        title = self.font_large.render("ASTRID MART - CHECKOUT", True, BRIGHT_GREEN)
        title_rect = title.get_rect(center=(self.width//2, self.height * 0.05))
        self.screen.blit(title, title_rect)
        
        # Cart items display area - Clean, no borders
        cart_area = pygame.Rect(self.width * 0.05, self.height * 0.12, 
                               self.width * 0.9, self.height * 0.4)
        
        # Display cart items - Smart layout supporting up to 8 items
        if self.cart:
            items = list(self.cart.values())
            items.sort(key=lambda x: x['first_added'])
            
            # Smart layout: 1 column for 1-4 items, 2 columns for 5-8 items
            total_items = len(items)
            
            if total_items <= 4:
                # Single column layout for 1-4 items - responsive spacing
                visible_items = min(4, total_items)
                start_idx = self.cart_scroll_offset
                end_idx = min(start_idx + visible_items, total_items)
                visible_items_list = items[start_idx:end_idx]
                
                item_height = self.scale(95)  # Responsive item height
                item_spacing = self.scale(105)  # Responsive spacing between items
                
                for i, item in enumerate(visible_items_list):
                    item_y = cart_area.y + (i * item_spacing)
                    
                    # Clean item background - no borders
                    item_bg = pygame.Rect(cart_area.x, item_y, cart_area.width, item_height)
                    pygame.draw.rect(self.screen, (30, 30, 30), item_bg)
                    
                    self.draw_cart_item(item, item_bg, cart_area)
            
            else:
                # Two column layout for 5-8 items - responsive dimensions
                visible_items = min(8, total_items)
                start_idx = self.cart_scroll_offset
                end_idx = min(start_idx + visible_items, total_items)
                visible_items_list = items[start_idx:end_idx]
                
                # Calculate column dimensions - responsive gap
                col_gap = self.scale(20)  # Responsive gap between columns
                col_width = (cart_area.width - col_gap) // 2
                col_height = self.scale(90)  # Responsive height for prominent images
                row_spacing = self.scale(100)  # Responsive spacing between rows
                
                for i, item in enumerate(visible_items_list):
                    row = i // 2
                    col = i % 2
                    
                    item_x = cart_area.x + (col * (col_width + col_gap))
                    item_y = cart_area.y + (row * row_spacing)
                    
                    # Clean item background - no borders
                    item_bg = pygame.Rect(item_x, item_y, col_width, col_height)
                    pygame.draw.rect(self.screen, (30, 30, 30), item_bg)
                    
                    self.draw_cart_item(item, item_bg, cart_area, is_compact=True)
            
            # Simple scroll indicators - only show if needed
            max_displayable = 4 if total_items <= 4 else 8
            if total_items > max_displayable:
                if self.cart_scroll_offset > 0:
                    up_text = self.font_large.render("▲", True, BRIGHT_GREEN)
                    up_rect = up_text.get_rect(center=(cart_area.right - 30, cart_area.y + 20))
                    self.screen.blit(up_text, up_rect)
                
                if self.cart_scroll_offset < total_items - max_displayable:
                    down_text = self.font_large.render("▼", True, BRIGHT_GREEN)
                    down_rect = down_text.get_rect(center=(cart_area.right - 30, cart_area.bottom - 20))
                    self.screen.blit(down_text, down_rect)
        else:
            # Simple empty cart message
            empty_text = self.font_large.render("Cart is empty - scan an item!", True, WHITE)
            empty_rect = empty_text.get_rect(center=(cart_area.centerx, cart_area.centery))
            self.screen.blit(empty_text, empty_rect)
        
        # TOTAL - Clean and big, centered - moved lower to avoid overlap
        total_y = cart_area.bottom + 80
        
        # Total price - HUGE and clean
        total_price_text = self.font_huge.render(f"TOTAL: €{self.total_price:.2f}", True, YELLOW)
        total_price_rect = total_price_text.get_rect(center=(self.width//2, total_y))
        # Simple background
        total_bg = pygame.Rect(total_price_rect.x - 20, total_price_rect.y - 10, 
                              total_price_rect.width + 40, total_price_rect.height + 20)
        pygame.draw.rect(self.screen, (40, 40, 0), total_bg)
        self.screen.blit(total_price_text, total_price_rect)
        
        # 4 ARCADE BUTTONS - Clean and simple
        button_y = total_price_rect.bottom + 50
        button_width = self.width * 0.22  # Slightly wider buttons
        button_height = self.height * 0.1
        
        # 4 essential buttons - just the action text
        buttons = [
            ("CHECKOUT", BRIGHT_GREEN),
            ("REMOVE", BLUE), 
            ("CLEAR ALL", YELLOW),
            ("HOME", RED)
        ]
        
        # Center the buttons - responsive spacing
        button_spacing = self.scale(20)  # Responsive spacing between buttons
        total_buttons_width = len(buttons) * button_width + (len(buttons) - 1) * button_spacing
        start_x = (self.width - total_buttons_width) // 2
        
        for i, (action, color) in enumerate(buttons):
            button_x = start_x + (i * (button_width + button_spacing))
            
            # Clean button design with subtle border
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 3)
            
            # Bold action text - properly sized and centered
            # Use medium font to ensure text fits
            action_text = self.font_medium.render(action, True, BLACK)
            action_rect = action_text.get_rect(center=button_rect.center)
            
            # Only add outline if text is short enough - responsive padding
            if action_text.get_width() < button_width - self.scale(20):
                # Add subtle shadow for readability
                shadow_text = self.font_medium.render(action, True, WHITE)
                shadow_rect = shadow_text.get_rect(center=(button_rect.centerx + 1, button_rect.centery + 1))
                self.screen.blit(shadow_text, shadow_rect)
            
            self.screen.blit(action_text, action_rect)
        
        # Status message - Clean and simple - responsive spacing
        if self.scanned_item:
            status_y = button_y + button_height + self.scale(30)
            
            # Clean scan feedback
            message_text = self.font_medium.render(f"✓ {self.scanned_item}", True, BRIGHT_GREEN)
            message_rect = message_text.get_rect(center=(self.width//2, status_y))
            self.screen.blit(message_text, message_rect)
    
    def draw_payment_mode(self):
        """Draw payment process screen - clean button design"""
        self.screen.fill(BLACK)
        
        # Title - responsive padding
        title = self.font_large.render("PAYMENT", True, GREEN)
        title_rect = title.get_rect(center=(self.width//2, self.height * 0.15))
        title_bg = pygame.Rect(title_rect.x - self.scale(20), title_rect.y - self.scale(10), 
                              title_rect.width + self.scale(40), title_rect.height + self.scale(20))
        self.draw_border_box(title_bg, GREEN, 4)
        self.screen.blit(title, title_rect)
        
        # Payment steps
        if self.payment_step == 0:
            # Show total amount
            amount_text = self.font_huge.render(f"€{self.payment_amount:.2f}", True, YELLOW)
            amount_rect = amount_text.get_rect(center=(self.width//2, self.height * 0.4))
            self.screen.blit(amount_text, amount_rect)
            
            # Clear buttons instead of confusing tiny circles
            button_width = self.width * 0.3  # Responsive button width
            button_height = self.height * 0.08  # Responsive button height
            
            # BLUE button - Pay
            pay_button_y = self.height * 0.6
            pay_button_rect = pygame.Rect(self.width//2 - button_width//2, pay_button_y, button_width, button_height)
            pygame.draw.rect(self.screen, BLUE, pay_button_rect)
            pygame.draw.rect(self.screen, BLACK, pay_button_rect, 3)
            
            pay_text = self.font_medium.render("PAY NOW", True, BLACK)
            pay_text_rect = pay_text.get_rect(center=pay_button_rect.center)
            self.screen.blit(pay_text, pay_text_rect)
            
            # RED button - Cancel
            cancel_button_y = self.height * 0.75
            cancel_button_rect = pygame.Rect(self.width//2 - button_width//2, cancel_button_y, button_width, button_height)
            pygame.draw.rect(self.screen, RED, cancel_button_rect)
            pygame.draw.rect(self.screen, BLACK, cancel_button_rect, 3)
            
            cancel_text = self.font_medium.render("CANCEL", True, BLACK)
            cancel_text_rect = cancel_text.get_rect(center=cancel_button_rect.center)
            self.screen.blit(cancel_text, cancel_text_rect)
        
        elif self.payment_step == 1:
            # Processing payment
            processing_text = self.font_large.render("Processing Payment...", True, YELLOW)
            processing_rect = processing_text.get_rect(center=(self.width//2, self.height * 0.4))
            self.screen.blit(processing_text, processing_rect)
            
            # Animate dots
            dots = "." * ((pygame.time.get_ticks() // 500) % 4)
            dots_text = self.font_large.render(dots, True, YELLOW)
            dots_rect = dots_text.get_rect(center=(self.width//2, self.height * 0.5))
            self.screen.blit(dots_text, dots_rect)
            
            # BLUE button - Continue
            button_width = self.width * 0.3
            button_height = self.height * 0.08
            continue_button_y = self.height * 0.7
            continue_button_rect = pygame.Rect(self.width//2 - button_width//2, continue_button_y, button_width, button_height)
            pygame.draw.rect(self.screen, BLUE, continue_button_rect)
            pygame.draw.rect(self.screen, BLACK, continue_button_rect, 3)
            
            continue_text = self.font_medium.render("CONTINUE", True, BLACK)
            continue_text_rect = continue_text.get_rect(center=continue_button_rect.center)
            self.screen.blit(continue_text, continue_text_rect)
        
        elif self.payment_step == 2:
            # Payment successful
            success_text = self.font_large.render("PAYMENT SUCCESSFUL!", True, GREEN)
            success_rect = success_text.get_rect(center=(self.width//2, self.height * 0.4))
            self.screen.blit(success_text, success_rect)
            
            # BLUE button - Get Receipt
            button_width = self.width * 0.3
            button_height = self.height * 0.08
            receipt_button_y = self.height * 0.6
            receipt_button_rect = pygame.Rect(self.width//2 - button_width//2, receipt_button_y, button_width, button_height)
            pygame.draw.rect(self.screen, BLUE, receipt_button_rect)
            pygame.draw.rect(self.screen, BLACK, receipt_button_rect, 3)
            
            receipt_text = self.font_medium.render("GET RECEIPT", True, BLACK)
            receipt_text_rect = receipt_text.get_rect(center=receipt_button_rect.center)
            self.screen.blit(receipt_text, receipt_text_rect)
        
        elif self.payment_step == 3:
            # Receipt and thank you
            thank_you_text = self.font_large.render("THANK YOU!", True, BRIGHT_GREEN)
            thank_you_rect = thank_you_text.get_rect(center=(self.width//2, self.height * 0.35))
            self.screen.blit(thank_you_text, thank_you_rect)
            
            receipt_text = self.font_medium.render("Receipt saved", True, WHITE)
            receipt_rect = receipt_text.get_rect(center=(self.width//2, self.height * 0.5))
            self.screen.blit(receipt_text, receipt_rect)
            
            # BLUE button - Continue Shopping
            button_width = self.width * 0.35
            button_height = self.height * 0.08
            continue_button_y = self.height * 0.65
            continue_button_rect = pygame.Rect(self.width//2 - button_width//2, continue_button_y, button_width, button_height)
            pygame.draw.rect(self.screen, BLUE, continue_button_rect)
            pygame.draw.rect(self.screen, BLACK, continue_button_rect, 3)
            
            continue_text = self.font_medium.render("CONTINUE SHOPPING", True, BLACK)
            continue_text_rect = continue_text.get_rect(center=continue_button_rect.center)
            self.screen.blit(continue_text, continue_text_rect)
    
    def draw_timer_mode(self):
        """Draw learning mode screen - clean, no borders, high quality images"""
        self.screen.fill(BLACK)
        
        # Title
        title = self.font_large.render("ASTRID MART - LEARNING MODE", True, ORANGE)
        title_rect = title.get_rect(center=(self.width//2, self.height * 0.05))
        self.screen.blit(title, title_rect)
        
        # Progress and score info - no timer!
        info_y = self.height * 0.12
        
        all_items = len(self.learning_product_order) if hasattr(self, 'learning_product_order') else len(self.skus.values())
        progress_text = self.font_medium.render(f"PRODUCT: {self.learning_current_index}/{all_items}", True, WHITE)
        score_text = self.font_medium.render(f"CORRECT: {self.timer_correct}", True, BRIGHT_GREEN)
        
        self.screen.blit(progress_text, (self.width * 0.2, info_y))
        self.screen.blit(score_text, (self.width * 0.6, info_y))
        
        # Check if all products have been shown
        if not self.current_target:
            self.state = GAME_OVER
            return
        
        # Main product display area - clean and simple
        target_y = self.height * 0.25
        
        # Instruction
        find_text = self.font_large.render("SCAN THIS PRODUCT:", True, PURPLE)
        find_rect = find_text.get_rect(center=(self.width//2, target_y))
        self.screen.blit(find_text, find_rect)
        
        # HUGE PRODUCT IMAGE - arcade style with original quality
        image_y = target_y + self.scale(60)
        image_size = self.scale(400)  # Much bigger image - 400px scaled to screen
        image_rect = pygame.Rect(self.width//2 - image_size//2, image_y, image_size, image_size)
        
        # Get the SKU for this target to find its image
        target_sku = None
        for sku, product in self.skus.items():
            if product['name'] == self.current_target['name']:
                target_sku = sku
                break
        
        if target_sku and target_sku in self.product_images:
            # Scale to huge size while preserving original quality
            image = self.product_images[target_sku]
            image_scaled = pygame.transform.scale(image, (image_size, image_size))
            self.screen.blit(image_scaled, image_rect)
        else:
            # Fallback if no image - simple gray box
            pygame.draw.rect(self.screen, (50, 50, 50), image_rect)
            no_image_text = self.font_medium.render("No Image", True, WHITE)
            no_image_rect = no_image_text.get_rect(center=image_rect.center)
            self.screen.blit(no_image_text, no_image_rect)
        
        # Product name below image - clean, no borders
        name_y = image_rect.bottom + self.scale(20)
        target_text = self.font_large.render(self.current_target['name'], True, HOT_PINK)
        target_rect = target_text.get_rect(center=(self.width//2, name_y))
        self.screen.blit(target_text, target_rect)
        
        # Feedback message - positioned below product name
        if self.scanned_item:
            feedback_y = name_y + self.scale(50)
            
            # Color based on message type
            feedback_color = BRIGHT_GREEN if "✓ Correct" in self.scanned_item else ORANGE
            feedback_text = self.font_medium.render(self.scanned_item, True, feedback_color)
            feedback_rect = feedback_text.get_rect(center=(self.width//2, feedback_y))
            self.screen.blit(feedback_text, feedback_rect)
        
        # Exit button at bottom - clear and responsive
        button_width = self.width * 0.25
        button_height = self.height * 0.06
        exit_button_y = self.height * 0.95
        exit_button_rect = pygame.Rect(self.width//2 - button_width//2, exit_button_y, button_width, button_height)
        pygame.draw.rect(self.screen, RED, exit_button_rect)
        pygame.draw.rect(self.screen, BLACK, exit_button_rect, 3)
        
        exit_text = self.font_small.render("RED BUTTON = EXIT", True, BLACK)
        exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)
        self.screen.blit(exit_text, exit_text_rect)
    
    def draw_product_manager(self):
        """Draw product manager screen"""
        self.screen.fill(BLACK)
        
        # Title
        title = self.font_large.render("PRODUCT MANAGER", True, PURPLE)
        title_rect = title.get_rect(center=(self.width//2, self.height * 0.1))
        title_bg = pygame.Rect(title_rect.x - 20, title_rect.y - 10, 
                              title_rect.width + 40, title_rect.height + 20)
        self.draw_border_box(title_bg, PURPLE, 4)
        self.screen.blit(title, title_rect)
        
        # Product count
        count_text = self.font_medium.render(f"Products in database: {len(self.skus)}", True, WHITE)
        count_rect = count_text.get_rect(center=(self.width//2, self.height * 0.25))
        self.screen.blit(count_text, count_rect)
        
        # Instructions
        instructions = [
            "E - Export products to CSV file",
            "I - Import products from CSV file",
            "ESC - Back to menu"
        ]
        
        start_y = self.height * 0.4
        for i, instruction in enumerate(instructions):
            text = self.font_medium.render(instruction, True, CYAN)
            text_rect = text.get_rect(center=(self.width//2, start_y + i * self.height * 0.08))
            self.screen.blit(text, text_rect)
        
        # CSV format example
        example_y = self.height * 0.65
        example_title = self.font_small.render("CSV Format Example:", True, YELLOW)
        self.screen.blit(example_title, (self.width * 0.1, example_y))
        
        csv_example = [
            "SKU,Name,Price,Category,Description,Image",
            "7501234567890,White Bread,2.20,Bakery,Fresh bread,images/bread.png"
        ]
        
        for i, line in enumerate(csv_example):
            text = self.font_small.render(line, True, WHITE)
            self.screen.blit(text, (self.width * 0.1, example_y + 30 + i * 25))
        
        # Status message
        if self.scanned_item:
            status_text = self.font_small.render(self.scanned_item, True, GREEN)
            status_rect = status_text.get_rect(center=(self.width//2, self.height * 0.85))
            self.screen.blit(status_text, status_rect)
    
    def draw_game_over(self):
        """Draw game over screen with big blinking score"""
        self.screen.fill(BLACK)
        
        # Title
        title = self.font_huge.render("LEARNING COMPLETE!", True, BRIGHT_GREEN)
        title_rect = title.get_rect(center=(self.width//2, self.height * 0.2))
        self.screen.blit(title, title_rect)
        
        # Your Score text
        score_label = self.font_large.render("Your Score:", True, WHITE)
        score_label_rect = score_label.get_rect(center=(self.width//2, self.height * 0.4))
        self.screen.blit(score_label, score_label_rect)
        
        # BIG BLINKING SCORE NUMBER
        blink_time = pygame.time.get_ticks()
        score_color = YELLOW if (blink_time // 500) % 2 == 0 else RED
        
        # Make an even bigger font for the score
        score_font = pygame.font.Font(None, int(self.height * 0.2))  # 20% of screen height
        score_text = score_font.render(str(self.timer_correct), True, score_color)
        score_rect = score_text.get_rect(center=(self.width//2, self.height * 0.55))
        self.screen.blit(score_text, score_rect)
        
        # Total products attempted
        total_items = len(self.learning_product_order) if hasattr(self, 'learning_product_order') else len(self.skus.values())
        total_text = self.font_medium.render(f"out of {total_items} products", True, CYAN)
        total_rect = total_text.get_rect(center=(self.width//2, self.height * 0.7))
        self.screen.blit(total_text, total_rect)
        
        # Continue instruction - use RED button which goes back to menu
        continue_text = self.font_medium.render("Press     button to continue", True, WHITE)
        continue_rect = continue_text.get_rect(center=(self.width//2, self.height * 0.85))
        # Draw red circle (K4 - Exit/Continue action)
        circle_x = continue_rect.centerx - 60
        pygame.draw.circle(self.screen, RED, (circle_x, continue_rect.centery), 15)
        pygame.draw.circle(self.screen, BLACK, (circle_x, continue_rect.centery), 15, 2)
        self.screen.blit(continue_text, continue_rect)
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            
            # Check for serial scanner input
            self.check_serial_scanner()
            
            # Check shutdown combo continuously
            if self.shutdown_combo_active:
                self.check_shutdown_combo()
            
            # Draw based on current state
            if self.state == MENU:
                self.draw_menu()
            elif self.state == RETAIL_MODE:
                self.draw_retail_mode()
            elif self.state == PAYMENT_MODE:
                self.draw_payment_mode()
            elif self.state == TIMER_MODE:
                self.draw_timer_mode()
            elif self.state == GAME_OVER:
                self.draw_game_over()
            elif self.state == PRODUCT_MANAGER:
                self.draw_product_manager()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        # Clean up serial scanner
        if self.serial_scanner:
            self.serial_running = False
            if self.serial_thread:
                self.serial_thread.join(timeout=1.0)
            self.serial_scanner.close()
        
        # Clean up joystick
        if self.joystick:
            self.joystick.quit()
        
        pygame.quit()

if __name__ == "__main__":
    # Check for help argument
    if '--help' in os.sys.argv or '-h' in os.sys.argv:
        print("Arcade Retail Store Game")
        print("Usage: python main.py [options]")
        print("")
        print("Options:")
        print("  --windowed    Run in windowed mode (for testing)")
        print("  --debug       Enable debug mode for barcode scanner")
        print("  --help, -h    Show this help message")
        print("")
        print("Example:")
        print("  python main.py --windowed --debug")
        exit(0)
    
    game = ArcadeRetailGame()
    game.run() 