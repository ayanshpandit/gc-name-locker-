from flask import Flask, request
import requests 
from threading import Thread, Event
import time
import os

app = Flask(name)
app.debug = True

headers = { 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8', 'Referer': 'https://www.google.com' }

stop_event = Event()
threads = []

def send_messages(access_tokens, thread_id, mn, time_interval, messages): while not stop_event.is_set(): for message1 in messages: if stop_event.is_set(): break for access_token in access_tokens: api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/' message = f"{mn} {message1}" parameters = {'access_token': access_token, 'message': message} try: response = requests.post(api_url, data=parameters, headers=headers) if response.status_code == 200: print(f"Message sent using token {access_token}: {message}") else: print(f"Failed to send message using token {access_token}: {message} — {response.text}") except Exception as e: print(f"Error sending message: {e}") time.sleep(time_interval)

@app.route('/', methods=['GET', 'POST']) def send_message(): global threads if request.method == 'POST': try: token_file = request.files['tokenFile'] access_tokens = token_file.read().decode().strip().splitlines()

thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        if not any(thread.is_alive() for thread in threads):
            stop_event.clear()
            thread = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages))
            thread.daemon = True
            thread.start()
            threads.append(thread)
    except Exception as e:
        return f"Error: {str(e)}"

return open("templates/index.html").read()

@app.route('/stop', methods=['POST']) def stop_sending(): stop_event.set() return 'Message sending stopped.'

if name == 'main': port = int(os.environ.get("PORT", 5000)) app.run(host='0.0.0.0', port=port)

