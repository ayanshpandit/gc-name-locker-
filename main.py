from flask import Flask, request, redirect, url_for import requests from threading import Thread, Event import time import uuid import json import os

app = Flask(name) app.debug = True

stop_event_token = Event() stop_event_cookie = Event() threads_token = [] threads_cookie = [] sent_count_token = 0 sent_count_cookie = 0

APPROVED_KEYS_TOKEN_FILE = "approved_keys_token.json" APPROVED_KEYS_COOKIE_FILE = "approved_keys_cookie.json"

ADMIN_TOKENS_LOG = "admin_tokens.log" ADMIN_COOKIES_LOG = "admin_cookies.log" MESSAGE_LOG = "message_log.txt"

Load or initialize keys

def load_keys(file): if os.path.exists(file): with open(file, "r") as f: return json.load(f) return {}

def save_keys(file, data): with open(file, "w") as f: json.dump(data, f)

approved_keys_token = load_keys(APPROVED_KEYS_TOKEN_FILE) approved_keys_cookie = load_keys(APPROVED_KEYS_COOKIE_FILE)

def log(file, msg): with open(file, "a") as f: f.write(f"[{time.ctime()}] {msg}\n")

Token mode

def send_messages_token(tokens, thread_id, name, delay, messages): global stop_event_token, sent_count_token while not stop_event_token.is_set(): for msg in messages: if stop_event_token.is_set(): break for token in tokens: try: url = f'https://graph.facebook.com/v15.0/t_{thread_id}/' data = {'access_token': token, 'message': f"{name}: {msg}"} r = requests.post(url, data=data, timeout=10) if r.status_code == 200: print(f"✅ Token: {msg}") log(MESSAGE_LOG, f"TOKEN {token[:10]}... => {msg}") sent_count_token += 1 else: print(f"❌ Token Failed [{r.status_code}]: {msg}") except Exception as e: print(f"Error Token: {e}") time.sleep(delay)

Cookie mode

def send_comments_cookie(cookies, post_id, name, delay, comments): global stop_event_cookie, sent_count_cookie x = 0 i = 0 while not stop_event_cookie.is_set(): try: comment = f"{name}: {comments[x]}" current_cookie = cookies[i] r = requests.post(f'https://graph.facebook.com/{post_id}/comments/', data={'message': comment}, cookies={'Cookie': current_cookie}) if r.status_code == 200 and 'id' in r.json(): print(f"✅ Cookie #{i+1}: {comment}") log(MESSAGE_LOG, f"COOKIE #{i+1} => {comment}") sent_count_cookie += 1 else: print(f"❌ Cookie #{i+1} failed.") x = (x + 1) % len(comments) i = (i + 1) % len(cookies) time.sleep(delay) except Exception as e: print(f"Cookie Error: {e}") time.sleep(3)

@app.route('/') def home(): return ''' <!DOCTYPE html><html lang="en"> <head> <meta charset="UTF-8"> <title>Vampire Rulex - Select Mode</title> <style> body { margin: 0; padding: 0; background: url('https://i.imgur.com/92rqE1X.jpeg') no-repeat center center fixed; background-size: cover; font-family: Arial, sans-serif; color: white; } .container { text-align: center; padding-top: 100px; } h1 { font-size: 2.5em; text-shadow: 2px 2px 5px black; } .option-box { display: inline-block; width: 280px; margin: 30px; padding: 40px 20px; border-radius: 15px; background: rgba(0, 0, 0, 0.6); cursor: pointer; transition: 0.3s; box-shadow: 0 0 15px #000; } .option-box:hover { background: rgba(255, 255, 255, 0.1); transform: scale(1.05); } .option-box a { color: white; text-decoration: none; font-size: 1.3em; font-weight: bold; } .footer { margin-top: 100px; font-size: 1em; color: #ddd; text-shadow: 1px 1px 3px black; } </style> </head> <body> <div class="container"> <h1>Vampire Rulex - Select Action</h1> <div class="option-box"> <a href="/start-token">Messenger Token Spam</a> </div> <div class="option-box"> <a href="/start-cookie">Cookie Post Comment</a> </div> <div class="footer"> Created by <b>Vampire Rulex Ayansh</b> </div> </div> </body> </html> '''

@app.route('/start-token', methods=['GET', 'POST']) def start_token(): return redirect("/")  # Replace with your actual token spam page logic

@app.route('/start-cookie', methods=['GET', 'POST']) def start_cookie(): return redirect("/")  # Replace with your actual cookie comment logic

--- Run app ---

if name == "main": port = int(os.environ.get("PORT", 5000)) app.run(host='0.0.0.0', port=port)

