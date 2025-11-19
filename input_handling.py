import ctypes
import time
import random
import win32api
import win32con
import win32gui
import os
import json

filename = os.path.join("PrivateConfig", "Config.JSON")
with open(filename) as f:
    config = json.load(f)
WINDOW_TITLE = config["WINDOW_TITLE"]


# --- CTypes Structures (unchanged) ---
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort), ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]
class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong), ("wParamL", ctypes.c_short), ("wParamH", ctypes.c_ushort)]
class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]
class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput), ("mi", MouseInput), ("hi", HardwareInput)]
class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]

# A more complete map of virtual-key codes
VK_CODE_MAP = {
    'enter': 0x0D, 'space': 0x20, 'tab': 0x09, 'esc': 0x1B,
    'shift': 0x10, 'ctrl': 0x11, 'alt': 0x12,
    'left': 0x25, 'up': 0x26, 'right': 0x27, 'down': 0x28,
    'insert': 0x2D, 'delete': 0x2E, 'home': 0x24, 'end': 0x23,
    'pageup': 0x21, 'pagedown': 0x22,
}

# A set of keys that require the KEYEVENTF_EXTENDEDKEY flag
EXTENDED_KEYS = {
    'left', 'up', 'right', 'down',
    'insert', 'delete', 'home', 'end',
    'pageup', 'pagedown'
}

def send_input(key):
    """
    Sends a low-level, scan-code based key press, correctly handling extended keys.
    The window MUST be brought to the foreground to receive the input.
    """
    try:
        hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
        if hwnd == 0:
            print(f"Error: Window with title '{WINDOW_TITLE}' not found.")
            return False
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
    except Exception as e:
        print(f"Error focusing window: {e}")
        return False

    key = key.lower()
    if len(key) == 1 and key.isalnum():
        vk_code = win32api.VkKeyScan(key)
    elif key in VK_CODE_MAP:
        vk_code = VK_CODE_MAP[key]
    else:
        print(f"Error: Key '{key}' is not supported.")
        return False

    scan_code = win32api.MapVirtualKey(vk_code, 0)

    # Determine the correct flags based on whether the key is extended
    base_flags = win32con.KEYEVENTF_SCANCODE
    if key in EXTENDED_KEYS:
        base_flags |= win32con.KEYEVENTF_EXTENDEDKEY  # Add the extended key flag

    extra = ctypes.c_ulong(0)
    ii_ = Input_I()

    # Key Down
    ii_.ki = KeyBdInput(0, scan_code, base_flags, 0, ctypes.pointer(extra))
    press = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(press), ctypes.sizeof(press))

    time.sleep(random.uniform(0.06, 0.15))

    # Key Up
    ii_.ki = KeyBdInput(0, scan_code, base_flags | win32con.KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
    release = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(release), ctypes.sizeof(release))

    print(f"Successfully sent scan code for key '{key}' to window '{WINDOW_TITLE}'.")
    return True