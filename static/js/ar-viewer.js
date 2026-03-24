/**
 * AR Viewer — ar-viewer.js (rewritten)
 * Simple, direct implementation using Google model-viewer and Sketchfab.
 */

// ── Sketchfab model UIDs per product ID ──────────────────────
// Each UID is matched to the actual product type for accurate AR viewing.
const PRODUCT_MODELS = {
    1: 'f90f76c75d8143eb97eb49844050aa26',
    3: '8e34fc2b303144f78490007d91ff57c4',
    19: '26354cd6800744289bc1754cab8dbd4b',
    20: '675f34f7304e4d92812a41e9750539aa',
    21: '55a01600dd0147e4bc43d69d30945e43',
    2: '23c16f0235aa46fb8cdbbeea2194847f',
    40: '1f11ec52bd8c4421abc18f45197c198e',
    41: 'bc0d0141da164d3c9f9fe71f6f340c9b',
    42: '23c16f0235aa46fb8cdbbeea2194847f',
    43: '3b7c2f6e2f164d18b6865953b2d88ef1',
    44: 'd551ce74dcd24528a05cbb0f4b7434d7',
    53: '1f9f52ae17d642b582d0c5ccf9dd64b3',
    56: 'e9ae41445cfb4fc0892497ba5869ee43',
    57: '4f4ee7261f11438592cc9e0467d722b3',
    58: '5610453d90754b6d8ec982bae336f94e',
    12: 'f2b37b2023434c9ba1ff1bb95bd1fd4d',
    25: '9e045e469d514fea9dda2ccd161f5fa3',
    28: '8e34fc2b303144f78490007d91ff57c4',
    54: '031dba0a7ef44158b7c3a1186438db64',
    55: 'fa173cf26e9e4c30a0763dff88bf9307',
    60: '2bad9d5f36b840c5a15e612cf9b7d78c',
    17: '919854763a7640dc8c72afbfccd3e3ee',
    18: '70dff3d9b24a447d9b8e675a3034e41a',
    59: '583be14ccd6942b98ddc38b766bbc6c7',
    22: 'dcd91921a2a74f69bb92241b6d593725',
    61: '5a732028df844628a74c4cfe22a19b9b',
    4: 'a74c80a25b2d42dba0f4cd97981f6e05',
    5: '9e045e469d514fea9dda2ccd161f5fa3',
    6: 'f33263c457664b43909200c5ed5e6fa2',
    7: '4732564eec0542ed8b1855f381e64127',
    8: '795cdaadafa1464fabb3ff184c50d750',
    9: 'ea8b556288744b3f8b16d1f0245ad6ae',
    10: 'f33263c457664b43909200c5ed5e6fa2',
    11: 'f90f76c75d8143eb97eb49844050aa26',
    13: 'd551ce74dcd24528a05cbb0f4b7434d7',
    14: '8a5b21b25141419983908e0518f96233',
    15: '675f34f7304e4d92812a41e9750539aa',
    16: '4373130bc33c442eb5ed4a0bca818eaf',
    23: '23c16f0235aa46fb8cdbbeea2194847f',
    24: '3b7c2f6e2f164d18b6865953b2d88ef1',
    26: 'f559464bf0f8453d95a0cd273de3ff0b',
    27: 'f90f76c75d8143eb97eb49844050aa26',
    29: 'a74c80a25b2d42dba0f4cd97981f6e05',
    30: '93775837f09141fd91bf1b41a0c0953e',
    31: 'f33263c457664b43909200c5ed5e6fa2',
    32: '8e34fc2b303144f78490007d91ff57c4',
    33: 'f90f76c75d8143eb97eb49844050aa26',
    34: '1f11ec52bd8c4421abc18f45197c198e',
    35: 'bc0d0141da164d3c9f9fe71f6f340c9b',
    36: '794b730ae452424bb3a9ce3c6caaff7a',
    37: 'bc0d0141da164d3c9f9fe71f6f340c9b',
    38: '1f11ec52bd8c4421abc18f45197c198e',
    39: 'bc0d0141da164d3c9f9fe71f6f340c9b',
    45: '0fa5cdc15e224aa883d8da05c2264a67',
    46: '23c16f0235aa46fb8cdbbeea2194847f',
    47: 'd551ce74dcd24528a05cbb0f4b7434d7',
    48: '23c16f0235aa46fb8cdbbeea2194847f',
    49: '0fa5cdc15e224aa883d8da05c2264a67',
    50: '693e3e5fc41b42c5af35bc965ab70014',
    51: 'f2b37b2023434c9ba1ff1bb95bd1fd4d',
    52: '8a5b21b25141419983908e0518f96233',
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
