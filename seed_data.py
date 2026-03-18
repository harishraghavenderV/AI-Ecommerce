"""Seed script to populate the database with sample products and an admin user."""
from app import app, db
from models import User, Product
from werkzeug.security import generate_password_hash
import json


def seed():
    with app.app_context():
        db.create_all()

        # Admin user
        if not User.query.filter_by(email='admin@shop.com').first():
            admin = User(
                username='admin',
                email='admin@shop.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                addresses=json.dumps([{
                    'label': 'Office',
                    'street': '123 Admin St',
                    'city': 'Tech City',
                    'state': 'CA',
                    'zip': '90001',
                    'phone': '555-0100'
                }])
            )
            db.session.add(admin)

        # Demo user
        if not User.query.filter_by(email='demo@shop.com').first():
            demo = User(
                username='demo',
                email='demo@shop.com',
                password_hash=generate_password_hash('demo123'),
                is_admin=False,
                addresses=json.dumps([{
                    'label': 'Home',
                    'street': '456 Main Ave',
                    'city': 'Sample Town',
                    'state': 'NY',
                    'zip': '10001',
                    'phone': '555-0200'
                }])
            )
            db.session.add(demo)

        # Products
        products_data = [
            {
                'name': 'Wireless Noise-Cancelling Headphones',
                'description': 'Premium wireless headphones with active noise cancellation, 30-hour battery life, and crystal-clear audio. Features Bluetooth 5.2, foldable design, and built-in microphone for calls.',
                'price': 299.99,
                'original_price': 399.99,
                'category': 'Electronics',
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop',
                'stock': 45,
                'specs': json.dumps({
                    'Brand': 'SoundMax',
                    'Battery': '30 hours',
                    'Bluetooth': '5.2',
                    'Weight': '250g',
                    'Noise Cancellation': 'Active'
                })
            },
            {
                'name': 'Smart Fitness Watch Pro',
                'description': 'Advanced fitness tracking smartwatch with heart rate monitor, GPS, blood oxygen sensor, and 14-day battery life. Water resistant to 50m with AMOLED display.',
                'price': 249.99,
                'original_price': 329.99,
                'category': 'Electronics',
                'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
                'stock': 30,
                'specs': json.dumps({
                    'Display': '1.4" AMOLED',
                    'Battery': '14 days',
                    'Water Resistance': '50m',
                    'Sensors': 'HR, SpO2, GPS',
                    'OS': 'FitOS 4.0'
                })
            },
            {
                'name': 'Ultra-Slim Laptop 15"',
                'description': 'Powerful ultra-slim laptop with 15.6" 4K display, Intel i7 processor, 16GB RAM, 512GB SSD. Perfect for professionals, with Thunderbolt 4 ports and all-day battery.',
                'price': 1299.99,
                'original_price': 1499.99,
                'category': 'Electronics',
                'image_url': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=400&fit=crop',
                'stock': 15,
                'specs': json.dumps({
                    'Processor': 'Intel Core i7-13700H',
                    'RAM': '16 GB DDR5',
                    'Storage': '512 GB NVMe SSD',
                    'Display': '15.6" 4K IPS',
                    'Battery': '12 hours'
                })
            },
            {
                'name': 'Organic Cotton T-Shirt',
                'description': 'Premium organic cotton crew-neck t-shirt with a relaxed fit. Sustainably sourced and ethically manufactured. Available in multiple colors.',
                'price': 34.99,
                'original_price': 49.99,
                'category': 'Clothing',
                'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop',
                'stock': 120,
                'specs': json.dumps({
                    'Material': '100% Organic Cotton',
                    'Fit': 'Relaxed',
                    'Care': 'Machine Washable',
                    'Origin': 'Fair Trade Certified'
                })
            },
            {
                'name': 'Classic Denim Jacket',
                'description': 'Timeless denim jacket crafted from premium selvage denim. Features button closure, chest pockets, and a comfortable fit that looks great with anything.',
                'price': 89.99,
                'original_price': 129.99,
                'category': 'Clothing',
                'image_url': 'https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=400&h=400&fit=crop',
                'stock': 60,
                'specs': json.dumps({
                    'Material': 'Premium Selvage Denim',
                    'Fit': 'Regular',
                    'Closure': 'Button',
                    'Pockets': '4'
                })
            },
            {
                'name': 'Running Shoes Air Boost',
                'description': 'Lightweight running shoes with responsive cushioning and breathable mesh upper. Features our proprietary AirBoost technology for maximum energy return.',
                'price': 149.99,
                'original_price': 189.99,
                'category': 'Footwear',
                'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop',
                'stock': 80,
                'specs': json.dumps({
                    'Type': 'Running',
                    'Sole': 'AirBoost Cushion',
                    'Upper': 'Breathable Mesh',
                    'Weight': '280g',
                    'Drop': '10mm'
                })
            },
            {
                'name': 'Stainless Steel Water Bottle',
                'description': 'Double-wall vacuum insulated water bottle keeps drinks cold for 24h or hot for 12h. BPA-free, leak-proof cap with one-hand operation. 750ml capacity.',
                'price': 29.99,
                'original_price': 39.99,
                'category': 'Home & Kitchen',
                'image_url': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400&h=400&fit=crop',
                'stock': 200,
                'specs': json.dumps({
                    'Capacity': '750ml',
                    'Material': '18/8 Stainless Steel',
                    'Insulation': 'Double-Wall Vacuum',
                    'BPA Free': 'Yes',
                    'Weight': '350g'
                })
            },
            {
                'name': 'Wireless Bluetooth Speaker',
                'description': 'Portable Bluetooth speaker with 360° surround sound, IP67 waterproof rating, and 20-hour battery. Perfect for outdoor adventures and pool parties.',
                'price': 79.99,
                'original_price': 119.99,
                'category': 'Electronics',
                'image_url': 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop',
                'stock': 55,
                'specs': json.dumps({
                    'Output': '30W',
                    'Battery': '20 hours',
                    'Waterproof': 'IP67',
                    'Bluetooth': '5.3',
                    'Weight': '680g'
                })
            },
            {
                'name': 'Leather Messenger Bag',
                'description': 'Handcrafted full-grain leather messenger bag with padded laptop compartment, multiple organisers, and adjustable shoulder strap. Ages beautifully with use.',
                'price': 179.99,
                'original_price': 249.99,
                'category': 'Accessories',
                'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=400&fit=crop',
                'stock': 25,
                'specs': json.dumps({
                    'Material': 'Full-Grain Leather',
                    'Laptop Fit': 'Up to 15"',
                    'Pockets': '6 compartments',
                    'Strap': 'Adjustable',
                    'Handcrafted': 'Yes'
                })
            },
            {
                'name': 'Ceramic Pour-Over Coffee Set',
                'description': 'Artisan ceramic pour-over coffee dripper set with carafe and reusable stainless steel filter. Makes the perfect cup of coffee every time.',
                'price': 54.99,
                'original_price': 74.99,
                'category': 'Home & Kitchen',
                'image_url': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&h=400&fit=crop',
                'stock': 40,
                'specs': json.dumps({
                    'Material': 'Ceramic + Glass',
                    'Capacity': '600ml',
                    'Filter': 'Reusable Steel Mesh',
                    'Dishwasher Safe': 'Yes'
                })
            },
            {
                'name': 'Yoga Mat Premium',
                'description': 'Extra thick (6mm) yoga mat with non-slip surface, alignment lines, and carrying strap. Made from eco-friendly TPE material. Perfect for all yoga styles.',
                'price': 44.99,
                'original_price': 64.99,
                'category': 'Sports & Fitness',
                'image_url': 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400&h=400&fit=crop',
                'stock': 90,
                'specs': json.dumps({
                    'Thickness': '6mm',
                    'Material': 'Eco TPE',
                    'Size': '183 x 61 cm',
                    'Non-Slip': 'Both Sides',
                    'Weight': '1.2kg'
                })
            },
            {
                'name': 'Minimalist Analog Watch',
                'description': 'Elegant minimalist watch with Swiss quartz movement, sapphire crystal glass, and genuine leather strap. Water resistant to 30m. A timeless accessory.',
                'price': 199.99,
                'original_price': 279.99,
                'category': 'Accessories',
                'image_url': 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400&h=400&fit=crop',
                'stock': 20,
                'specs': json.dumps({
                    'Movement': 'Swiss Quartz',
                    'Crystal': 'Sapphire',
                    'Case': '40mm Stainless Steel',
                    'Strap': 'Genuine Leather',
                    'Water Resistance': '30m'
                })
            },
            {
                'name': 'Smart Home LED Bulb Pack (4)',
                'description': 'Wi-Fi enabled smart LED bulbs with 16 million colors, voice control compatibility (Alexa/Google), tunable white, and energy-saving 9W design.',
                'price': 39.99,
                'original_price': 59.99,
                'category': 'Home & Kitchen',
                'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400&h=400&fit=crop',
                'stock': 150,
                'specs': json.dumps({
                    'Wattage': '9W (60W equivalent)',
                    'Colors': '16 Million',
                    'Voice Control': 'Alexa, Google',
                    'Connectivity': 'Wi-Fi',
                    'Pack': '4 Bulbs'
                })
            },
            {
                'name': 'Professional Camera Backpack',
                'description': 'Dedicated camera backpack with customizable dividers, rain cover, tripod holder, and laptop sleeve. Fits 2 camera bodies and 6 lenses comfortably.',
                'price': 119.99,
                'original_price': 169.99,
                'category': 'Accessories',
                'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=400&fit=crop',
                'stock': 35,
                'specs': json.dumps({
                    'Capacity': '25L',
                    'Camera Fit': '2 Bodies + 6 Lenses',
                    'Laptop Sleeve': 'Up to 15"',
                    'Rain Cover': 'Included',
                    'Weight': '1.5kg'
                })
            },
            {
                'name': 'Resistance Band Set',
                'description': 'Complete set of 5 resistance bands with different levels (extra light to extra heavy). Includes door anchor, ankle straps, and carrying bag.',
                'price': 24.99,
                'original_price': 39.99,
                'category': 'Sports & Fitness',
                'image_url': 'https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=400&h=400&fit=crop',
                'stock': 110,
                'specs': json.dumps({
                    'Bands': '5 Levels',
                    'Material': 'Natural Latex',
                    'Accessories': 'Door Anchor, Ankle Straps',
                    'Bag': 'Included',
                    'Max Resistance': '150 lbs'
                })
            },
            {
                'name': 'Bamboo Cutting Board Set',
                'description': 'Set of 3 premium bamboo cutting boards in different sizes. Features juice grooves, easy-grip handles, and natural antibacterial properties.',
                'price': 34.99,
                'original_price': 49.99,
                'category': 'Home & Kitchen',
                'image_url': 'https://images.unsplash.com/photo-1594226801341-41427b4e5c22?w=400&h=400&fit=crop',
                'stock': 75,
                'specs': json.dumps({
                    'Material': 'Organic Bamboo',
                    'Set': '3 Sizes (S, M, L)',
                    'Features': 'Juice Grooves',
                    'Antibacterial': 'Natural',
                    'Care': 'Hand Wash'
                })
            },
        ]

        for pdata in products_data:
            if not Product.query.filter_by(name=pdata['name']).first():
                p = Product(**pdata)
                db.session.add(p)

        db.session.commit()
        print("✅ Database seeded successfully!")
        print(f"   - Admin: admin@shop.com / admin123")
        print(f"   - Demo:  demo@shop.com / demo123")
        print(f"   - {len(products_data)} products across multiple categories")


if __name__ == '__main__':
    seed()
