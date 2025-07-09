import time
import keyboard
import pygetwindow as gw

def is_windsurf_textbox_active():
    try:
        win = gw.getActiveWindow()
        # Match window title for Windsurf; adjust if your Windsurf window has a different title
        return win and 'windsurf' in win.title.lower()
    except Exception:
        return False

print("[Windsurf Voice-to-Text] Running. Focus a Windsurf text box and press Tab to activate voice typing (Win+H). Press Ctrl+C to exit.")

try:
    while True:
        if is_windsurf_textbox_active():
            # Listen for Tab key as a proxy for focusing an input (customize as needed)
            if keyboard.is_pressed('tab'):
                time.sleep(0.1)
                keyboard.press_and_release('windows+h')
                print("[Windsurf Voice-to-Text] Activated voice typing (Win+H)!")
                time.sleep(2)  # Prevent rapid repeats
        time.sleep(0.1)
except KeyboardInterrupt:
    print("[Windsurf Voice-to-Text] Exited.")
