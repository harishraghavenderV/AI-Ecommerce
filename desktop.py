import webview
import threading
import socket
import logging
import os
import ctypes
import ctypes.wintypes
from app import app, db

# ── Suppress Flask logs ──────────────────────────────────────
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# ── Paths ────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ICON_PATH  = os.path.join(BASE_DIR, 'static', 'images', 'trenzia_icon.ico')

# ── Tell Windows this is a unique app (not "python.exe") ──────
# This makes the taskbar show OUR icon instead of the Python snake
myappid = 'trenzia.ai.ecommerce.1'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def start_server(port):
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)

def set_window_icon_via_win32(icon_path):
    """After the pywebview window opens, force-set the icon using Win32 API."""
    import time, ctypes
    time.sleep(2)  # wait for window to appear
    try:
        GWL_HINSTANCE   = -6
        WM_SETICON      = 0x0080
        ICON_SMALL      = 0
        ICON_BIG        = 1
        IMAGE_ICON      = 1
        LR_LOADFROMFILE = 0x00000010

        hwnd_list = []
        def enum_callback(hwnd, lParam):
            import win32gui
            if 'Trenzia' in win32gui.GetWindowText(hwnd):
                hwnd_list.append(hwnd)
            return True

        import win32gui
        win32gui.EnumWindows(enum_callback, None)

        if hwnd_list:
            hwnd = hwnd_list[0]
            hicon = ctypes.windll.user32.LoadImageW(
                0, icon_path, IMAGE_ICON, 64, 64, LR_LOADFROMFILE
            )
            hicon_sm = ctypes.windll.user32.LoadImageW(
                0, icon_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE
            )
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon)
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_sm)
    except Exception as e:
        print(f'[icon] Could not set Win32 icon: {e}')

if __name__ == '__main__':
    port = get_free_port()

    # Start Flask in background
    server_thread = threading.Thread(target=start_server, args=(port,))
    server_thread.daemon = True
    server_thread.start()

    # Start Win32 icon applier in background
    icon_thread = threading.Thread(target=set_window_icon_via_win32, args=(ICON_PATH,))
    icon_thread.daemon = True
    icon_thread.start()

    import time
    time.sleep(1.5)  # let Flask boot

    webview.create_window(
        title='Trenzia',
        url=f'http://127.0.0.1:{port}/',
        width=1280,
        height=800,
        text_select=False,
        confirm_close=True
    )

    webview.start(icon=ICON_PATH)
