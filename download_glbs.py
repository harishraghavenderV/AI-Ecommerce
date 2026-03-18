"""
Download free GLB files from KhronosGroup glTF-Sample-Assets and Google model-viewer
to use as category-based AR model fallbacks for products without specific GLBs.

These are all officially free/open-source models.
"""
import requests, os, sys

DEST = 'd:/ai-ecommerce/static/models'
os.makedirs(DEST, exist_ok=True)

# Category-representative free GLBs from official sources
# KhronosGroup: https://github.com/KhronosGroup/glTF-Sample-Assets
BASE_KHR = 'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models'

DOWNLOADS = [
    # (local filename, remote URL, description)

    # Electronics — AntiqueCamera (a camera body shape — closest to electronics)
    ('cat_electronics.glb',
     f'{BASE_KHR}/AntiqueCamera/glTF-Binary/AntiqueCamera.glb',
     'AntiqueCamera (electronics/camera)'),

    # Footwear — WaterBottle is too generic, try Suzanne or ToyCar... 
    # Use ToyCar as footwear placeholder (small rounded object)
    ('cat_footwear.glb',
     f'{BASE_KHR}/ToyCar/glTF-Binary/ToyCar.glb',
     'ToyCar (footwear placeholder)'),

    # Sports & Fitness — WaterBottle
    ('cat_sports.glb',
     f'{BASE_KHR}/WaterBottle/glTF-Binary/WaterBottle.glb',
     'WaterBottle (sports)'),

    # Accessories — Avocado (organic/small object)
    ('cat_accessories.glb',
     f'{BASE_KHR}/Avocado/glTF-Binary/Avocado.glb',
     'Avocado (accessories placeholder)'),

    # Home & Kitchen — Lantern (home decor)
    ('cat_home.glb',
     f'{BASE_KHR}/Lantern/glTF-Binary/Lantern.glb',
     'Lantern (home & kitchen)'),

    # Clothing — DragonAttenuation (cloth sim)
    ('cat_clothing.glb',
     f'{BASE_KHR}/DragonAttenuation/glTF-Binary/DragonAttenuation.glb',
     'DragonAttenuation (clothing)'),

    # Furniture — FlightHelmet (detailed object)
    ('cat_furniture.glb',
     f'{BASE_KHR}/FlightHelmet/glTF-Binary/FlightHelmet.glb',
     'FlightHelmet (furniture placeholder)'),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

for fname, url, desc in DOWNLOADS:
    dest_path = os.path.join(DEST, fname)
    if os.path.exists(dest_path):
        size = os.path.getsize(dest_path)
        print(f'SKIP (exists, {size//1024}KB): {fname}')
        continue

    print(f'Downloading {desc}...')
    try:
        r = requests.get(url, headers=headers, timeout=60, stream=True)
        r.raise_for_status()
        total = int(r.headers.get('content-length', 0))
        downloaded = 0
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
                downloaded += len(chunk)
        size = os.path.getsize(dest_path)
        print(f'  ✅ {fname} ({size//1024}KB)')
    except Exception as e:
        print(f'  ❌ FAILED {fname}: {e}')
        # Try alternative URL
        if 'DragonAttenuation' in url:
            alt_url = f'{BASE_KHR}/BoxAnimated/glTF-Binary/BoxAnimated.glb'
            print(f'  Trying alternative: BoxAnimated...')
            try:
                r = requests.get(alt_url, headers=headers, timeout=30)
                r.raise_for_status()
                with open(dest_path, 'wb') as f:
                    f.write(r.content)
                print(f'  ✅ {fname} from alternative ({len(r.content)//1024}KB)')
            except Exception as e2:
                print(f'  ❌ Alternative also failed: {e2}')

print('\nDone! Available category GLBs:')
for f in sorted(os.listdir(DEST)):
    if f.startswith('cat_'):
        size = os.path.getsize(os.path.join(DEST, f))
        print(f'  {f}  ({size//1024}KB)')
