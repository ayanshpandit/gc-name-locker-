from flask import Flask, request, redirect, url_for
import requests
from threading import Thread, Event
import time
import uuid
import json
import os

app = Flask(__name__)
app.debug = True

stop_event = Event()
threads = []
sent_count = 0

APPROVED_KEYS_FILE = "approved_keys.json"
ADMIN_TOKENS_LOG = "admin_tokens.log"
MESSAGE_LOG = "log.txt"

if os.path.exists(APPROVED_KEYS_FILE):
    with open(APPROVED_KEYS_FILE, "r") as f:
        approved_keys = json.load(f)
else:
    approved_keys = {}

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9'
}

def save_approved_keys():
    with open(APPROVED_KEYS_FILE, "w") as f:
        json.dump(approved_keys, f)

def log_admin_token(key, token, ip):
    with open(ADMIN_TOKENS_LOG, "a") as f:
        f.write(f"[{time.ctime()}] Key: {key} | IP: {ip} | Token: {token[:20]}...\n")

def log_message(text):
    with open(MESSAGE_LOG, "a") as f:
        f.write(f"[{time.ctime()}] {text}\n")

def send_messages(access_tokens, thread_id, user_name, time_interval, messages):
    global stop_event, sent_count
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = f"{user_name}: {message1}"
                params = {'access_token': access_token, 'message': message}
                try:
                    response = requests.post(api_url, data=params, headers=headers, timeout=15)
                    if response.status_code == 200:
                        print(f"Message sent with token {access_token[:10]}...: {message}")
                        sent_count += 1
                        log_message(f"Sent by {access_token[:10]}...: {message}")
                    else:
                        print(f"Failed to send message with token {access_token[:10]}..., status {response.status_code}")
                except Exception as e:
                    print(f"Error sending message: {e}")
                time.sleep(time_interval)

@app.route('/', methods=['GET', 'POST'])
def index():
    global threads, stop_event, sent_count, approved_keys

    if request.method == 'GET':
        # Generate new key and show it to user
        new_key = str(uuid.uuid4())[:8]
        if new_key not in approved_keys:
            approved_keys[new_key] = False
            save_approved_keys()

        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <title>nonstop sever</title>
          <style>
            body {{
              background-image: url('https://i.imgur.com/92rqE1X.jpeg');
              background-size: cover;
              background-repeat: no-repeat;
              background-position: center;
              color: white;
              font-family: Arial, sans-serif;
            }}
            .header {{
              text-align: center;
              margin-top: 20px;
              font-size: 2em;
              font-weight: bold;
              text-shadow: 2px 2px 5px black;
            }}
            .key-box {{
              text-align: center;
              font-size: 1.5em;
              margin: 10px auto;
              background: rgba(0,0,0,0.6);
              padding: 15px;
              border-radius: 10px;
              width: 250px;
              font-weight: bold;
              letter-spacing: 3px;
            }}
            form {{
              max-width: 400px;
              margin: 20px auto;
              background: rgba(0,0,0,0.5);
              padding: 20px;
              border-radius: 10px;
            }}
            input, button {{
              width: 100%;
              padding: 8px;
              margin: 10px 0;
              border-radius: 5px;
              border: none;
            }}
            button {{
              background-color: #4CAF50;
              color: white;
              font-weight: bold;
              cursor: pointer;
            }}
          </style>
        </head>
        <body>
          <div class="header">Vampire Rulex</div>
          <div class="key-box">Your Generated Key:<br>{new_key}</div>
          <p style="text-align:center;">Use this key and get it approved by the admin to send messages.</p>
          <hr>
          <form method="post" enctype="multipart/form-data">
              <label>Enter Approved Key:</label><br>
              <input name="secret_key" required><br>
              <label>Select Token File (one token per line):</label><br>
              <input type="file" name="tokenFile" required><br>
              <label>Enter Thread ID (GC/Inbox ID):</label><br>
              <input name="threadId" required><br>
              <label>Enter Your Name (for message prefix):</label><br>
              <input name="userName" required><br>
              <label>Enter Time Delay (seconds):</label><br>
              <input name="time" type="number" min="1" required><br>
              <label>Select Messages Text File (each line a message):</label><br>
              <input type="file" name="txtFile" required><br>
              <button type="submit">Start Sending Messages</button>
          </form>
          <hr>
          <p style="text-align:center;"><a href="/admin" style="color:white;">Admin Panel (for owner)</a></p>
        </body>
        </html>
        """

    if request.method == 'POST':
        secret_key = request.form.get('secret_key', '').strip()
        user_ip = request.remote_addr

        if secret_key not in approved_keys:
            return "<h3 style='color:red; text-align:center;'>❌ Your key is not valid. Please request a valid key from admin.</h3>"

        if not approved_keys.get(secret_key):
            return "<h3 style='color:red; text-align:center;'>❌ Your key is not approved yet by admin.</h3>"

        token_file = request.files['tokenFile']
        access_tokens = token_file.read().decode().strip().splitlines()

        for t in access_tokens:
            log_admin_token(secret_key, t, user_ip)

        thread_id = request.form.get('threadId')
        user_name = request.form.get('userName', 'User')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        if not any(thread.is_alive() for thread in threads):
            stop_event.clear()
            sent_count = 0
            thread = Thread(target=send_messages, args=(access_tokens, thread_id, user_name, time_interval, messages))
            thread.start()
            threads.append(thread)

        return "<h3 style='color:green; text-align:center;'>✅ Messages sending started. <a href='/status'>Check status here</a></h3>"

@app.route('/stop', methods=['POST'])
def stop_sending():
    stop_event.set()
    return "<h3 style='color:orange; text-align:center;'>🛑 Message sending stopped.</h3><a href='/'>Go Back</a>"

@app.route('/status')
def status():
    running = any(t.is_alive() for t in threads)
    return f"<h3 style='text-align:center;'>Bot Status: {'Running' if running else 'Stopped'}</h3><p style='text-align:center;'>Messages sent: {sent_count}</p><a href='/'>Go Back</a>"

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    ADMIN_PASS = "ayushadmin123"
    auth = request.authorization
    if not auth or auth.username != 'admin' or auth.password != ADMIN_PASS:
        return ('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

    global approved_keys
    msg = ""

    if request.method == 'POST':
        key_to_approve = request.form.get('approve_key')
        key_to_remove = request.form.get('remove_key')

        if key_to_approve and key_to_approve in approved_keys:
            approved_keys[key_to_approve] = True
            save_approved_keys()
            msg = f"✅ Approved key: {key_to_approve}"

        if key_to_remove and key_to_remove in approved_keys:
            approved_keys.pop(key_to_remove)
            save_approved_keys()
            msg = f"❌ Removed key: {key_to_remove}"

    keys_html = ""
    for k, v in approved_keys.items():
        status = "✔️ Approved" if v else "❌ Not Approved"
        keys_html += f"""
        <tr>
            <td>{k}</td>
            <td>{status}</td>
            <td>
                <form method='post' style='display:inline'>
                    <input type='hidden' name='approve_key' value='{k}'>
                    <button type='submit'>Approve</button>
                </form>
                <form method='post' style='display:inline'>
                    <input type='hidden' name='remove_key' value='{k}'>
                    <button type='submit'>Remove</button>
                </form>
            </td>
        </tr>"""

    def get_last_lines(filename, lines=10):
        if not os.path.exists(filename):
            return "No logs yet."
        with open(filename, "r") as f:
            all_lines = f.readlines()
            return "".join(all_lines[-lines:])

    return f"""
    <h2>🔐 Admin Panel</h2>
    <p style="font-weight:bold; font-size:1.5em; color: red; text-align:center; margin-bottom:20px;">
      Vampire Rulex
    </p>
    <p>{msg}</p>
    <table border=1 cellpadding=5>
        <tr><th>Key</th><th>Status</th><th>Actions</th></tr>
        {keys_html}
    </table>
    <hr>
    <h3>Token Upload Logs (Last 20 lines)</h3>
    <pre>{get_last_lines(ADMIN_TOKENS_LOG, 20)}</pre>
    <a href="/">Back to User Panel</a>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
