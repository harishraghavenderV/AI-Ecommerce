/**
 * ShopAI — Main JavaScript
 * Real-time cart, wishlist, search autocomplete, and UI interactions
 */

// ─── TOAST NOTIFICATION ──────────────────────────────
function showToast(message, type = 'info') {
    let toast = document.querySelector('.toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.className = 'toast';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
}


// ─── ADD TO CART ─────────────────────────────────────
function addToCart(productId, quantity = 1) {
    fetch('/api/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, quantity: quantity })
    })
    .then(res => {
        if (res.status === 401) {
            window.location.href = '/auth/login';
            return;
        }
        return res.json();
    })
    .then(data => {
        if (data && data.success) {
            updateCartBadge(data.cart_count);
            showToast('Added to cart!');
        } else if (data && data.error) {
            showToast(data.error, 'error');
        }
    })
    .catch(err => console.error('Cart error:', err));
}


// ─── UPDATE CART ─────────────────────────────────────
function updateCart(itemId, action) {
    fetch('/api/cart/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId, action: action })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            updateCartBadge(data.cart_count);

            if (action === 'remove' || data.cart_count === 0) {
                const item = document.getElementById('cart-item-' + itemId);
                if (item) {
                    item.classList.add('removing');
                    setTimeout(() => {
                        item.remove();
                        if (document.querySelectorAll('.cart-item').length === 0) {
                            location.reload();
                        }
                    }, 300);
                }
            } else {
                // Update totals
                if (document.getElementById('cart-subtotal')) {
                    document.getElementById('cart-subtotal').textContent = '$' + data.total.toFixed(2);
                    const tax = data.total * 0.08;
                    document.getElementById('cart-total').textContent = '$' + (data.total + tax).toFixed(2);
                }
                // Reload to update quantities
                location.reload();
            }
        }
    })
    .catch(err => console.error('Cart update error:', err));
}


// ─── CART BADGE ──────────────────────────────────────
function updateCartBadge(count) {
    const badge = document.getElementById('cart-badge');
    if (!badge) return;
    if (count === undefined) {
        // Fetch current count
        fetch('/cart')
            .then(res => res.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newBadge = doc.getElementById('cart-badge');
                if (newBadge) {
                    badge.textContent = newBadge.textContent;
                    badge.classList.remove('hidden');
                }
            });
        return;
    }
    badge.textContent = count;
    if (count > 0) {
        badge.classList.remove('hidden');
        // Animate
        badge.style.transform = 'scale(1.4)';
        setTimeout(() => badge.style.transform = 'scale(1)', 200);
    } else {
        badge.classList.add('hidden');
    }
}


// ─── WISHLIST TOGGLE ─────────────────────────────────
function toggleWishlist(productId, btn) {
    fetch('/api/wishlist/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId })
    })
    .then(res => {
        if (res.status === 401) {
            window.location.href = '/auth/login';
            return;
        }
        return res.json();
    })
    .then(data => {
        if (data && data.success) {
            if (data.action === 'added') {
                btn.classList.add('bg-red-500/20', 'text-red-400');
                btn.classList.remove('bg-white/5', 'text-dark-400');
                showToast('Added to wishlist!');
            } else {
                btn.classList.remove('bg-red-500/20', 'text-red-400');
                btn.classList.add('bg-white/5', 'text-dark-400');
                showToast('Removed from wishlist');
            }
        }
    })
    .catch(err => console.error('Wishlist error:', err));
}


// ─── SEARCH AUTOCOMPLETE ────────────────────────────
const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');
let searchTimeout = null;

if (searchInput) {
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();

        if (query.length < 2) {
            searchResults.classList.add('hidden');
            searchResults.innerHTML = '';
            return;
        }

        searchTimeout = setTimeout(() => {
            fetch('/api/search?q=' + encodeURIComponent(query))
                .then(res => res.json())
                .then(results => {
                    if (results.length === 0) {
                        searchResults.innerHTML = '<div class="p-4 text-center text-sm text-gray-500">No results found</div>';
                        searchResults.classList.remove('hidden');
                        return;
                    }

                    searchResults.innerHTML = results.map(p => `
                        <a href="/product/${p.id}" class="search-item">
                            <img src="${p.image_url}" class="w-10 h-10 rounded-lg object-cover flex-shrink-0" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 40 40%22><rect fill=%22%231e293b%22 width=%2240%22 height=%2240%22/></svg>'">
                            <div class="flex-1 min-w-0">
                                <p class="text-sm font-medium text-gray-200 truncate">${p.name}</p>
                                <p class="text-xs text-gray-500">${p.category}</p>
                            </div>
                            <span class="text-sm font-bold text-indigo-400 flex-shrink-0">$${p.price.toFixed(2)}</span>
                        </a>
                    `).join('');
                    searchResults.classList.remove('hidden');
                })
                .catch(err => console.error('Search error:', err));
        }, 250);
    });

    // Close search on outside click
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.add('hidden');
        }
    });

    // Search on Enter
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const query = this.value.trim();
            if (query) {
                window.location.href = '/shop?q=' + encodeURIComponent(query);
            }
        }
    });
}


// ─── FLASH MESSAGE AUTO-DISMISS ─────────────────────
setTimeout(() => {
    const container = document.getElementById('flash-container');
    if (container) {
        container.style.transition = 'opacity 0.5s';
        container.style.opacity = '0';
        setTimeout(() => container.remove(), 500);
    }
}, 4000);


// ─── SMOOTH SCROLL FOR ANCHOR LINKS ─────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});
