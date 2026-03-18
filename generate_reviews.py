import os
import json
import random
import time
from datetime import datetime, timedelta
import google.generativeai as genai

from app import app, db
from models import Product, User, Review

# Ensure API Key is available
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Please set GEMINI_API_KEY environment variable. Run: set GEMINI_API_KEY=your_key")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

def generate_reviews_for_product(product, users):
    """Generates 2 fake reviews for a given product."""
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
You are an AI generating realistic e-commerce customer reviews.
Product Name: {product.name}
Category: {product.category}
Description: {product.description[:150]}...

Write exactly 2 realistic, distinct reviews for this product from different types of customers. 
Include the star rating (1-5). Most should be 4 or 5 stars, but vary them slightly.
Output ONLY strict JSON in the following format (no markdown blocks, no backticks, strictly parseable JSON text):

[
  {{"rating": 5, "comment": "This is an amazing product..."}},
  {{"rating": 4, "comment": "Good quality, but..."}}
]
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.replace('```json', '').replace('```', '').strip()
        reviews_data = json.loads(text)
        
        for r_data in reviews_data:
            user = random.choice(users)
            # Random date within the last 30 days
            random_days_ago = random.randint(1, 30)
            created_at = datetime.utcnow() - timedelta(days=random_days_ago)
            
            review = Review(
                user_id=user.id,
                product_id=product.id,
                rating=r_data.get('rating', 5),
                comment=r_data.get('comment', ''),
                created_at=created_at
            )
            db.session.add(review)
            
    except Exception as e:
        print(f"Error generating reviews for {product.name}: {e}")

def run():
    with app.app_context():
        # Clear existing reviews just in case
        Review.query.delete()
        db.session.commit()
        
        products = Product.query.all()
        users = User.query.all()
        
        if not users or not products:
            print("Database empty. Please seed first.")
            return

        print(f"Generating reviews for {len(products)} products...")
        
        for i, product in enumerate(products):
            print(f"Processing ({i+1}/{len(products)}): {product.name}")
            generate_reviews_for_product(product, users)
            # sleep to avoid hitting API rate limits
            time.sleep(2)
            
        db.session.commit()
        print("Successfully generated AI Customer Reviews!")

if __name__ == '__main__':
    run()
