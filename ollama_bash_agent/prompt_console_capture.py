from playwright.sync_api import sync_playwright

PROMPT = "Write a recursive function that returns the factorial of n."
URL = "http://localhost:5000"  # Update if your app runs elsewhere

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
