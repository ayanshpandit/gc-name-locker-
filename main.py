from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
import random
import string
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'vampire_rulex_secret'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

for folder in ['tokens', 'messages']:
    os.makedirs(os.path.join(UPLOAD_FOLDER, folder), exist_ok=True)

admin_keys = {'vRADMIN'}
approved_keys = set()

def generate_key():
    return "vR" + ''.join(random.choices(string.digits, k=3))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/messenger', methods=['GET', 'POST'])
def messenger():
    if request.method == 'POST':
        key = request.form.get("key")
        if key not in approved_keys:
            return "Key not approved."

        token_file = request.files.get('token_file')
        msg_file = request.files.get('message_file')
        group_uid = request.form.get('group_uid')
        speed = request.form.get('speed')
        hater_name = request.form.get('hater_name')

        if token_file and token_file.filename.endswith('.txt'):
            token_path = os.path.join(UPLOAD_FOLDER, 'tokens', secure_filename(token_file.filename))
            token_file.save(token_path)
        if msg_file and msg_file.filename.endswith('.txt'):
            msg_path = os.path.join(UPLOAD_FOLDER, 'messages', secure_filename(msg_file.filename))
            msg_file.save(msg_path)

        with open("action_log.txt", "a") as log:
            log.write(f"[{datetime.now()}] KEY: {key} | GROUP: {group_uid} | SPEED: {speed} | HATER: {hater_name}
")

        return redirect(url_for('index'))

    return render_template('messenger.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        new_key = request.form.get('key')
        if new_key:
            approved_keys.add(new_key)
    return render_template('admin.html', keys=list(approved_keys))

@app.route('/generate_key')
def generate():
    return generate_key()

if __name__ == '__main__':
    app.run(debug=True)
