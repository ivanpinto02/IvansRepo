import subprocess
import sys
import time
from pathlib import Path

PROMPT = "Write a recursive function that returns the factorial of n."
URL = "http://localhost:5000"  # Update if your app runs elsewhere
import subprocess
import sys
import time
import requests
from pathlib import Path

PROMPT = "Write a recursive function that returns the factorial of n."
URL = "http://localhost:5000"  # Flask default
APP_LAUNCH = [sys.executable, str(Path(__file__).parent / "app.py")]

# 1. Launch Flask web app
app_proc = subprocess.Popen(APP_LAUNCH, cwd=str(Path(__file__).parent))

# 2. Wait for server to be ready (poll)
for i in range(20):
    try:
        r = requests.get(URL + '/healthz')
        print(f"[Healthcheck Attempt {i+1}] Status: {getattr(r, 'status_code', None)}")
        if r.status_code == 200:
            print("[Healthcheck Success]")
            break
    except Exception as e:
        print(f"[Healthcheck Attempt {i+1}] Exception: {e}")
    time.sleep(0.5)
else:
    print("[ERROR] Flask server did not start in time.")
    app_proc.terminate()
    sys.exit(1)

# 3. Run Playwright test
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    logs = []
    page.on("console", lambda msg: logs.append(f"{msg.type}: {msg.text}"))
    page.goto(URL)
    page.fill('input[name="prompt"]', PROMPT)       # Update selector if needed
    page.click('button[type="submit"]')             # Update selector if needed
    page.wait_for_timeout(5000)
    browser.close()
    print("# 📝 Captured Console Logs\n")
    for log in logs:
        print(f"- `{log}`")

# 4. Shutdown Flask web app
app_proc.terminate()
