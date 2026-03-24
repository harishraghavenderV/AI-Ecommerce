"""
start_with_ngrok.py
───────────────────
Run this instead of `python app.py` to get a public HTTPS URL via ngrok.
Works from any network — WiFi, mobile data, anywhere!

Usage:
    python start_with_ngrok.py
"""

import subprocess
import threading
import time
import sys
import requests


def start_ngrok():
    """Start ngrok tunnel and print the public URL."""
    print("[ngrok] Starting tunnel on port 5000...")
    proc = subprocess.Popen(
        ['ngrok', 'http', '5000'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    # Wait for ngrok to boot
    for attempt in range(10):
        time.sleep(1.5)
        try:
            resp = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=3)
            tunnels = resp.json().get('tunnels', [])
            for t in tunnels:
                if t.get('proto') == 'https':
                    url = t['public_url']
                    print(f"\n{'='*60}")
                    print(f"  🌐  ngrok PUBLIC URL:  {url}")
                    print(f"  📱  QR codes now work on ANY network / mobile data!")
                    print(f"  AR:  {url}/ar/<product_id>")
                    print(f"{'='*60}\n")
                    return url
        except Exception:
            print(f"[ngrok] Waiting... (attempt {attempt+1}/10)")
    print("[ngrok] ⚠️  Could not detect tunnel URL. Check https://dashboard.ngrok.com")
    return None


def main():
    # Step 1 — Start ngrok in background thread
    ngrok_thread = threading.Thread(target=start_ngrok, daemon=True)
    ngrok_thread.start()

    # Step 2 — Give ngrok 2s head start, then launch Flask
    time.sleep(2)

    print("[Flask] Starting app.py ...")
    try:
        import app  # noqa: F401 — this launches the Flask dev server
        app.app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except ImportError:
        # Fallback: run as subprocess
        subprocess.run([sys.executable, 'app.py'])


if __name__ == '__main__':
    main()
