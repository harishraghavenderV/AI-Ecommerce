/**
 * AR Viewer — ar-viewer.js (rewritten)
 * Simple, direct implementation using Google model-viewer and Sketchfab.
 */

// ── Sketchfab model UIDs per product ID ──────────────────────
// Each UID is matched to the actual product type for accurate AR viewing.
const PRODUCT_MODELS = {
    // ── Electronics ─────────────────────────────────────────
    1: 'f90f76c75d8143eb97eb49844050aa26',   // Noise-Cancelling Headphones
    2: '23c16f0235aa46fb8cdbbeea2194847f',   // Running Shoes → Nike Air Max
    3: '8e34fc2b303144f78490007d91ff57c4',   // Laptop → MacBook Pro
    4: 'a74c80a25b2d42dba0f4cd97981f6e05',   // Tablet → iPad Pro
    5: '9e045e469d514fea9dda2ccd161f5fa3',   // Smartphone → iPhone 15 Pro
    6: 'f33263c457664b43909200c5ed5e6fa2',   // Smartwatch → Apple Watch Ultra
    7: '4732564eec0542ed8b1855f381e64127',   // Backpack
    8: '795cdaadafa1464fabb3ff184c50d750',   // JBL Speaker (local 8.glb)
    9: 'ea8b556288744b3f8b16d1f0245ad6ae',   // Drone → DJI Mavic
    10: 'f33263c457664b43909200c5ed5e6fa2',   // Smartwatch
    11: 'f90f76c75d8143eb97eb49844050aa26',   // Earbuds → headphones
    12: 'f2b37b2023434c9ba1ff1bb95bd1fd4d',   // Handbag → leather handbag
    13: 'd551ce74dcd24528a05cbb0f4b7434d7',   // Boot
    14: '8a5b21b25141419983908e0518f96233',   // Sunglasses → wayfarer
    15: '675f34f7304e4d92812a41e9750539aa',   // Office Chair
    16: '4373130bc33c442eb5ed4a0bca818eaf',   // Fitness
    17: '919854763a7640dc8c72afbfccd3e3ee',   // Bottle
    18: '70dff3d9b24a447d9b8e675a3034e41a',   // Coffee machine
    19: '26354cd6800744289bc1754cab8dbd4b',   // Vacuum
    20: '675f34f7304e4d92812a41e9750539aa',   // Furniture
    21: '55a01600dd0147e4bc43d69d30945e43',   // Jewellery
    22: 'dcd91921a2a74f69bb92241b6d593725',   // Wallet
    23: '23c16f0235aa46fb8cdbbeea2194847f',   // Sneaker
    24: '3b7c2f6e2f164d18b6865953b2d88ef1',   // Adidas sneaker

    // ── New Electronics (25–33) ─────────────────────────────
    25: '9e045e469d514fea9dda2ccd161f5fa3',   // iPhone 15 Pro Max
    26: 'f559464bf0f8453d95a0cd273de3ff0b',   // Samsung Galaxy S24 Ultra
    27: 'f90f76c75d8143eb97eb49844050aa26',   // Sony WH-1000XM5 Headphones
    28: '8e34fc2b303144f78490007d91ff57c4',   // MacBook Pro M3
    29: 'a74c80a25b2d42dba0f4cd97981f6e05',   // iPad Pro M2
    30: '93775837f09141fd91bf1b41a0c0953e',   // Sony Alpha Camera → Nikon Z6
    31: 'f33263c457664b43909200c5ed5e6fa2',   // Apple Watch Ultra 2
    32: '8e34fc2b303144f78490007d91ff57c4',   // Dell XPS 15 → laptop
    33: 'f90f76c75d8143eb97eb49844050aa26',   // Bose QC45 Earbuds → headphones

    // ── Clothing (34–41) ───────────────────────────────────
    34: '1f11ec52bd8c4421abc18f45197c198e',   // Merino Wool Sweater
    35: 'bc0d0141da164d3c9f9fe71f6f340c9b',   // Linen Blazer
    36: '794b730ae452424bb3a9ce3c6caaff7a',   // Oversized Hoodie
    37: 'bc0d0141da164d3c9f9fe71f6f340c9b',   // Chino Pants
    38: '1f11ec52bd8c4421abc18f45197c198e',   // Floral Wrap Dress
    39: 'bc0d0141da164d3c9f9fe71f6f340c9b',   // Puffer Down Jacket
    40: '1f11ec52bd8c4421abc18f45197c198e',   // Organic Cotton T-Shirt
    41: 'bc0d0141da164d3c9f9fe71f6f340c9b',   // Denim Jacket

    // ── Footwear (42–49) ───────────────────────────────────
    42: '23c16f0235aa46fb8cdbbeea2194847f',   // Nike Air Max 270
    43: '3b7c2f6e2f164d18b6865953b2d88ef1',   // Adidas Ultraboost 23
    44: 'd551ce74dcd24528a05cbb0f4b7434d7',   // Chelsea Ankle Boot
    45: '0fa5cdc15e224aa883d8da05c2264a67',   // Birkenstock Arizona → sandal
    46: '23c16f0235aa46fb8cdbbeea2194847f',   // New Balance 990v6 → sneaker
    47: 'd551ce74dcd24528a05cbb0f4b7434d7',   // Dr. Martens 1460 → boot
    48: '23c16f0235aa46fb8cdbbeea2194847f',   // Vans Old Skool → sneaker
    49: '0fa5cdc15e224aa883d8da05c2264a67',   // Heel Mule Platform → sandal

    // ── Accessories (50–57) ────────────────────────────────
    50: '693e3e5fc41b42c5af35bc965ab70014',   // Rolex Submariner → luxury watch
    51: 'f2b37b2023434c9ba1ff1bb95bd1fd4d',   // LV Leather Tote → handbag
    52: '8a5b21b25141419983908e0518f96233',   // Polaroid Wayfarer → sunglasses
    53: 'dcd91921a2a74f69bb92241b6d593725',   // Leather Bifold Wallet
    54: '55a01600dd0147e4bc43d69d30945e43',   // Gold Chain Necklace
    55: '4732564eec0542ed8b1855f381e64127',   // Canvas Backpack 30L
    56: '55a01600dd0147e4bc43d69d30945e43',   // Silk Pocket Square
    57: '693e3e5fc41b42c5af35bc965ab70014',   // Stainless Bracelet → watch style

    // ── Home & Kitchen (58–65) ─────────────────────────────
    58: '26354cd6800744289bc1754cab8dbd4b',   // Dyson V15 Vacuum
    59: '70dff3d9b24a447d9b8e675a3034e41a',   // Instant Pot → coffee machine
    60: '70dff3d9b24a447d9b8e675a3034e41a',   // Nespresso Vertuo → espresso machine
    61: '4831c2ce6a0044d9bee9eacefcc0f2bd',   // Marble Serving Board
    62: 'd0618ac16b2a4a87b9b6c7d5e6765626',   // Le Creuset Dutch Oven
    63: 'fcce92a09de84456a071ea6117b57cbc',   // Philips Hue Bulbs
    64: '675f34f7304e4d92812a41e9750539aa',   // Ergonomic Office Chair
    65: '26354cd6800744289bc1754cab8dbd4b',   // Air Purifier → vacuum style

    // ── Sports & Fitness (66–73) ───────────────────────────
    66: '4373130bc33c442eb5ed4a0bca818eaf',   // Resistance Bands
    67: 'f33263c457664b43909200c5ed5e6fa2',   // Garmin GPS Watch → Apple Watch
    68: '919854763a7640dc8c72afbfccd3e3ee',   // Hydro Flask bottle
    69: '4373130bc33c442eb5ed4a0bca818eaf',   // Yoga Mat
    70: '919854763a7640dc8c72afbfccd3e3ee',   // Knee Sleeves
    71: '4373130bc33c442eb5ed4a0bca818eaf',   // Adjustable Dumbbells
    72: '919854763a7640dc8c72afbfccd3e3ee',   // Whey Protein tub
    73: '4373130bc33c442eb5ed4a0bca818eaf',   // Speed Jump Rope

    // ── Extra Electronics (74–76) ──────────────────────────
    74: 'f559464bf0f8453d95a0cd273de3ff0b',   // Steam Deck OLED → Samsung device
    75: 'ea8b556288744b3f8b16d1f0245ad6ae',   // DJI Mini 4 Pro Drone
    76: '8e34fc2b303144f78490007d91ff57c4',   // LG C3 OLED TV → screen/laptop
};

// ── Load 3D model into container ─────────────────────────────
function loadARModel(containerId, productId, modelSrc, productName, productImage) {
    const container = document.getElementById(containerId);
    const loadingEl = document.getElementById('ar-loading');
    if (!container) return;

    // ── Option A: local/category GLB via Google model-viewer ─────────────
    if (modelSrc) {
        // Inline the model-viewer element directly
        container.innerHTML = `
            <model-viewer
                src="${modelSrc}"
                alt="${productName}"
                ar
                ar-modes="webxr scene-viewer quick-look"
                ar-scale="auto"
                auto-rotate
                auto-rotate-delay="0"
                camera-controls
                shadow-intensity="1"
                shadow-softness="0.8"
                exposure="1"
                xr-environment
                style="width:100%;height:100%;min-height:400px;background:#f5f5f7;border-radius:16px;"
                poster="${productImage}">
                <button slot="ar-button" style="
                    position:absolute;bottom:16px;right:16px;
                    background:linear-gradient(135deg,#7c3aed,#ec4899);color:#fff;border:none;
                    padding:10px 20px;border-radius:980px;font-size:13px;
                    font-weight:600;cursor:pointer;font-family:Inter,sans-serif;
                    box-shadow:0 4px 15px rgba(124,58,237,0.4);">
                    ✦ View in AR
                </button>
                <div slot="progress-bar"></div>
            </model-viewer>`;


        const mv = container.querySelector('model-viewer');
        if (mv) {
            // Hide spinner once loaded
            mv.addEventListener('load', () => {
                if (loadingEl) loadingEl.style.display = 'none';
            });
            // Show error if it fails
            mv.addEventListener('error', (e) => {
                console.warn('model-viewer error, falling back to Sketchfab', e);
                if (loadingEl) loadingEl.style.display = 'flex';
                // Fallback: try Sketchfab
                const uid = PRODUCT_MODELS[productId];
                if (uid) {
                    loadSketchfab(container, loadingEl, uid, productName);
                } else {
                    if (loadingEl) loadingEl.innerHTML =
                        '<p style="color:#86868b;font-size:13px;text-align:center;padding:12px;">No 3D model available</p>';
                }
            });
            // Safety timeout — hide spinner after 15s regardless
            setTimeout(() => {
                if (loadingEl) loadingEl.style.display = 'none';
            }, 15000);
        }
        return;
    }

    // ── Option B: Sketchfab embed ────────────────────────────
    const uid = PRODUCT_MODELS[productId];
    if (uid) {
        loadSketchfab(container, loadingEl, uid, productName);
        return;
    }

    // ── Option C: no model at all ────────────────────────────
    if (loadingEl) {
        loadingEl.innerHTML =
            '<p style="color:#86868b;font-size:13px;text-align:center;padding:16px;">No 3D model available for this product.</p>';
    }
}

function loadSketchfab(container, loadingEl, uid, productName) {
    container.innerHTML = `
        <iframe
            src="https://sketchfab.com/models/${uid}/embed?autostart=1&ui_theme=dark&ui_infos=0&ui_controls=1&ui_stop=0&ui_watermark=0"
            style="width:100%;height:100%;min-height:400px;border:none;border-radius:16px;"
            allow="autoplay; fullscreen; xr-spatial-tracking"
            allowfullscreen
            title="${productName}">
        </iframe>`;
    // Sketchfab doesn't fire load events we can hook — hide spinner after 2s
    setTimeout(() => {
        if (loadingEl) loadingEl.style.display = 'none';
    }, 2000);
}

// ── QR code helper ────────────────────────────────────────────
function generateProductQR(containerId, productId) {
    const el = document.getElementById(containerId);
    if (!el || typeof QRCode === 'undefined') return;

    // Clear any previous QR
    el.innerHTML = '';

    let origin = window.location.origin;
    const host = window.location.hostname;

    // If visiting via localhost/127.0.0.1, replace with the server's LAN IP
    // so the QR code works when scanned from a phone on the same WiFi network.
    if (host === 'localhost' || host === '127.0.0.1') {
        // Try to get the LAN IP injected by the server (see base.html meta tag)
        const lanIpMeta = document.querySelector('meta[name="lan-ip"]');
        const lanIp = lanIpMeta ? lanIpMeta.getAttribute('content') : null;
        if (lanIp) {
            origin = 'http://' + lanIp + ':' + (window.location.port || '5000');
        }
    }

    const qrUrl = origin + '/ar/' + productId;
    console.log('[AR] QR code URL:', qrUrl);

    new QRCode(el, {
        text: qrUrl,
        width: 150,
        height: 150,
        colorDark: '#1d1d1f',
        colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.H
    });
}

// Expose globals
window.PRODUCT_MODELS = PRODUCT_MODELS;
window.loadARModel = loadARModel;
window.generateProductQR = generateProductQR;
