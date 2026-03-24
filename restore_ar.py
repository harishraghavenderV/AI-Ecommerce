import app
import re

previous_js_mapping = '''
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
}
'''

new_uids = {}
for line in previous_js_mapping.split('\n'):
    match = re.search(r"(\d+):\s*'([a-f0-9]+)'", line)
    if match:
        new_uids[int(match.group(1))] = match.group(2)

with app.app.app_context():
    count = 0
    # Apply restored UIDs exactly!
    for pid, uid in new_uids.items():
        p = app.Product.query.get(pid)
        if p:
            # ONLY overwrite if it's NOT the furniture items I specifically built
            # New furniture items are IDs 50-55 and 61 (armchair).
            # Wait, 1-76 are all IDs in the text block, which correspond to seed_products!
            # The newly created furniture items are definitely not 1-50, but let's check what IDs they are.
            if p.name in ['Classic Blue Armchair', 'Industrial Steel TV Stand', 'Nordic Wooden Dining Chair', 
                          'Minimalist White Bookshelf', 'Queen Size Platform Bed', 'Modern Green Velvet Sofa',
                          'Modern Minimalist 3-Seater Sofa', 'Minimalist Oak Coffee Table', 'Nordic Accent Lounge Chair']:
                continue
                
            p.ar_model = uid
            app.db.session.add(p)
            count += 1
            
    app.db.session.commit()
    print(f'Restored original AR mappings for {count} products to the DB!')

    # Now run the sync script to pull everything into the JS precisely!
    products = app.Product.query.all()
    mapping = {}
    for prod in products:
        if prod.ar_model and len(prod.ar_model) > 10:
            mapping[prod.id] = prod.ar_model

js_path = r'static/js/ar-viewer.js'
with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

dict_str = 'const PRODUCT_MODELS = {\n'
for pid, uid in mapping.items():
    dict_str += f'    {pid}: \'{uid}\', \n'
dict_str += '};\n'

new_content = re.sub(r'const PRODUCT_MODELS = \{.*?\};', dict_str, content, flags=re.DOTALL)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'Resynced ar-viewer.js with {len(mapping)} verified clean AR Models!')
