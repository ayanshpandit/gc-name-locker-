from flask import Flask, request, render_template, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'AY9NSH_SUPER_SECRET_KEY'  # Change this for security

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'ay9nsh@123'  # 🔐 Change this

KEY_FILE = "approved_keys.txt"

def read_keys():
    if not os.path.exists(KEY_FILE):
        return []
    with open(KEY_FILE, "r") as f:
        return f.read().splitlines()

def save_keys(keys):
    with open(KEY_FILE, "w") as f:
        f.write("\n".join(keys))

@app.route("/")
def user_panel():
    return render_template("message.html")

@app.route("/start", methods=["POST"])
def start_bot():
    user_key = request.form.get("key")
    approved_keys = read_keys()

    if user_key not in approved_keys:
        return "❌ Access Denied: Key not approved"
    
    # 🔁 Your bot logic here
    return "✅ Bot Started Successfully!"

# ---------------- ADMIN PANEL ------------------

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            return "❌ Invalid credentials"
    return '''
    <form method="post">
        <h2>Admin Login</h2>
        <input type="text" name="username" placeholder="Username" required><br><br>
        <input type="password" name="password" placeholder="Password" required><br><br>
        <button type="submit">Login</button>
    </form>
    '''

@app.route("/admin/panel")
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    keys = read_keys()
    return render_template("admin.html", keys=keys)

@app.route("/admin/add", methods=["POST"])
def add_key():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    new_key = request.form.get("new_key").strip()
    keys = read_keys()
    if new_key and new_key not in keys:
        keys.append(new_key)
        save_keys(keys)
    return redirect(url_for('admin_panel'))

@app.route("/admin/delete/<key>")
def delete_key(key):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    keys = read_keys()
    if key in keys:
        keys.remove(key)
        save_keys(keys)
    return redirect(url_for('admin_panel'))
