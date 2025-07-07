#!/usr/bin/env python3
"""
Test Barcode Scanner - Simple test to verify barcode scanner setup
Run this to test if your barcode scanner is working correctly with the game
"""

import json
import threading
import time
import queue
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("pyserial not available - serial barcode scanners won't work")

def setup_serial_scanner():
    """Setup serial barcode scanner if available"""
    if not SERIAL_AVAILABLE:
        return None
    
    try:
        # List all available serial ports
        ports = serial.tools.list_ports.comports()
        scanner_port = None
        
        print("\n📡 SERIAL PORT DETECTION:")
        for port in ports:
            port_name = port.device.lower()
            print(f"   Found: {port.device} - {port.description}")
            
            # Check for USB modem patterns (like your scanner)
            if 'usbmodem' in port_name or 'usb' in port.description.lower():
                scanner_port = port.device
                print(f"   ✅ Potential scanner port: {scanner_port}")
                break
        
        if scanner_port:
            # Try to open the scanner
            scanner = serial.Serial(
                port=scanner_port,
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1
            )
            print(f"🔍 Serial barcode scanner connected: {scanner_port}")
            return scanner
        else:
            print("❌ No serial barcode scanner found")
            return None
            
    except Exception as e:
        print(f"❌ Serial scanner setup failed: {e}")
        return None

def read_serial_scanner(scanner, scan_queue, running):
    """Read data from serial barcode scanner"""
    if not scanner:
        return
    
    barcode_buffer = ""
    
    while running[0]:
        try:
            if scanner.in_waiting > 0:
                # Read available data
                data = scanner.read(scanner.in_waiting)
                text = data.decode('utf-8', errors='ignore').strip()
                
                if text:
                    print(f"📡 Serial received: '{text}'")
                    
                    # Check if this looks like a complete barcode
                    if len(text) >= 8 and text.isalnum():
                        # Put complete barcode in queue
                        scan_queue.put(text)
                        print(f"✅ Complete barcode detected: '{text}'")
                    else:
                        # Handle partial data
                        barcode_buffer += text
                        if len(barcode_buffer) >= 8 and barcode_buffer.isalnum():
                            scan_queue.put(barcode_buffer)
                            print(f"✅ Buffered barcode complete: '{barcode_buffer}'")
                            barcode_buffer = ""
            
            time.sleep(0.01)  # Small delay to prevent busy waiting
            
        except Exception as e:
            print(f"❌ Serial scanner read error: {e}")
            time.sleep(0.1)

def main():
    print("🔍 BARCODE SCANNER TEST")
    print("=" * 50)
    
    # Load the products database
    try:
        with open('products.json', 'r') as f:
            products_data = json.load(f)
            skus = products_data.get('skus', {})
    except FileNotFoundError:
        print("❌ Error: products.json not found!")
        return
    
    print("📦 Available products in database:")
    for sku, product in skus.items():
        print(f"   {product['name']} - Barcode: {sku}")
    
    # Setup serial scanner
    serial_scanner = setup_serial_scanner()
    scan_queue = queue.Queue()
    running = [True]
    
    if serial_scanner:
        # Start serial reading thread
        serial_thread = threading.Thread(target=read_serial_scanner, args=(serial_scanner, scan_queue, running), daemon=True)
        serial_thread.start()
    
    print("\n🔍 SCANNER TEST:")
    print("1. Use your barcode scanner to scan one of the products above")
    print("2. Or manually type a barcode and press Enter")
    print("3. Type 'quit' to exit")
    print("\nWaiting for barcode input...")
    
    while True:
        try:
            # Check for serial scanner input
            barcode_from_scanner = None
            if serial_scanner:
                try:
                    while not scan_queue.empty():
                        barcode_from_scanner = scan_queue.get_nowait()
                        break
                except queue.Empty:
                    pass
            
            # If we got a barcode from scanner, process it
            if barcode_from_scanner:
                user_input = barcode_from_scanner
                print(f"📡 Serial scanner input: {user_input}")
            else:
                # Get manual input
                user_input = input("\nScan barcode or type 'quit': ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Clean the input (keep only alphanumeric characters)
            clean_barcode = ''.join(filter(str.isalnum, user_input))
            
            if clean_barcode in skus:
                product = skus[clean_barcode]
                print(f"✅ SUCCESS! Found product:")
                print(f"   📦 {product['name']}")
                print(f"   💰 €{product['price']:.2f}")
                print(f"   🏷️  {product['category']}")
                print(f"   🔍 Barcode: {clean_barcode}")
                print(f"   ✨ This will work perfectly in the game!")
            else:
                print(f"❌ Barcode not found: {clean_barcode}")
                print(f"   Available barcodes: {', '.join(skus.keys())}")
                
                # Check if it's a partial match
                partial_matches = [sku for sku in skus.keys() if sku.startswith(clean_barcode)]
                if partial_matches:
                    print(f"   📝 Did you mean one of these? {', '.join(partial_matches)}")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Clean up
    if serial_scanner:
        running[0] = False
        time.sleep(0.1)
        serial_scanner.close()

if __name__ == "__main__":
    main() 