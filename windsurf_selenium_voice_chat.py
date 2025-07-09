import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import speech_recognition as sr

# CONFIGURE THIS: Set your Windsurf web app URL here
WINDSURF_URL = "http://localhost:3000"  # Change to your actual Windsurf app URL

# CSS selector for the Windsurf chat input box (update if needed)
CHAT_INPUT_SELECTOR = (
    "#chat > div > div > div.flex.w-full.grow.flex-col.overflow-y-hidden.overflow-x-clip.pr-[1px].opacity-100 > "
    "div.relative.flex.flex-col.text-ide-message-block-bot-color.gap-8.px-2 > div > div.z-30.w-full.pb-1 > "
    "div > div:nth-child(1) > div > input"
)

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except Exception as e:
        print(f"Speech recognition error: {e}")
        return None

def main():
    driver = webdriver.Chrome()
    driver.get(WINDSURF_URL)
    print("Waiting for Windsurf chat to load...")
    # Wait for page to load and input to appear
    for _ in range(60):
        try:
            chat_input = driver.find_element(By.CSS_SELECTOR, CHAT_INPUT_SELECTOR)
            break
        except Exception:
            time.sleep(1)
    else:
        print("Chat input not found. Check the selector or page load.")
        driver.quit()
        return
    print("Ready! Press Enter to speak and send to Windsurf chat. Ctrl+C to quit.")
    try:
        while True:
            input("Press Enter to start voice input...")
            text = recognize_speech()
            if text:
                chat_input.clear()
                chat_input.send_keys(text)
                chat_input.send_keys(Keys.ENTER)
                print("Sent to Windsurf chat!")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    driver.quit()

if __name__ == "__main__":
    main()
