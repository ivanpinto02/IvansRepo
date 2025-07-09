import time
import keyboard
import pygetwindow as gw

def is_windsurf_active():
    try:
        win = gw.getActiveWindow()
        return win and 'windsurf' in win.title.lower()
    except Exception:
        return False

print("Voice-to-text helper running. Focus a Windsurf text box and press Tab to trigger voice typing (Win+H). Press Ctrl+C to stop.")

while True:
    if is_windsurf_active():
        # Listen for Tab as a proxy for focusing an input
        if keyboard.is_pressed('tab'):
            time.sleep(0.1)
            keyboard.press_and_release('windows+h')
            print("Activated voice typing (Win+H) in Windsurf!")
            time.sleep(2)  # Prevent rapid repeats
    time.sleep(0.1)
