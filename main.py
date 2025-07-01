import os
from flask import Flask
from fbchat import Client
from fbchat.models import *

EMAIL = os.environ.get("filewala21@gmail.com")
PASSWORD = os.environ.get("pandit@ak47")
GROUP_NAME = "9Y9NSH H3R3 <3"

app = Flask(__name__)

class NameLockBot(Client):
    def onGroupName(self, author_id, new_title, thread_id, thread_type, **kwargs):
        if new_title != GROUP_NAME:
            print(f"Group name changed to {new_title}, reverting...")
            self.changeThreadTitle(GROUP_NAME, thread_id=thread_id, thread_type=thread_type)

@app.route("/")
def home():
    return "Messenger GC Name Locker Bot Running ✅"

def start_bot():
    bot = NameLockBot(EMAIL, PASSWORD)
    bot.listen()

if __name__ == "__main__":
    import threading
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
