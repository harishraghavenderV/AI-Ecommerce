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

    # Seed products from seed_products.py
    try:
        import seed_products
        seed_products.run()
    except Exception as e:
        print(f"Product seeding error: {e}", flush=True)

# Vercel Python runtime requires the app exposed as a module-level callable named 'app'
# Do NOT rename to 'handler' - that causes TypeError: issubclass() arg 1 must be a class
