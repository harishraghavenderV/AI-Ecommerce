"""
Vercel WSGI entry point for the Trenzia Flask app.
Vercel runs this as a serverless function.
"""
import sys
import os

# Add parent directory to path so we can import app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Auto-seed database on cold start if empty
from models import db, Product, User
with app.app_context():
    db.create_all()
    if Product.query.count() == 0:
        # Import and run the seed function
        try:
            from seed_data import seed
            seed()
            print("Database seeded successfully on Vercel cold start.", flush=True)
        except Exception as e:
            print(f"Seeding error: {e}", flush=True)

# Vercel expects the WSGI app to be called 'app' or 'handler'
handler = app
