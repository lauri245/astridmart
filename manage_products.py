#!/usr/bin/env python3
"""
Product Management Tool for Arcade Retail Store
Simple command-line interface to manage SKUs and products
"""

import json
import csv
import os

class ProductManager:
    def __init__(self):
        self.products_file = 'products.json'
        self.products_data = self.load_products()
        self.skus = self.products_data.get('skus', {})
        self.keyboard_shortcuts = self.products_data.get('keyboard_shortcuts', {})
    
    def load_products(self):
        """Load products from JSON file"""
        try:
            with open(self.products_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Products file {self.products_file} not found. Creating new one...")
            return {"skus": {}, "keyboard_shortcuts": {}}
    
    def save_products(self):
        """Save products to JSON file"""
        self.products_data['skus'] = self.skus
        self.products_data['keyboard_shortcuts'] = self.keyboard_shortcuts
        with open(self.products_file, 'w') as f:
            json.dump(self.products_data, f, indent=2)
        print(f"Products saved to {self.products_file}")
    
    def add_product(self):
        """Add a new product"""
        print("\n--- Add New Product ---")
        sku = input("Enter SKU (e.g., 7501234567890): ").strip()
        
        if sku in self.skus:
            print(f"SKU {sku} already exists!")
            return
        
        name = input("Enter product name: ").strip()
        
        try:
            price = float(input("Enter price in EUR: €"))
        except ValueError:
            print("Invalid price entered!")
            return
        
        category = input("Enter category: ").strip()
        description = input("Enter description (optional): ").strip()
        image_path = input("Enter image path (optional, e.g., images/product.png): ").strip()
        
        self.skus[sku] = {
            'name': name,
            'price': price,
            'category': category,
            'description': description,
            'image': image_path
        }
        
        # Ask for keyboard shortcut
        shortcut = input("Assign keyboard shortcut (0-9, or press Enter to skip): ").strip()
        if shortcut and shortcut.isdigit() and len(shortcut) == 1:
            # Remove existing shortcut if any
            for key, existing_sku in list(self.keyboard_shortcuts.items()):
                if existing_sku == sku:
                    del self.keyboard_shortcuts[key]
            
            self.keyboard_shortcuts[shortcut] = sku
            print(f"Keyboard shortcut '{shortcut}' assigned to {name}")
        
        print(f"Product '{name}' added successfully!")
        self.save_products()
    
    def edit_product(self):
        """Edit an existing product"""
        print("\n--- Edit Product ---")
        sku = input("Enter SKU to edit: ").strip()
        
        if sku not in self.skus:
            print(f"SKU {sku} not found!")
            return
        
        product = self.skus[sku]
        print(f"\nEditing: {product['name']}")
        print("Press Enter to keep current value, or type new value:")
        
        name = input(f"Name [{product['name']}]: ").strip()
        if name:
            product['name'] = name
        
        price_input = input(f"Price in EUR [{product['price']}]: ").strip()
        if price_input:
            try:
                product['price'] = float(price_input)
            except ValueError:
                print("Invalid price, keeping current value")
        
        category = input(f"Category [{product['category']}]: ").strip()
        if category:
            product['category'] = category
        
        description = input(f"Description [{product.get('description', '')}]: ").strip()
        if description or description == "":
            product['description'] = description
        
        image = input(f"Image path [{product.get('image', '')}]: ").strip()
        if image or image == "":
            product['image'] = image
        
        print(f"Product '{product['name']}' updated successfully!")
        self.save_products()
    
    def list_products(self):
        """List all products"""
        print("\n--- Product List ---")
        if not self.skus:
            print("No products found.")
            return
        
        print(f"{'SKU':<15} {'Name':<20} {'Price':<8} {'Category':<12} {'Shortcut':<8} {'Image':<15}")
        print("-" * 85)
        
        for sku, product in self.skus.items():
            shortcut = ""
            for key, mapped_sku in self.keyboard_shortcuts.items():
                if mapped_sku == sku:
                    shortcut = key
                    break
            
            image_display = "✓" if product.get('image') and os.path.exists(product.get('image', '')) else "✗"
            
            print(f"{sku:<15} {product['name']:<20} €{product['price']:<7.2f} {product['category']:<12} {shortcut:<8} {image_display:<15}")
    
    def delete_product(self):
        """Delete a product"""
        print("\n--- Delete Product ---")
        sku = input("Enter SKU to delete: ").strip()
        
        if sku not in self.skus:
            print(f"SKU {sku} not found!")
            return
        
        product_name = self.skus[sku]['name']
        confirm = input(f"Are you sure you want to delete '{product_name}'? (y/N): ").lower()
        
        if confirm == 'y':
            del self.skus[sku]
            
            # Remove keyboard shortcut if exists
            for key, mapped_sku in list(self.keyboard_shortcuts.items()):
                if mapped_sku == sku:
                    del self.keyboard_shortcuts[key]
                    break
            
            print(f"Product '{product_name}' deleted successfully!")
            self.save_products()
        else:
            print("Deletion cancelled.")
    
    def export_csv(self):
        """Export products to CSV"""
        csv_file = 'products.csv'
        try:
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['SKU', 'Name', 'Price', 'Category', 'Description', 'Image'])
                
                for sku, product in self.skus.items():
                    writer.writerow([
                        sku,
                        product['name'],
                        product['price'],
                        product['category'],
                        product.get('description', ''),
                        product.get('image', '')
                    ])
            
            print(f"Products exported to {csv_file}")
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
    
    def import_csv(self):
        """Import products from CSV"""
        csv_file = 'products.csv'
        
        if not os.path.exists(csv_file):
            print(f"CSV file {csv_file} not found!")
            return
        
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                new_count = 0
                updated_count = 0
                
                for row in reader:
                    sku = row['SKU']
                    
                    if sku in self.skus:
                        updated_count += 1
                    else:
                        new_count += 1
                    
                    self.skus[sku] = {
                        'name': row['Name'],
                        'price': float(row['Price']),
                        'category': row['Category'],
                        'description': row.get('Description', ''),
                        'image': row.get('Image', '')
                    }
                
                self.save_products()
                print(f"CSV imported successfully!")
                print(f"New products: {new_count}, Updated products: {updated_count}")
                
        except Exception as e:
            print(f"Error importing CSV: {e}")
    
    def assign_shortcuts(self):
        """Assign keyboard shortcuts to products"""
        print("\n--- Assign Keyboard Shortcuts ---")
        print("Current shortcuts:")
        
        for key in "0123456789":
            if key in self.keyboard_shortcuts:
                sku = self.keyboard_shortcuts[key]
                name = self.skus.get(sku, {}).get('name', 'Unknown')
                print(f"  {key}: {name} ({sku})")
            else:
                print(f"  {key}: (unassigned)")
        
        print("\nAvailable products:")
        unassigned_products = []
        for sku, product in self.skus.items():
            is_assigned = False
            for mapped_sku in self.keyboard_shortcuts.values():
                if mapped_sku == sku:
                    is_assigned = True
                    break
            if not is_assigned:
                unassigned_products.append((sku, product['name']))
        
        if unassigned_products:
            for i, (sku, name) in enumerate(unassigned_products[:10]):
                print(f"  {sku}: {name}")
        else:
            print("  All products have shortcuts assigned")
        
        key = input("\nEnter key (0-9) to assign/reassign: ").strip()
        if not (key.isdigit() and len(key) == 1):
            print("Invalid key!")
            return
        
        sku = input("Enter SKU to assign to this key: ").strip()
        if sku not in self.skus:
            print("SKU not found!")
            return
        
        self.keyboard_shortcuts[key] = sku
        product_name = self.skus[sku]['name']
        print(f"Key '{key}' assigned to '{product_name}'")
        self.save_products()
    
    def manage_images(self):
        """Manage product images"""
        print("\n--- Manage Product Images ---")
        print("Image status for all products:")
        
        for sku, product in self.skus.items():
            image_path = product.get('image', '')
            status = "✓ Found" if image_path and os.path.exists(image_path) else "✗ Missing"
            print(f"  {product['name']}: {image_path} ({status})")
        
        print("\nOptions:")
        print("1. Set image for a product")
        print("2. Create placeholder images")
        print("3. Return to main menu")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            sku = input("Enter SKU: ").strip()
            if sku not in self.skus:
                print("SKU not found!")
                return
            
            current_image = self.skus[sku].get('image', '')
            print(f"Current image: {current_image}")
            
            new_image = input("Enter new image path (or press Enter to clear): ").strip()
            self.skus[sku]['image'] = new_image
            self.save_products()
            print("Image path updated!")
        
        elif choice == '2':
            if os.path.exists('create_placeholder_images.py'):
                os.system('python3 create_placeholder_images.py')
            else:
                print("Placeholder image generator not found!")
        
        elif choice == '3':
            return
        else:
            print("Invalid choice!")
    
    def set_prices(self):
        """Bulk set or adjust prices"""
        print("\n--- Set Prices ---")
        print("Current prices:")
        
        total_value = 0
        for sku, product in self.skus.items():
            print(f"  {product['name']}: €{product['price']:.2f}")
            total_value += product['price']
        
        print(f"\nTotal catalog value: €{total_value:.2f}")
        print(f"Average price: €{total_value/len(self.skus):.2f}" if self.skus else "")
        
        print("\nOptions:")
        print("1. Set price for individual product")
        print("2. Apply percentage change to all prices")
        print("3. Set price range (min/max)")
        print("4. Return to main menu")
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == '1':
            sku = input("Enter SKU: ").strip()
            if sku not in self.skus:
                print("SKU not found!")
                return
            
            product = self.skus[sku]
            print(f"Current price for {product['name']}: €{product['price']:.2f}")
            
            try:
                new_price = float(input("Enter new price: €"))
                product['price'] = new_price
                self.save_products()
                print(f"Price updated to €{new_price:.2f}")
            except ValueError:
                print("Invalid price!")
        
        elif choice == '2':
            try:
                percentage = float(input("Enter percentage change (+10 for 10% increase, -5 for 5% decrease): "))
                multiplier = 1 + (percentage / 100)
                
                for sku, product in self.skus.items():
                    old_price = product['price']
                    new_price = round(old_price * multiplier, 2)
                    product['price'] = new_price
                    print(f"  {product['name']}: €{old_price:.2f} → €{new_price:.2f}")
                
                self.save_products()
                print("All prices updated!")
            except ValueError:
                print("Invalid percentage!")
        
        elif choice == '3':
            try:
                min_price = float(input("Enter minimum price: €"))
                max_price = float(input("Enter maximum price: €"))
                
                if min_price >= max_price:
                    print("Minimum price must be less than maximum price!")
                    return
                
                for sku, product in self.skus.items():
                    old_price = product['price']
                    new_price = max(min_price, min(max_price, old_price))
                    if new_price != old_price:
                        product['price'] = new_price
                        print(f"  {product['name']}: €{old_price:.2f} → €{new_price:.2f}")
                
                self.save_products()
                print("Prices adjusted to range!")
            except ValueError:
                print("Invalid price values!")
        
        elif choice == '4':
            return
        else:
            print("Invalid choice!")
    
    def run(self):
        """Main menu loop"""
        while True:
            print("\n" + "="*60)
            print("🛒 ARCADE RETAIL STORE - PRODUCT MANAGER")
            print("="*60)
            print(f"📦 Products in database: {len(self.skus)}")
            
            if self.skus:
                total_value = sum(product['price'] for product in self.skus.values())
                print(f"💰 Total catalog value: €{total_value:.2f}")
                
                # Check image status
                with_images = sum(1 for p in self.skus.values() if p.get('image') and os.path.exists(p.get('image', '')))
                print(f"🖼️  Products with images: {with_images}/{len(self.skus)}")
            
            print()
            print("1. 📋 List all products")
            print("2. ➕ Add new product")
            print("3. ✏️  Edit product")
            print("4. ❌ Delete product")
            print("5. ⌨️  Assign keyboard shortcuts")
            print("6. 💰 Manage prices")
            print("7. 🖼️  Manage images")
            print("8. 📤 Export to CSV")
            print("9. 📥 Import from CSV")
            print("0. 🚪 Quit")
            print()
            
            choice = input("Enter your choice (0-9): ").strip()
            
            if choice == '1':
                self.list_products()
            elif choice == '2':
                self.add_product()
            elif choice == '3':
                self.edit_product()
            elif choice == '4':
                self.delete_product()
            elif choice == '5':
                self.assign_shortcuts()
            elif choice == '6':
                self.set_prices()
            elif choice == '7':
                self.manage_images()
            elif choice == '8':
                self.export_csv()
            elif choice == '9':
                self.import_csv()
            elif choice == '0':
                print("Goodbye! 👋")
                break
            else:
                print("Invalid choice!")
            
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    manager = ProductManager()
    manager.run() 