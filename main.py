import os
import asyncio
from flask import Flask
from threading import Thread
from pyppeteer import launch

# Facebook credentials & config
EMAIL = "filewala21@gmail.com"
PASSWORD = "@ayushpandit#12086"
LOCKED_GROUP_NAME = "V9MPIR3 OWN3R 9Y9NSH H3R3 <💝"
GROUP_URL = "https://www.facebook.com/messages/t/24377723681819852"

# Flask app to satisfy Render's port check
app = Flask(__name__)

@app.route('/')
def home():
    return "Messenger GC Name Locker Bot Running ✅"

# Pyppeteer Bot Function
async def locker_bot():
    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.setViewport({"width": 1280, "height": 800})

    print("[+] Logging in...")
    await page.goto('https://www.facebook.com/login', {'waitUntil': 'networkidle2'})
    await page.type('#email', EMAIL)
    await page.type('#pass', PASSWORD)
    await page.click('[name=login]')
    await page.waitForNavigation({'waitUntil': 'networkidle2'})

    print("[+] Opening Messenger Group...")
    await page.goto(GROUP_URL, {'waitUntil': 'networkidle2'})
    await asyncio.sleep(10)

    while True:
        try:
            await page.reload({'waitUntil': 'networkidle2'})
            await asyncio.sleep(5)

            name_element = await page.querySelector('h1 span')
            if name_element:
                group_name = await page.evaluate('(el) => el.textContent', name_element)
                if group_name.strip() != LOCKED_GROUP_NAME.strip():
                    print(f"[⚠] Name changed: {group_name} → Reverting...")

                    await name_element.click()
                    await asyncio.sleep(3)

                    pencil = await page.querySelector("[aria-label='Edit name']")
                    if pencil:
                        await pencil.click()
                        await asyncio.sleep(2)

                        input_box = await page.querySelector("input[type='text']")
                        await input_box.click({'clickCount': 3})
                        await input_box.type(LOCKED_GROUP_NAME)
                        await asyncio.sleep(1)

                        save_btn = await page.querySelector("[aria-label='Save']")
                        if save_btn:
                            await save_btn.click()
                            print("[✔] Reverted successfully!")

            await asyncio.sleep(10)
        except Exception as e:
            print(f"[Error] {e}")
            await asyncio.sleep(10)

# Thread wrapper to start asyncio loop
def start_bot():
    asyncio.run(locker_bot())

# Main entry point
if __name__ == '__main__':
    # Start bot in a background thread
    Thread(target=start_bot).start()

    # Run Flask server to keep Render happy
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
