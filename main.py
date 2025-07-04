from flask import Flask, request, redirect, url_for, render_template_string import uuid import os import json from threading import Thread, Event import requests import time

app = Flask(name)

Event for stopping threads

stop_event_token = Event() stop_event_cookie = Event() sent_token_count = 0 sent_cookie_count = 0 threads = []

Key storage

KEYS_TOKEN = "approved_keys_token.json" KEYS_COOKIE = "approved_keys_cookie.json"

Ensure files exist

if not os.path.exists(KEYS_TOKEN): with open(KEYS_TOKEN, 'w') as f: json.dump({}, f) if not os.path.exists(KEYS_COOKIE): with open(KEYS_COOKIE, 'w') as f: json.dump({}, f)

def load_keys(file): with open(file) as f: return json.load(f)

def save_keys(file, data): with open(file, 'w') as f: json.dump(data, f)

@app.route('/') def home(): html = ''' <!DOCTYPE html> <html lang="en"> <head> <meta charset="UTF-8"> <title>Vampire Rulex Ayansh</title> <style> body { background: url('https://i.imgur.com/92rqE1X.jpeg') no-repeat center center fixed; background-size: cover; font-family: Arial; color: white; text-align: center; padding-top: 100px; } .option { display: inline-block; background: rgba(0,0,0,0.7); padding: 40px; border-radius: 15px; margin: 20px; width: 300px; cursor: pointer; transition: transform 0.3s ease; } .option:hover { transform: scale(1.05); } a { text-decoration: none; color: white; font-weight: bold; font-size: 1.3em; } </style> </head> <body> <h1>Vampire Rulex Ayansh</h1> <div class="option"><a href="/start-token">Messenger Token Spam</a></div> <div class="option"><a href="/start-cookie">Cookie Post Comment</a></div> </body> </html> ''' return render_template_string(html)

@app.route('/start-token', methods=['GET']) def token_ui(): key = str(uuid.uuid4())[:8] keys = load_keys(KEYS_TOKEN) keys[key] = False save_keys(KEYS_TOKEN, keys) return f""" <h2 style='text-align:center;'>Messenger Token Key: <code>{key}</code></h2> <p style='text-align:center;'>Wait for admin approval.</p> """

@app.route('/start-cookie', methods=['GET']) def cookie_ui(): key = str(uuid.uuid4())[:8] keys = load_keys(KEYS_COOKIE) keys[key] = False save_keys(KEYS_COOKIE, keys) return f""" <h2 style='text-align:center;'>Cookie Comment Key: <code>{key}</code></h2> <p style='text-align:center;'>Wait for admin approval.</p> """

@app.route('/admin', methods=['GET', 'POST']) def admin(): auth = request.authorization if not auth or auth.username != "admin" or auth.password != "ayushadmin123": return ('Login required', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

token_keys = load_keys(KEYS_TOKEN)
cookie_keys = load_keys(KEYS_COOKIE)
msg = ""

if request.method == 'POST':
    mode = request.form.get('mode')
    key = request.form.get('key')
    if mode == 'token' and key in token_keys:
        token_keys[key] = True
        save_keys(KEYS_TOKEN, token_keys)
        msg = f"✅ Token Key {key} Approved"
    elif mode == 'cookie' and key in cookie_keys:
        cookie_keys[key] = True
        save_keys(KEYS_COOKIE, cookie_keys)
        msg = f"✅ Cookie Key {key} Approved"

token_list = ''.join([f"<li>{k} - {'✅' if v else '❌'}</li>" for k,v in token_keys.items()])
cookie_list = ''.join([f"<li>{k} - {'✅' if v else '❌'}</li>" for k,v in cookie_keys.items()])
return f'''
<h2>Admin Panel</h2>
<form method='POST'>
    Key: <input name='key'>
    <select name='mode'>
        <option value='token'>Token</option>
        <option value='cookie'>Cookie</option>
    </select>
    <button type='submit'>Approve</button>
</form>
<p>{msg}</p>
<h3>Token Keys</h3><ul>{token_list}</ul>
<h3>Cookie Keys</h3><ul>{cookie_list}</ul>
'''

if name == 'main': port = int(os.environ.get("PORT", 5000)) app.run(host='0.0.0.0', port=port)

