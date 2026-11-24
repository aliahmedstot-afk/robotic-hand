"""
Voice Control Companion for Windows
Run with: py voice_assistant.py
No third-party Python packages required.
"""
import ctypes, json, os, secrets, subprocess, sys, threading, time, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote_plus

HOST = "127.0.0.1"
PORT = 8765
ALLOWED_ORIGIN = "https://aliahmedstot-afk.github.io"
PAIR_CODE = secrets.token_urlsafe(6)
USER32 = ctypes.windll.user32 if sys.platform == "win32" else None

def key(vk):
    USER32.keybd_event(vk, 0, 0, 0)
    USER32.keybd_event(vk, 0, 2, 0)

def hotkey(*keys):
    for k in keys: USER32.keybd_event(k, 0, 0, 0)
    for k in reversed(keys): USER32.keybd_event(k, 0, 2, 0)

def type_text(text):
    # Unicode keystrokes; limited length to avoid accidental huge pastes.
    text = str(text)[:500]
    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort),
                    ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong),
                    ("dwExtraInfo", ctypes.c_size_t)]
    class INPUT_UNION(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT)]
    class INPUT(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong), ("union", INPUT_UNION)]
    for ch in text:
        code = ord(ch)
        for flags in (0x0004, 0x0004 | 0x0002):
            item = INPUT()
            item.type = 1
            item.union.ki = KEYBDINPUT(0, code, flags, 0, None)
            USER32.SendInput(1, ctypes.byref(item), ctypes.sizeof(INPUT))

def run_command(data):
    cmd = data.get("command", "")
    if cmd == "ping": return "Laptop companion connected."
    apps = {
        "notepad": ["notepad.exe"],
        "calculator": ["calc.exe"],
        "file explorer": ["explorer.exe"],
        "explorer": ["explorer.exe"],
        "chrome": ["cmd", "/c", "start", "", "chrome"],
        "edge": ["cmd", "/c", "start", "", "msedge"],
        "settings": ["cmd", "/c", "start", "", "ms-settings:"],
    }
    if cmd == "open_app":
        app = str(data.get("app", "")).lower()
        if app not in apps: raise ValueError("That app is not on the approved list.")
        subprocess.Popen(apps[app], shell=False)
        return "Opening " + app + "."
    if cmd == "volume_up": key(0xAF); return "Volume up."
    if cmd == "volume_down": key(0xAE); return "Volume down."
    if cmd == "mute": key(0xAD); return "Mute toggled."
    if cmd == "switch_window": hotkey(0x12, 0x09); return "Switched window."
    if cmd == "show_desktop": hotkey(0x5B, 0x44); return "Showing desktop."
    if cmd == "scroll_down": key(0x28); return "Scrolled down."
    if cmd == "scroll_up": key(0x26); return "Scrolled up."
    if cmd == "press_enter": key(0x0D); return "Pressed Enter."
    if cmd == "type_text":
        text = str(data.get("text", ""))
        if not text or len(text) > 500: raise ValueError("Text must be 1–500 characters.")
        type_text(text); return "Typed your text."
    if cmd == "search_web":
        text = str(data.get("text", ""))[:200]
        if not text: raise ValueError("Say what you want to search for.")
        webbrowser.open("https://www.google.com/search?q=" + quote_plus(text))
        return "Opening a web search for " + text + "."
    if cmd == "close_window":
        hotkey(0x12, 0x73); return "Close-window shortcut sent."
    raise ValueError("Command not recognized or not allowed.")

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def add_cors_headers(self):
        origin = self.headers.get("Origin", "")
        if origin == ALLOWED_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Private-Network", "true")
    def do_OPTIONS(self):
        self.send_response(204); self.add_cors_headers(); self.end_headers()
    def do_POST(self):
        origin = self.headers.get("Origin", "")
        if origin != ALLOWED_ORIGIN:
            self.send_error(403, "Website origin not allowed"); return
        if self.path != "/command":
            self.send_error(404); return
        if self.headers.get("Authorization", "") != "Bearer " + PAIR_CODE:
            self.send_error(401, "Wrong pairing code"); return
        try:
            length = min(int(self.headers.get("Content-Length", "0")), 12000)
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            message = run_command(data)
            body = json.dumps({"ok": True, "message": message}).encode()
            self.send_response(200); self.add_cors_headers(); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        except Exception as e:
            body = json.dumps({"ok": False, "message": str(e)}).encode()
            self.send_response(400); self.add_cors_headers(); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

if sys.platform != "win32":
    print("This companion is for Windows 10/11."); input("Press Enter to exit."); raise SystemExit
print("\nVOICE CONTROL COMPANION")
print("Pairing code (enter this on the website): " + PAIR_CODE)
print("Local address: http://127.0.0.1:" + str(PORT))
print("Keep this window open while using voice control. Press Ctrl+C to stop.\n")
try:
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
except KeyboardInterrupt:
    print("\nVoice control stopped.")
