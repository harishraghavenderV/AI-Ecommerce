from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session

from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Product, CartItem, WishlistItem, Order, OrderItem, Review, Coupon

from datetime import datetime

import json

import os

import socket

import random

from dotenv import load_dotenv

import google.generativeai as genai



load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:

    genai.configure(api_key=GEMINI_API_KEY)



app = Flask(__name__)

# Vercel has a read-only filesystem; use /tmp for SQLite.
# Locally, the db sits in the instance/ folder as normal.
IS_VERCEL = os.environ.get('VERCEL', False)
if IS_VERCEL:
    DB_PATH = '/tmp/ecommerce.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ai-ecommerce-secret-key-2024')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db.init_app(app)

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'login'





def _get_lan_ip():

    """Get the machine's LAN IP address for QR code generation."""

    try:

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s.connect(('8.8.8.8', 80))

        ip = s.getsockname()[0]

        s.close()

        return ip

    except Exception:

        return '127.0.0.1'



_LAN_IP = _get_lan_ip()





@app.context_processor

def inject_lan_ip():

    return {'lan_ip': _LAN_IP}





@login_manager.user_loader

def load_user(user_id):

    return User.query.get(int(user_id))





@app.context_processor

def inject_cart_count():

    count = 0

    if current_user.is_authenticated:

        count = sum(item.quantity for item in current_user.cart_items)

    return dict(cart_count=count)





@app.context_processor

def inject_categories():

    categories = db.session.query(Product.category).distinct().all()

    return dict(all_categories=[c[0] for c in categories])





# ─── HOME ───────────────────────────────────────────────

@app.route('/')

def index():

    featured = Product.query.order_by(Product.created_at.desc()).limit(8).all()

    categories = db.session.query(Product.category).distinct().all()

    categories = [c[0] for c in categories]

    top_rated = Product.query.all()

    top_rated = sorted(top_rated, key=lambda p: p.avg_rating, reverse=True)[:4]

    return render_template('index.html', featured=featured, categories=categories, top_rated=top_rated)





# ─── AUTH ────────────────────────────────────────────────

@app.route('/auth/login', methods=['GET', 'POST'])

def login():

    if current_user.is_authenticated:

        return redirect(url_for('index'))

    if request.method == 'POST':

        email = request.form.get('email', '').strip()

        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):

            login_user(user)

            flash('Welcome back!', 'success')

            next_page = request.args.get('next')

            return redirect(next_page or url_for('index'))

        flash('Invalid email or password.', 'error')

    return render_template('login.html')





@app.route('/auth/register', methods=['GET', 'POST'])

def register():

    if current_user.is_authenticated:

        return redirect(url_for('index'))

    if request.method == 'POST':

        username = request.form.get('username', '').strip()

        email = request.form.get('email', '').strip()

        password = request.form.get('password', '')

        confirm = request.form.get('confirm_password', '')



        if password != confirm:

            flash('Passwords do not match.', 'error')

            return render_template('register.html')

        if User.query.filter_by(email=email).first():

            flash('Email already registered.', 'error')

            return render_template('register.html')

        if User.query.filter_by(username=username).first():

            flash('Username already taken.', 'error')

            return render_template('register.html')



        user = User(

            username=username,

            email=email,

            password_hash=generate_password_hash(password)

        )

        db.session.add(user)

        db.session.commit()

        login_user(user)

        flash('Account created successfully!', 'success')

        return redirect(url_for('index'))

    return render_template('register.html')





@app.route('/auth/logout')

@login_required

def logout():

    logout_user()

    flash('You have been logged out.', 'success')

    return redirect(url_for('index'))





# ─── PROFILE ────────────────────────────────────────────

@app.route('/profile', methods=['GET', 'POST'])

@login_required

def profile():

    if request.method == 'POST':

        action = request.form.get('action')

        if action == 'update_profile':

            current_user.username = request.form.get('username', current_user.username)

            current_user.email = request.form.get('email', current_user.email)

            db.session.commit()

            flash('Profile updated!', 'success')

        elif action == 'add_address':

            addresses = json.loads(current_user.addresses or '[]')

            new_addr = {

                'label': request.form.get('label', 'Home'),

                'street': request.form.get('street', ''),

                'city': request.form.get('city', ''),

                'state': request.form.get('state', ''),

                'zip': request.form.get('zip', ''),

                'phone': request.form.get('phone', '')

            }

            addresses.append(new_addr)

            current_user.addresses = json.dumps(addresses)

            db.session.commit()

            flash('Address added!', 'success')

        elif action == 'delete_address':

            idx = int(request.form.get('address_index', -1))

            addresses = json.loads(current_user.addresses or '[]')

            if 0 <= idx < len(addresses):

                addresses.pop(idx)

                current_user.addresses = json.dumps(addresses)

                db.session.commit()

                flash('Address removed.', 'success')

        return redirect(url_for('profile'))

    addresses = json.loads(current_user.addresses or '[]')

    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()

    return render_template('profile.html', addresses=addresses, orders=orders)





# ─── SHOP ────────────────────────────────────────────────

@app.route('/shop')

def shop():

    category = request.args.get('category', '')

    sort_by = request.args.get('sort', 'newest')

    min_price = request.args.get('min_price', type=float)

    max_price = request.args.get('max_price', type=float)

    search_q = request.args.get('q', '')



    query = Product.query

    if category:

        query = query.filter_by(category=category)

    if min_price is not None:

        query = query.filter(Product.price >= min_price)

    if max_price is not None:

        query = query.filter(Product.price <= max_price)

    if search_q:

        query = query.filter(

            db.or_(

                Product.name.ilike(f'%{search_q}%'),

                Product.description.ilike(f'%{search_q}%'),

                Product.category.ilike(f'%{search_q}%')

            )

        )



    if sort_by == 'price_low':

        query = query.order_by(Product.price.asc())

    elif sort_by == 'price_high':

        query = query.order_by(Product.price.desc())

    elif sort_by == 'name':

        query = query.order_by(Product.name.asc())

    else:

        query = query.order_by(Product.created_at.desc())



    products = query.all()

    if sort_by == 'rating':

        products = sorted(products, key=lambda p: p.avg_rating, reverse=True)



    categories = db.session.query(Product.category).distinct().all()

    categories = [c[0] for c in categories]



    wishlist_ids = []

    compare_ids = session.get('compare_ids', [])

    if current_user.is_authenticated:

        wishlist_ids = [w.product_id for w in current_user.wishlist_items]



    return render_template('shop.html', products=products, categories=categories,

                           current_category=category, current_sort=sort_by,

                           min_price=min_price, max_price=max_price, search_q=search_q,

                           wishlist_ids=wishlist_ids, compare_ids=compare_ids)





# ─── PRODUCT DETAIL ─────────────────────────────────────

@app.route('/product/<int:product_id>')

def product_detail(product_id):

    product = Product.query.get_or_404(product_id)

    specs = json.loads(product.specs or '{}')

    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()



    # AI Recommendation: category-based suggestions

    related = Product.query.filter(

        Product.category == product.category,

        Product.id != product.id

    ).limit(4).all()



    # Frequently bought together (simulated AI logic)

    all_products = Product.query.filter(Product.id != product.id).all()

    bought_together = random.sample(all_products, min(3, len(all_products)))



    in_wishlist = False

    user_reviewed = False

    if current_user.is_authenticated:

        in_wishlist = WishlistItem.query.filter_by(

            user_id=current_user.id, product_id=product_id

        ).first() is not None

        user_reviewed = Review.query.filter_by(

            user_id=current_user.id, product_id=product_id

        ).first() is not None

    # ── Resolve GLB model URL ─────────────────────────────────

    # Priority: 1) product-specific GLB  2) category fallback GLB

    CATEGORY_GLB = {

        'Electronics': 'models/cat_electronics.glb',

        'Clothing':    'models/cat_clothing.glb',

        'Footwear':    'models/cat_footwear.glb',

        'Accessories': 'models/cat_accessories.glb',

        'Home & Kitchen': 'models/cat_home.glb',

        'Sports & Fitness': 'models/cat_sports.glb',

        'Furniture':   'models/cat_home.glb',

    }



    product_glb = os.path.join(app.static_folder, 'models', f'{product_id}.glb')

    if os.path.exists(product_glb):

        glb_url = url_for('static', filename=f'models/{product_id}.glb')

    else:

        # Use a category-representative GLB so AR always works

        cat_key = CATEGORY_GLB.get(product.category, 'models/cat_electronics.glb')

        glb_url = url_for('static', filename=cat_key)



    return render_template('product.html', product=product, specs=specs, reviews=reviews,

                           related=related, bought_together=bought_together,

                           in_wishlist=in_wishlist, user_reviewed=user_reviewed,

                           glb_model_url=glb_url)





# ─── REVIEWS ────────────────────────────────────────────

@app.route('/product/<int:product_id>/review', methods=['POST'])

@login_required

def add_review(product_id):

    existing = Review.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if existing:

        flash('You have already reviewed this product.', 'error')

        return redirect(url_for('product_detail', product_id=product_id))

    rating = int(request.form.get('rating', 5))

    comment = request.form.get('comment', '')

    review = Review(user_id=current_user.id, product_id=product_id, rating=rating, comment=comment)

    db.session.add(review)

    db.session.commit()

    flash('Review submitted!', 'success')

    return redirect(url_for('product_detail', product_id=product_id))





# ─── CART API ────────────────────────────────────────────

@app.route('/api/cart/add', methods=['POST'])

@login_required

def cart_add():

    data = request.get_json()

    product_id = data.get('product_id')

    quantity = data.get('quantity', 1)

    product = Product.query.get(product_id)

    if not product:

        return jsonify({'error': 'Product not found'}), 404



    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if item:

        item.quantity += quantity

    else:

        item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)

        db.session.add(item)

    db.session.commit()

    count = sum(i.quantity for i in current_user.cart_items)

    return jsonify({'success': True, 'cart_count': count})





@app.route('/api/cart/update', methods=['POST'])

@login_required

def cart_update():

    data = request.get_json()

    item_id = data.get('item_id')

    action = data.get('action')



    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()

    if not item:

        return jsonify({'error': 'Item not found'}), 404



    if action == 'increase':

        item.quantity += 1

    elif action == 'decrease':

        item.quantity -= 1

        if item.quantity <= 0:

            db.session.delete(item)

    elif action == 'remove':

        db.session.delete(item)



    db.session.commit()



    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    total = sum(ci.product.price * ci.quantity for ci in cart_items)

    count = sum(ci.quantity for ci in cart_items)

    return jsonify({'success': True, 'total': round(total, 2), 'cart_count': count})





@app.route('/cart')

@login_required

def cart():

    items = CartItem.query.filter_by(user_id=current_user.id).all()

    total = sum(item.product.price * item.quantity for item in items)

    return render_template('cart.html', items=items, total=round(total, 2))





# ─── WISHLIST API ────────────────────────────────────────

@app.route('/api/wishlist/toggle', methods=['POST'])

@login_required

def wishlist_toggle():

    data = request.get_json()

    product_id = data.get('product_id')

    existing = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if existing:

        db.session.delete(existing)

        db.session.commit()

        return jsonify({'success': True, 'action': 'removed'})

    else:

        item = WishlistItem(user_id=current_user.id, product_id=product_id)

        db.session.add(item)

        db.session.commit()

        return jsonify({'success': True, 'action': 'added'})





@app.route('/wishlist')

@login_required

def wishlist():

    items = WishlistItem.query.filter_by(user_id=current_user.id).all()

    return render_template('wishlist.html', items=items)





# ─── SEARCH API ─────────────────────────────────────────

@app.route('/api/search')

def api_search():

    q = request.args.get('q', '').strip()

    if len(q) < 2:

        return jsonify([])



    keywords = q.lower().split()

    products = Product.query.all()

    results = []

    for p in products:

        score = 0

        text = f"{p.name} {p.description} {p.category}".lower()

        for kw in keywords:

            if kw in p.name.lower():

                score += 10

            if kw in p.category.lower():

                score += 5

            if kw in p.description.lower():

                score += 2

        if score > 0:

            results.append({

                'id': p.id,

                'name': p.name,

                'category': p.category,

                'price': p.price,

                'image_url': p.image_url,

                'score': score

            })

    results.sort(key=lambda x: x['score'], reverse=True)

    return jsonify(results[:10])





# ─── CHECKOUT ────────────────────────────────────────────

@app.route('/checkout', methods=['GET', 'POST'])

@login_required

def checkout():

    items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not items:

        flash('Your cart is empty.', 'error')

        return redirect(url_for('cart'))



    total = sum(item.product.price * item.quantity for item in items)

    addresses = json.loads(current_user.addresses or '[]')



    if request.method == 'POST':

        address_idx = int(request.form.get('address_index', 0))

        payment_method = request.form.get('payment_method', 'Card')

        coupon_code = request.form.get('coupon_code', '').strip()



        if not addresses:

            flash('Please add an address in your profile first.', 'error')

            return redirect(url_for('profile'))



        selected_address = addresses[min(address_idx, len(addresses) - 1)]



        # Apply coupon discount

        discount = 0

        if coupon_code:

            coupon = Coupon.query.filter_by(code=coupon_code, user_id=current_user.id, used=False).first()

            if coupon and coupon.expires_at > datetime.utcnow():

                discount = round(total * coupon.discount_percent / 100, 2)

                total = round(total - discount, 2)

                coupon.used = True

            else:

                flash('Invalid or expired coupon code.', 'error')

                return render_template('checkout.html', items=items, total=round(total, 2), addresses=addresses)



        # Apply Logic Points discount

        use_points = request.form.get('use_points') == 'on'

        if use_points and current_user.loyalty_points > 0:

            points_value = current_user.loyalty_points * 1.0

            points_used_value = min(points_value, total)

            points_used = int(points_used_value)

            current_user.loyalty_points -= points_used

            total = round(total - points_used_value, 2)



        # Include 8% tax in total for the order receipt to make it accurate to UI

        total = round(total * 1.08, 2)



        order = Order(

            user_id=current_user.id,

            total=total,

            status='Confirmed',

            payment_method=payment_method,

            address=json.dumps(selected_address)

        )

        db.session.add(order)

        db.session.flush()



        for item in items:

            oi = OrderItem(

                order_id=order.id,

                product_id=item.product_id,

                quantity=item.quantity,

                price=item.product.price

            )

            db.session.add(oi)

            if item.product.stock >= item.quantity:

                item.product.stock -= item.quantity



        CartItem.query.filter_by(user_id=current_user.id).delete()

        

        # Award loyalty points (e.g., 1 point per 10 rupees)

        earned_points = int(total // 10)

        current_user.loyalty_points += earned_points

        

        db.session.commit()

        flash('Order placed successfully!', 'success')

        return redirect(url_for('order_confirmation', order_id=order.id))



    return render_template('checkout.html', items=items, total=round(total, 2), addresses=addresses)





@app.route('/order/<int:order_id>/confirmation')

@login_required

def order_confirmation(order_id):

    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id:

        flash('Unauthorized.', 'error')

        return redirect(url_for('index'))

    address = json.loads(order.address)

    return render_template('order_confirmation.html', order=order, address=address)





def sync_user_orders(user_id):

    orders_list = Order.query.filter_by(user_id=user_id).all()

    now = datetime.utcnow()

    updated = False

    for order in orders_list:

        if order.status == 'Delivered':

            continue

        elapsed = (now - order.created_at).total_seconds()

        if elapsed >= 180:

            order.status = 'Delivered'

            updated = True

        elif elapsed >= 120 and order.status != 'Shipped':

            order.status = 'Shipped'

            updated = True

        elif elapsed >= 60 and order.status == 'Confirmed':

            order.status = 'Packed'

            updated = True

    if updated:

        db.session.commit()



# ─── ORDERS ─────────────────────────────────────────────

@app.route('/orders')

@login_required

def orders():

    sync_user_orders(current_user.id)

    sort = request.args.get('sort', 'newest')

    query = Order.query.filter_by(user_id=current_user.id)

    if sort == 'oldest':

        query = query.order_by(Order.created_at.asc())

    else:

        query = query.order_by(Order.created_at.desc())

    user_orders = query.all()

    

    # Calculate progress widths for initial render

    now = datetime.utcnow()

    order_progress = {}

    for o in user_orders:

        elapsed = (now - o.created_at).total_seconds()

        perc = min((elapsed / 180.0) * 100, 100) if elapsed > 0 else 0

        order_progress[o.id] = f"{perc:.1f}%"

        

    return render_template('orders.html', orders=user_orders, current_sort=sort, progress=order_progress)



@app.route('/api/orders/status')

@login_required

def api_orders_status():

    sync_user_orders(current_user.id)

    orders_list = Order.query.filter_by(user_id=current_user.id, status='Delivered')

    # Or just returning all... let's return all active ones

    orders_list = Order.query.filter_by(user_id=current_user.id).all()

    now = datetime.utcnow()

    data = {}

    for o in orders_list:

        elapsed = (now - o.created_at).total_seconds()

        perc = min((elapsed / 180.0) * 100, 100) if elapsed > 0 else 0

        data[o.id] = {

            'status': o.status,

            'progress': f"{perc:.1f}%"

        }

    return jsonify(data)





# ─── COMPARE ────────────────────────────────────────────

@app.route('/compare/add/<int:product_id>')

def compare_add(product_id):

    compare_ids = session.get('compare_ids', [])

    if product_id not in compare_ids and len(compare_ids) < 4:

        compare_ids.append(product_id)

        session['compare_ids'] = compare_ids

    return redirect(request.referrer or url_for('shop'))





@app.route('/compare/remove/<int:product_id>')

def compare_remove(product_id):

    compare_ids = session.get('compare_ids', [])

    if product_id in compare_ids:

        compare_ids.remove(product_id)

        session['compare_ids'] = compare_ids

    return redirect(request.referrer or url_for('compare'))





@app.route('/compare')

def compare():

    compare_ids = session.get('compare_ids', [])

    products = Product.query.filter(Product.id.in_(compare_ids)).all() if compare_ids else []

    return render_template('compare.html', products=products)





# ─── ADMIN ───────────────────────────────────────────────

@app.route('/admin/tickets')

@login_required

def admin_tickets():

    if not current_user.is_admin:

        flash('Admin access required.', 'error')

        return redirect(url_for('index'))

    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()

    # Create an active map of users context

    users_dict = {u.id: u for u in User.query.all()}

    return render_template('admin_tickets.html', tickets=tickets, users_dict=users_dict)



@app.route('/admin/ticket/<int:ticket_id>/status', methods=['POST'])

@login_required

def admin_ticket_status(ticket_id):

    if not current_user.is_admin:

        return jsonify({'error': 'Unauthorized'}), 403

    ticket = Ticket.query.get_or_404(ticket_id)

    status = request.form.get('status')

    if status in ['Open', 'In Progress', 'Closed']:

        ticket.status = status

        db.session.commit()

    return redirect(url_for('admin_tickets'))



@app.route('/admin')

@login_required

def admin():

    if not current_user.is_admin:

        flash('Admin access required.', 'error')

        return redirect(url_for('index'))

    products = Product.query.all()

    total_revenue = db.session.query(db.func.sum(Order.total)).scalar() or 0

    total_orders = Order.query.count()

    total_users = User.query.count()



    # Top selling products

    top_selling = db.session.query(

        Product.name, db.func.sum(OrderItem.quantity).label('sold')

    ).join(OrderItem).group_by(Product.id).order_by(db.desc('sold')).limit(5).all()



    # Low stock alerts

    low_stock = Product.query.filter(Product.stock < 10).all()



    # Sales by category

    cat_sales = db.session.query(

        Product.category, db.func.sum(OrderItem.quantity * OrderItem.price).label('revenue')

    ).join(OrderItem).group_by(Product.category).all()



    # AI Business Insights (Mock)

    insights = [

        "📈 Electronics category shows 23% growth this month",

        "🎯 Recommended: Increase inventory for top-selling items",

        "💡 Consider bundling complementary products for better margins",

        "🔄 Customer retention rate has improved by 15%",

        "⚡ Peak shopping hours: 6 PM - 10 PM"

    ]



    return render_template('admin.html', products=products,

                           total_revenue=round(total_revenue, 2),

                           total_orders=total_orders,

                           total_users=total_users,

                           top_selling=top_selling,

                           low_stock=low_stock,

                           cat_sales=cat_sales,

                           insights=insights)





@app.route('/admin/product/add', methods=['GET', 'POST'])

@login_required

def admin_add_product():

    if not current_user.is_admin:

        flash('Admin access required.', 'error')

        return redirect(url_for('index'))

    if request.method == 'POST':

        specs_raw = request.form.get('specs', '{}')

        try:

            specs = json.loads(specs_raw)

        except json.JSONDecodeError:

            specs = {}



        product = Product(

            name=request.form.get('name'),

            description=request.form.get('description'),

            price=float(request.form.get('price', 0)),

            original_price=float(request.form.get('original_price', 0)) or None,

            category=request.form.get('category'),

            image_url=request.form.get('image_url', '/static/images/placeholder.png'),

            stock=int(request.form.get('stock', 0)),

            specs=json.dumps(specs),

            ar_model=request.form.get('ar_model', '')

        )

        db.session.add(product)

        db.session.commit()

        flash('Product added!', 'success')

        return redirect(url_for('admin'))

    return render_template('edit_product.html', product=None)





@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])

@login_required

def admin_edit_product(product_id):

    if not current_user.is_admin:

        flash('Admin access required.', 'error')

        return redirect(url_for('index'))

    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':

        product.name = request.form.get('name', product.name)

        product.description = request.form.get('description', product.description)

        product.price = float(request.form.get('price', product.price))

        product.original_price = float(request.form.get('original_price', 0)) or None

        product.category = request.form.get('category', product.category)

        product.image_url = request.form.get('image_url', product.image_url)

        product.stock = int(request.form.get('stock', product.stock))

        product.ar_model = request.form.get('ar_model', product.ar_model)

        specs_raw = request.form.get('specs', '{}')

        try:

            product.specs = json.dumps(json.loads(specs_raw))

        except json.JSONDecodeError:

            pass

        db.session.commit()

        flash('Product updated!', 'success')

        return redirect(url_for('admin'))

    return render_template('edit_product.html', product=product)





@app.route('/admin/product/delete/<int:product_id>')

@login_required

def admin_delete_product(product_id):

    if not current_user.is_admin:

        flash('Admin access required.', 'error')

        return redirect(url_for('index'))

    product = Product.query.get_or_404(product_id)

    db.session.delete(product)

    db.session.commit()

    flash('Product deleted.', 'success')

    return redirect(url_for('admin'))





# ─── MOVE WISHLIST TO CART ───────────────────────────────

@app.route('/api/wishlist/move-to-cart', methods=['POST'])

@login_required

def wishlist_move_to_cart():

    data = request.get_json()

    product_id = data.get('product_id')

    wish = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if wish:

        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

        if cart_item:

            cart_item.quantity += 1

        else:

            cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)

            db.session.add(cart_item)

        db.session.delete(wish)

        db.session.commit()

        return jsonify({'success': True})

    return jsonify({'error': 'Item not found'}), 404





# ─── VR / AR ENDPOINT ───────────────────────────────────

@app.route('/vr/<int:product_id>')

def vr_view(product_id):

    product = Product.query.get_or_404(product_id)

    return render_template('vr_viewer.html', product=product)





@app.route('/ar/<int:product_id>')

def ar_view(product_id):

    product = Product.query.get_or_404(product_id)

    # Check if a GLB model file exists for this product

    glb_path = os.path.join(app.static_folder, 'models', f'{product_id}.glb')

    glb_url = url_for('static', filename=f'models/{product_id}.glb') if os.path.exists(glb_path) else None

    return render_template('ar_viewer.html', product=product, glb_model_url=glb_url)





@app.route('/cart/add/<int:product_id>')

@login_required

def add_to_cart(product_id):

    product = Product.query.get_or_404(product_id)

    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if item:

        item.quantity += 1

    else:

        item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)

        db.session.add(item)

    db.session.commit()

    flash('Added to bag!', 'success')

    return redirect(url_for('product_detail', product_id=product_id))





# ─── PERSONALIZED DESCRIPTION ENDPOINT ─────────────────────

@app.route('/api/personalized-description/<int:product_id>')

def personalized_description(product_id):

    if not current_user.is_authenticated or not GEMINI_API_KEY:

        return jsonify({'description': None})



    product = Product.query.get_or_404(product_id)

    prefs = json.loads(current_user.preferences or '{}')

    if not prefs:

        return jsonify({'description': None})



    try:

        model = genai.GenerativeModel('gemini-2.5-flash-lite')

        prompt = f"""Rewrite this product description to match the user's preferences.



Product: {product.name}

Original Description: {product.description}

Specs: {product.specs}



User Preferences: {json.dumps(prefs)}



Rules:

- Keep it roughly the same length (2-3 sentences).

- If user prefers simple language, avoid jargon.

- If user is eco-conscious, highlight sustainability.

- If user is tech-savvy, emphasize specifications.

- Make it feel personal and tailored, not generic.

- Do NOT add any prefix like "Here's the rewritten description". Just return the description text directly."""



        response = model.generate_content(prompt)

        return jsonify({'description': response.text.strip()})

    except Exception as e:

        print(f"Personalization Error: {e}")

        return jsonify({'description': None})





# ─── COMPATIBILITY CHECK ENDPOINT ────────────────────────────

@app.route('/api/compatibility/<int:product_id>')

def compatibility_check(product_id):

    if not current_user.is_authenticated or not GEMINI_API_KEY:

        return jsonify({'status': None})



    product = Product.query.get_or_404(product_id)

    devices = json.loads(current_user.owned_devices or '[]')

    if not devices:

        return jsonify({'status': None})



    try:

        model = genai.GenerativeModel('gemini-2.5-flash-lite')

        prompt = f"""You are a product compatibility expert.



Product: {product.name}

Description: {product.description}

Specs: {product.specs}



User's owned devices: {json.dumps(devices)}



Analyze if this product is compatible with the user's devices.

Respond ONLY in this JSON format (no markdown, no code fences):

{{"status": "compatible|warning|incompatible", "message": "One short sentence explaining why", "device": "The relevant device name or null"}}



If the product category is completely unrelated to any device (e.g. clothing vs phone), respond with:

{{"status": "neutral", "message": "No compatibility concerns", "device": null}}"""



        response = model.generate_content(prompt)

        raw = response.text.strip()

        if raw.startswith('```'):

            raw = raw.split('\n', 1)[1] if '\n' in raw else raw[3:]

        if raw.endswith('```'):

            raw = raw[:-3]

        raw = raw.strip()

        if raw.startswith('json'):

            raw = raw[4:].strip()

        result = json.loads(raw)

        return jsonify(result)

    except Exception as e:

        print(f"Compatibility Error: {e}")

        return jsonify({'status': None})





# ─── USER DEVICES ENDPOINT ───────────────────────────────────

@app.route('/api/user-devices', methods=['GET', 'POST'])

@login_required

def user_devices():

    if request.method == 'POST':

        data = request.get_json()

        devices = data.get('devices', [])

        current_user.owned_devices = json.dumps(devices)

        db.session.commit()

        return jsonify({'success': True, 'devices': devices})

    

    devices = json.loads(current_user.owned_devices or '[]')

    return jsonify({'devices': devices})





# ─── USER PREFERENCES ENDPOINT ───────────────────────────────

@app.route('/api/user-preferences', methods=['GET', 'POST'])

@login_required

def user_preferences():

    if request.method == 'POST':

        data = request.get_json()

        prefs = data.get('preferences', {})

        current_user.preferences = json.dumps(prefs)

        db.session.commit()

        return jsonify({'success': True, 'preferences': prefs})

    

    prefs = json.loads(current_user.preferences or '{}')

    return jsonify({'preferences': prefs})





# ─── VIRTUAL TRY-ON ENDPOINT ──────────────────────────────

@app.route('/api/virtual-tryon', methods=['POST'])

@login_required

def virtual_tryon():

    if not GEMINI_API_KEY:

        return jsonify({'error': 'Virtual try-on is unavailable'}), 503



    if 'selfie' not in request.files:

        return jsonify({'error': 'Please upload a selfie'}), 400



    product_id = request.form.get('product_id')

    if not product_id:

        return jsonify({'error': 'Product ID is required'}), 400



    product = Product.query.get(int(product_id))

    if not product:

        return jsonify({'error': 'Product not found'}), 404



    selfie = request.files['selfie']

    import io

    selfie_bytes = selfie.read()



    try:

        model = genai.GenerativeModel('gemini-2.5-flash-lite')

        prompt = f"""You are a fashion and styling expert. The user has uploaded a selfie and wants to know how the following product would look on them.



Product: {product.name}

Category: {product.category}

Description: {product.description}



Based on the selfie and the product details:

1. Describe how this product would look on this person (complexion, build, style match).

2. Suggest what to pair it with.

3. Give an overall styling verdict (Great Match / Good Fit / Consider Alternatives).

4. Rate the style match out of 10.



Be enthusiastic, specific, and helpful. Use 3-4 concise paragraphs. Format with emoji."""



        import PIL.Image

        img = PIL.Image.open(io.BytesIO(selfie_bytes))

        response = model.generate_content([prompt, img])



        return jsonify({'result': response.text.strip()})

    except Exception as e:

        import traceback

        print(f"Virtual Try-On Error:\n{traceback.format_exc()}")

        return jsonify({'error': 'Failed to process virtual try-on. Please try again.'}), 500





# ─── VIBE / AESTHETIC MATCHER ENDPOINT ────────────────────

@app.route('/api/vibe-search', methods=['POST'])

def vibe_search():

    if not GEMINI_API_KEY:

        return jsonify({'error': 'Vibe search is unavailable (missing API key)'}), 503



    data = request.get_json()

    vibe_text = data.get('vibe', '').strip() if data else ''

    if not vibe_text:

        return jsonify({'error': 'Please describe a vibe or aesthetic'}), 400



    try:

        # Build a compact catalog summary for context

        all_products = Product.query.all()

        catalog_lines = []

        for p in all_products:

            specs_str = p.specs or '{}'

            catalog_lines.append(

                f"ID:{p.id} | {p.name} | ₹{p.price} | Category: {p.category} | {p.description[:80]}"

            )

        catalog_text = "\n".join(catalog_lines)



        model = genai.GenerativeModel('gemini-2.5-flash-lite')

        prompt = f"""You are an expert interior designer, fashion stylist, and lifestyle curator for an e-commerce store.



The user wants products that match this aesthetic/vibe:

"{vibe_text}"



Here is the full product catalog:

{catalog_text}



Your task:

1. Understand the colors, textures, moods, and themes implied by the vibe.

2. Select 4-8 products from the catalog that BEST match this aesthetic, across DIFFERENT categories if possible.

3. Give each pick a short "why it fits" reason (1 sentence max).

4. Give the entire collection a creative name.



Respond ONLY in this strict JSON format (no markdown, no code fences):

{{"collection_name": "...", "description": "...", "picks": [{{"id": 1, "reason": "..."}}, ...]}}

"""



        response = model.generate_content(prompt)

        raw = response.text.strip()

        # Remove markdown code fences if present

        if raw.startswith('```'):

            raw = raw.split('\n', 1)[1] if '\n' in raw else raw[3:]

        if raw.endswith('```'):

            raw = raw[:-3]

        raw = raw.strip()

        if raw.startswith('json'):

            raw = raw[4:].strip()



        result = json.loads(raw)



        # Enrich with full product data

        enriched_picks = []

        for pick in result.get('picks', []):

            product = Product.query.get(pick.get('id'))

            if product:

                enriched_picks.append({

                    'id': product.id,

                    'name': product.name,

                    'price': product.price,

                    'original_price': product.original_price,

                    'category': product.category,

                    'image_url': product.image_url,

                    'reason': pick.get('reason', ''),

                    'url': url_for('product_detail', product_id=product.id)

                })



        return jsonify({

            'collection_name': result.get('collection_name', 'Curated for You'),

            'description': result.get('description', ''),

            'picks': enriched_picks

        })

    except Exception as e:

        import traceback

        print(f"Vibe Search Error:\n{traceback.format_exc()}")

        return jsonify({'error': 'Failed to process vibe search. Please try again.'}), 500





# ─── VISUAL SEARCH ENDPOINT ──────────────────────────────

@app.route('/api/visual-search', methods=['POST'])

def visual_search():

    if not GEMINI_API_KEY:

        return jsonify({'error': 'Visual search is currently unavailable (missing API key)'}), 503



    if 'image' not in request.files:

        return jsonify({'error': 'No image provided'}), 400



    file = request.files['image']

    if file.filename == '':

        return jsonify({'error': 'No image selected'}), 400



    try:

        # Read the image bytes

        image_bytes = file.read()

        

        # We need to construct a dict for the prompt if using the generative model with bytes directly

        # Format required by google.generativeai for raw data

        image_part = {

            "mime_type": file.mimetype or "image/jpeg",

            "data": image_bytes

        }



        # Initialize the flash model which is faster and great for vision

        model = genai.GenerativeModel('gemini-2.5-flash-lite')

        

        prompt = (

            "You are an expert e-commerce product identifier. "

            "Look at this image and identify the main product. "

            "Return ONLY a short, concise 2-4 word search query that a user would type into a search bar to find this exact or very similar item. "

            "Do not include any other text, punctuation, or explanation. "

            "Example outputs: 'black leather jacket', 'wireless noise-cancelling headphones', 'ceramic coffee mug'."

        )



        response = model.generate_content([image_part, prompt])

        query = response.text.strip().strip("'").strip('"')

        

        return jsonify({'query': query})

    except Exception as e:

        import traceback

        err_msg = traceback.format_exc()

        print(f"Visual Search Error: {err_msg}")

        return jsonify({'error': str(e), 'traceback': err_msg}), 500





# ─── AI ASSISTANT ENDPOINT ────────────────────────────────

def search_products(query: str) -> list[dict]:

    """Search for products in the store by name or category. Use this to help users discover items."""

    products = Product.query.filter(

        (Product.name.ilike(f'%{query}%')) | (Product.category.ilike(f'%{query}%'))

    ).all()

    return [{'id': p.id, 'name': p.name, 'price_inr': f'₹{p.price}', 'stock': p.stock} for p in products]



def get_order_status(order_id: int = None) -> list[dict]:

    """Get the status of the user's orders. Provide order_id for a specific order, or None for recent orders."""

    if not current_user.is_authenticated:

        return [{'error': 'User not authenticated'}]

    query = Order.query.filter_by(user_id=current_user.id)

    if order_id:

        query = query.filter_by(id=order_id)

    orders = query.order_by(Order.created_at.desc()).limit(5).all()

    if not orders:

        return [{'message': 'No orders found'}]

        

    result = []

    for o in orders:

        items = [{'name': i.product.name, 'quantity': i.quantity} for i in o.items]

        result.append({'id': o.id, 'status': o.status, 'total': o.total, 'date': o.created_at.strftime('%Y-%m-%d'), 'items': items})

    return result



def add_to_cart_tool(product_id: int, quantity: int = 1) -> dict:

    """Add a product to the user's shopping cart. Requires a valid product_id."""

    if not current_user.is_authenticated:

        return {'error': 'User not authenticated'}

    product = Product.query.get(product_id)

    if not product:

        return {'error': 'Product not found'}

    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if item:

        item.quantity += quantity

    else:

        item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)

        db.session.add(item)

    db.session.commit()

    return {'success': True, 'message': f'Added {quantity}x {product.name} to cart'}



def raise_ticket_tool(subject: str, description: str) -> dict:

    """Raise a support ticket for the user if they have an issue or complaint."""

    if not current_user.is_authenticated:

        return {'error': 'User not authenticated'}

    from models import Ticket

    ticket = Ticket(user_id=current_user.id, subject=subject, description=description)

    db.session.add(ticket)

    db.session.commit()

    return {'success': True, 'ticket_id': ticket.id, 'message': 'Ticket created successfully'}



def negotiate_price(product_id: int, offered_price: float) -> dict:

    """Negotiate a price for a product. The user offers a price and the AI decides whether to accept, counter, or reject based on margins and inventory."""

    if not current_user.is_authenticated:

        return {'error': 'User not authenticated'}

    product = Product.query.get(product_id)

    if not product:

        return {'error': 'Product not found'}

    

    from datetime import timedelta

    import string

    

    current_price = product.price

    cost_floor = current_price * 0.70  # 30% margin floor = minimum acceptable

    

    # Check if a valid unused coupon already exists for this user+product

    existing = Coupon.query.filter_by(user_id=current_user.id, product_id=product_id, used=False).first()

    if existing and existing.expires_at > datetime.utcnow():

        return {'already_negotiated': True, 'existing_code': existing.code, 'discount': existing.discount_percent,

                'message': f'You already have an active deal! Use code {existing.code} for {existing.discount_percent}% off.'}

    

    if offered_price >= current_price:

        return {'accepted': False, 'message': f'That\'s already at or above the current price of ₹{current_price}. No discount needed!'}

    

    if offered_price < cost_floor:

        # Reject but counter-offer

        counter = round(cost_floor * 1.05, 2)  # 5% above floor

        discount_pct = round((1 - counter / current_price) * 100, 1)

        code = 'DEAL' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        coupon = Coupon(code=code, discount_percent=discount_pct, user_id=current_user.id,

                       product_id=product_id, expires_at=datetime.utcnow() + timedelta(hours=24))

        db.session.add(coupon)

        db.session.commit()

        return {'accepted': False, 'counter_offer': counter, 'discount_percent': discount_pct,

                'coupon_code': code, 'expires_in': '24 hours',

                'message': f'I can\'t go that low, but I can offer ₹{counter} ({discount_pct}% off). Use code: {code}'}

    

    # Accepted! Generate coupon

    discount_pct = round((1 - offered_price / current_price) * 100, 1)

    code = 'DEAL' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    coupon = Coupon(code=code, discount_percent=discount_pct, user_id=current_user.id,

                   product_id=product_id, expires_at=datetime.utcnow() + timedelta(hours=24))

    db.session.add(coupon)

    db.session.commit()

    return {'accepted': True, 'final_price': offered_price, 'discount_percent': discount_pct,

            'coupon_code': code, 'expires_in': '24 hours',

            'message': f'Deal! Use code {code} at checkout for {discount_pct}% off. Valid for 24 hours.'}



def gift_concierge(recipient_description: str, occasion: str, budget: float) -> dict:

    """Find the perfect gift. Takes a description of the recipient, the occasion, and the budget. Returns curated gift suggestions with a personalized card message."""

    if not current_user.is_authenticated:

        return {'error': 'User not authenticated'}

    

    products = Product.query.filter(Product.price <= budget).all()

    if not products:

        return {'message': f'No products found within budget ₹{budget}. Try increasing your budget.'}

    

    product_list = [{'id': p.id, 'name': p.name, 'price': p.price, 'category': p.category, 

                     'description': p.description[:80]} for p in products]

    

    return {'available_products': product_list,

            'recipient': recipient_description, 'occasion': occasion, 'budget': budget,

            'message': f'Found {len(product_list)} products within ₹{budget} budget. I will now curate the best gifts and write a personalized card.'}

ai_tools = [search_products, get_order_status, add_to_cart_tool, raise_ticket_tool, negotiate_price, gift_concierge]



@app.route('/api/negotiate/<int:product_id>', methods=['POST'])

@login_required

def api_negotiate(product_id):

    data = request.get_json()

    offered_price = float(data.get('offer', 0))

    # Call the existing AI tool logic directly

    result = negotiate_price(product_id, offered_price)

    if 'error' in result:

        return jsonify(result), 400

    return jsonify(result)



@app.route('/api/size-recommendation', methods=['POST'])

def api_size_recommendation():

    """Predicts a perfect fit (S/M/L/etc) based on height/weight for clothing."""

    data = request.get_json()

    height = float(data.get('height', 0))

    weight = float(data.get('weight', 0))

    product_category = data.get('category', 'Clothing')

    

    if height <= 0 or weight <= 0:

        return jsonify({'error': 'Please provide valid height and weight.'}), 400



    if not GEMINI_API_KEY:

        # Fallback simplistic heuristic if AI is disabled

        if weight < 60: size = 'Small'

        elif weight < 80: size = 'Medium'

        elif weight < 100: size = 'Large'

        else: size = 'Extra Large'

        return jsonify({'size': size, 'message': f'Based on your data, Size {size} is a Perfect Fit.'})



    try:

        model = genai.GenerativeModel('gemini-2.5-flash-lite')

        prompt = f"""

You are an expert sizing assistant for Trenzia E-commerce.

A user wants to buy an item from the '{product_category}' category.

Their height is {height} cm and their weight is {weight} kg.



Task:

1. Recommend the best fit size (e.g., Small, Medium, Large, XL, etc., or shoe size like US 9/UK 8).

2. Write a single short, confidence-building sentence (e.g., "Based on your data, Size M is a Perfect Fit.")

3. Only output raw JSON, no markdown formatting.

{{ "size": "M", "message": "Based on your data, Size M is a Perfect Fit." }}

"""

        response = model.generate_content(prompt)

        text = response.text.replace('```json', '').replace('```', '').strip()

        result = json.loads(text)

        return jsonify(result)

    except Exception as e:

        print(f"Sizing Predictor Error: {e}")

        return jsonify({'error': 'AI could not predict size right now. Try our size chart.'}), 500



@app.route('/api/build-cart', methods=['POST'])

def api_build_cart():

    if not GEMINI_API_KEY:

        return jsonify({'error': 'AI features are currently unavailable (missing API key)'}), 503

    

    data = request.get_json()

    goal = data.get('goal', '')

    if not goal:

        return jsonify({'error': 'Goal cannot be empty'}), 400



    try:

        # Fetch inventory context

        products = Product.query.all()

        inventory_context = "Available Products:\n"

        for p in products:

            inventory_context += f"- ID: {p.id} | {p.name} | Category: {p.category} | Price: ₹{p.price} | Stock: {p.stock}\n"



        prompt = f"""

You are the Trenzia AI Goal Shopper.

A user has asked you to build a cart based on this goal:

"{goal}"



Here is the current inventory:

{inventory_context}



Task:

1. Select the exact items the user needs to achieve this goal, staying strictly within their mentioned budget (if any).

2. Choose logical, high-quality combinations. Do not exceed the budget.

3. Return a JSON object with this exact structure (NO extra text, NO markdown formatting outside the curly braces, just raw JSON):

{{

  "products": [

    {{"id": 1, "reason": "Short reason why they need this"}},

    {{"id": 2, "reason": "Short reason why they need this"}}

  ],

  "explanation": "A friendly 2-3 sentence explanation of the whole cart you built and how it hits their goal and budget."

}}

"""

        model = genai.GenerativeModel('gemini-2.5-flash-lite')

        response = model.generate_content(prompt)

        text = response.text.strip()

        

        # Clean up markdown block if present

        if text.startswith('```json'):

            text = text[7:]

        if text.endswith('```'):

            text = text[:-3]

        text = text.strip()

        

        # Parse JSON

        result = json.loads(text)

        

        # Hydrate products

        hydrated_products = []

        total = 0

        for item in result.get('products', []):

            product = Product.query.get(item['id'])

            if product:

                hydrated_products.append({

                    'id': product.id,

                    'name': product.name,

                    'price': product.price,

                    'image_url': product.image_url,

                    'reason': item['reason']

                })

                total += product.price

                

        return jsonify({

            'products': hydrated_products,

            'explanation': result.get('explanation', ''),

            'total': total

        })

        

    except Exception as e:

        import traceback

        err_msg = traceback.format_exc()

        print(f"AI Build Cart Error:\n{err_msg}")

        return jsonify({'error': 'Failed to build cart. Please try again.'}), 500



@app.route('/api/chat', methods=['POST'])

def chat_endpoint():

    if not current_user.is_authenticated:

        return jsonify({'error': 'Please log in to use the AI Assistant'}), 401

    

    if not GEMINI_API_KEY:

        return jsonify({'error': 'AI features are currently unavailable (missing API key)'}), 503



    data = request.get_json()

    user_message = data.get('message', '')

    if not user_message:

        return jsonify({'error': 'Message cannot be empty'}), 400



    try:

        model = genai.GenerativeModel(

            model_name='gemini-2.5-flash-lite',

            tools=ai_tools,

            system_instruction=f"""You are a helpful AI Assistant for ShopAI, an e-commerce store. The current user is '{current_user.username}'.



You can help them with:

1. **Search Products** — Find items by name or category.

2. **Check Order Status** — Look up recent orders via track_user_orders (e.g. "where is my jacket?") or a specific order ID via get_order_status.

3. **Add to Cart** — Add products directly to their shopping bag.

4. **Raise Support Tickets** — File complaints or issues.

5. **Negotiate Prices** — Users can haggle! If they ask for a discount, use the negotiate_price tool with the product_id and their offered_price. Be playful and act like a friendly market seller. If the deal is accepted, share the coupon code enthusiastically.

6. **Gift Concierge** — If they need help finding a gift, use gift_concierge with the recipient description, occasion, and budget. Then curate 2-4 best picks from the results and write a heartfelt, personalized gift card message (2-3 sentences, warm and touching).



Always be polite, concise, and conversational. Use emoji sparingly. Format responses in Markdown.

IMPORTANT: This is an Indian e-commerce store. ALL prices are in Indian Rupees. ALWAYS display prices with the ₹ symbol (e.g. ₹1,299). NEVER use $ or USD. If a price is given as a number, prefix it with ₹."""

        )

        

        # We send a single prompt with forced function calling if available, or auto.

        # For simplicity, we create a one-off chat session to allow multi-turn function calling execution.

        chat = model.start_chat(enable_automatic_function_calling=True)

        response = chat.send_message(user_message)

        

        return jsonify({'response': response.text})

    except Exception as e:

        import traceback

        err_msg = traceback.format_exc()

        print(f"AI Chat Error:\n{err_msg}")

        return jsonify({'error': 'Failed to process AI request. Please try again later.'}), 500





# ─── INIT DB ────────────────────────────────────────────

with app.app_context():

    db.create_all()





if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=5000)
