import os
import asyncio
from flask import Flask
from fbchat import Client
from fbchat.models import *

EMAIL = os.environ.get("ounrifkdxl@dygovil.com")
PASSWORD = os.environ.get("@ayushpandit#12086")
GROUP_NAME = "9Y9NSH H3R3 <3"

app = Flask(__name__)

class NameLockBot(Client):
    async def onGroupName(self, mid, author_id, new_title, thread_id, thread_type, **kwargs):
        if new_title != GROUP_NAME:
            print(f"Group name changed to {new_title}, reverting...")
            await self.changeThreadTitle(GROUP_NAME, thread_id=thread_id, thread_type=thread_type)

async def start_bot():
    client = NameLockBot(EMAIL, PASSWORD)
    await client.start(EMAIL, PASSWORD)
    print("Bot started.")
    await client.listen()

@app.route("/")
def home():
    return "Messenger GC Name Locker Bot Running âœ…"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    app.run(host="0.0.0.0", port=port)
