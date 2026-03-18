# Trenzia — AI-Powered E-Commerce Platform 🛍️

A fully-featured, AI-driven e-commerce web application built with Flask and powered by Google Gemini AI.

## ✨ Features

### 🛒 Shopping Experience
- **Dynamic Shopping Cart** — AJAX-powered sidebar cart with real-time updates
- **Smart Search & Filtering** — Category, price range, and sort-by-rating filters
- **Product Comparison** — Compare up to 4 products side by side
- **Wishlist** — Save products for later

### 🤖 AI-Powered Features
- **AI Chatbot Assistant** — Natural language shopping assistant that can:
  - Search products by name or category
  - Track your orders in real-time (*"Where is my jacket?"*)
  - Add items to cart via chat
  - Raise support tickets
  - Negotiate prices and generate coupon codes
  - Act as a Gift Concierge
- **AI Style Profile Builder** — "Style DNA" quiz for personalized recommendations
- **AI Goal Shopper** — Describe a goal, AI builds the perfect cart with budget
- **AI Size Predictor** — Height/weight-based size recommendations for clothing
- **AI Price Negotiation (Haggling)** — Negotiate discounts with an AI seller
- **AI Personalized Descriptions** — Product descriptions tailored to your preferences
- **AI Customer Reviews** — Gemini-generated authentic product reviews
- **Vibe / Aesthetic Search** — Find products by mood/aesthetic (e.g. "cozy minimalist")
- **Visual Search** — Upload a photo to find matching products
- **Product Compatibility Check** — Checks if products work with your owned devices

### 🎯 Gamification & Loyalty
- **Logic Points System** — Earn 1 point per ₹10 spent, redeem at checkout
- **AI Coupon Codes** — Dynamic discount coupons from haggling
- **Gamified Order Tracking** — Animated real-time order progress pipeline

### 🥽 Immersive Visualization
- **AR Product Viewer** — View products in Augmented Reality on mobile
- **3D Model Viewer** — Interactive 3D product visualization
- **Virtual Try-On** — AI-powered style analysis with selfie upload

### 👨‍💼 Admin Dashboard
- Product management (Add/Edit/Delete)
- Revenue analytics and KPIs
- Support ticket management
- Low stock alerts and top-selling products

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A [Google Gemini API Key](https://aistudio.google.com/)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-ecommerce.git
cd ai-ecommerce

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Create a .env file in the project root:
echo GEMINI_API_KEY=your_gemini_api_key_here > .env

# 5. Seed the database with products and users
python seed_data.py

# 6. Run the application
python app.py
```

Visit `http://localhost:5000` in your browser.

### Demo Accounts
After seeding, you can log in with:
- **Email:** `demo@shop.com` / **Password:** `demo123`
- **Email:** `testuser@example.com` / **Password:** `password123`

### Generating AI Reviews (Optional)
```bash
python generate_reviews.py
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Flask, Flask-SQLAlchemy, Flask-Login |
| **Database** | SQLite (via SQLAlchemy ORM) |
| **AI / ML** | Google Gemini API (`google-generativeai`) |
| **Frontend** | HTML5, Vanilla CSS, Tailwind CSS (CDN), JavaScript |
| **3D / AR** | Google `<model-viewer>`, WebXR |
| **Auth** | Werkzeug password hashing, Flask-Login sessions |

---

## 📁 Project Structure

```
ai-ecommerce/
├── app.py              # Main Flask application & all routes
├── models.py           # SQLAlchemy database models
├── seed_data.py        # Database seeder (users + products)
├── generate_reviews.py # AI review generator script
├── requirements.txt    # Python dependencies
├── static/
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   ├── images/         # Product images
│   └── models/         # 3D GLB model files for AR
└── templates/          # Jinja2 HTML templates
    ├── base.html
    ├── index.html
    ├── shop.html
    ├── product.html
    ├── cart.html
    ├── checkout.html
    ├── orders.html
    ├── profile.html
    ├── admin.html
    └── ...
```

---

## ⚙️ Environment Variables

| Variable | Description | Required |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key for all AI features | Yes |

> ⚠️ **Never commit your `.env` file to version control!**

---

## 📸 Screenshots

*(Add screenshots here after deployment)*

---

## 📄 License

MIT License — feel free to use this project for learning and portfolio purposes.
