"""
Vercel WSGI entry point for the Trenzia Flask app.
"""
import sys
import os

# Add parent directory to path so we can import app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db

# Create tables and seed on the very first request (Vercel cold start)
_is_initialized = False

@app.before_request
def init_db_once():
    global _is_initialized
    if _is_initialized:
        return
    _is_initialized = True
    try:
        db.create_all()
        from models import Product, User
        if Product.query.count() == 0:
            # Import seed data inline to avoid circular imports
            from seed_data import seed
            # seed() calls app.app_context() internally, so just call the inner logic instead
            _seed_inline()
        print("Vercel DB ready.", flush=True)
    except Exception as e:
        print(f"Vercel DB init error: {e}", flush=True)


def _seed_inline():
    """Seed users and products directly without opening a new app_context."""
    from models import User, Product
    from werkzeug.security import generate_password_hash
    import json

    if not User.query.filter_by(email='admin@shop.com').first():
        admin = User(
            username='admin',
            email='admin@shop.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            addresses=json.dumps([{
                'label': 'Office', 'street': '123 Admin St',
                'city': 'Tech City', 'state': 'CA', 'zip': '90001', 'phone': '555-0100'
            }])
        )
        db.session.add(admin)

    if not User.query.filter_by(email='demo@shop.com').first():
        demo = User(
            username='demo',
            email='demo@shop.com',
            password_hash=generate_password_hash('demo123'),
            is_admin=False,
            addresses=json.dumps([{
                'label': 'Home', 'street': '456 Main Ave',
                'city': 'Sample Town', 'state': 'NY', 'zip': '10001', 'phone': '555-0200'
            }])
        )
        db.session.add(demo)

    db.session.commit()

    # Import product data from seed_products.py which has full product list
    try:
        import seed_products
        seed_products.run()
    except Exception as e:
        print(f"Product seeding error: {e}", flush=True)
        # Fallback: seed a few basic products so the site has content
        products = [
            {'name': 'iPhone 15 Pro Max', 'description': 'Apple flagship smartphone with titanium design', 'price': 1349.99, 'original_price': 1499.99, 'category': 'Smartphones', 'stock': 30, 'image_url': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop'},
            {'name': 'MacBook Pro 14"', 'description': 'M3 chip, 14-inch Liquid Retina XDR display', 'price': 1999.99, 'original_price': 2199.99, 'category': 'Laptops', 'stock': 15, 'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&h=400&fit=crop'},
            {'name': 'Sony WH-1000XM5', 'description': 'Industry-leading noise canceling headphones', 'price': 299.99, 'original_price': 399.99, 'category': 'Electronics', 'stock': 49, 'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop'},
        ]
        for p in products:
            prod = Product(**p, specs='{}')
            db.session.add(prod)
        db.session.commit()


# Vercel expects the WSGI app exposed as 'app' or 'handler'
handler = app
