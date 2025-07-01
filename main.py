import asyncio
from pyppeteer import launch

# Facebook credentials
EMAIL = "filewala21@gmail.com"
PASSWORD = "@ayushpandit#12086"
LOCKED_GROUP_NAME = "V9MPIR3 OWN3R 9Y9NSH H3R3 <💝>"

# Messenger Group Link
GROUP_URL = "https://www.facebook.com/messages/t/24377723681819852"

async def run():
    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.setViewport({"width": 1280, "height": 800})

    print("[+] Opening Facebook login...")
    await page.goto('https://www.facebook.com/login', {'waitUntil': 'networkidle2'})

    await page.type('#email', EMAIL)
    await page.type('#pass', PASSWORD)
    await page.click('[name=login]')
    await page.waitForNavigation({'waitUntil': 'networkidle2'})
    print("[+] Logged in!")

    print("[+] Navigating to Messenger group chat...")
    await page.goto(GROUP_URL, {'waitUntil': 'networkidle2'})
    await asyncio.sleep(10)

    print("[+] Monitoring group name...")

    while True:
        try:
            await page.reload({'waitUntil': 'networkidle2'})
            await asyncio.sleep(5)
            print("[*] Checking group name...")

            # Find current group name element
            name_element = await page.querySelector('h1 span')
            if name_element:
                group_name = await page.evaluate('(el) => el.textContent', name_element)
                print(f"[!] Current group name: {group_name}")

                if group_name.strip() != LOCKED_GROUP_NAME.strip():
                    print("[⚠] Name changed! Reverting...")

                    # Click group name to open settings
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
                            print("[✔] Group name reverted!")

            await asyncio.sleep(10)

        except Exception as e:
            print(f"[Error] {e}")
            await asyncio.sleep(10)

# Start the bot
asyncio.get_event_loop().run_until_complete(run())
