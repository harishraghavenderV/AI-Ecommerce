"""
Vercel WSGI entry point for the Trenzia Flask app.
Vercel runs this as a serverless function.
"""
import sys
import os

# Add parent directory to path so we can import app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Execute database seeding AT RUNTIME on the first request, 
# NOT at module-level, to prevent crashing the Vercel builder during test imports.
@app.before_request
def auto_seed_vercel_db():
    if not hasattr(app, '_vercel_seeded'):
        from models import db, Product
        db.create_all()
        if Product.query.count() == 0:
            try:
                from seed_data import seed
                seed()
                print("Database seeded successfully on Vercel cold start.", flush=True)
            except Exception as e:
                print(f"Seeding error: {e}", flush=True)
        app._vercel_seeded = True

app.before_request_funcs.setdefault(None, []).append(auto_seed_vercel_db)

# Vercel expects the WSGI app to be called 'app' or 'handler'
handler = app
