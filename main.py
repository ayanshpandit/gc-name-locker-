from flask import Flask, request, redirect, url_for, render_template_string import uuid import os import json from threading import Thread, Event import requests import time

app = Flask(name) app.debug = True

--- Your remaining logic should go here ---

For example:

@app.route('/') def home(): return render_template_string(''' <!DOCTYPE html> <html lang="en"> <head> <meta charset="UTF-8"> <title>Vampire Rulex - Select Mode</title> <style> body { margin: 0; padding: 0; background: url('https://i.imgur.com/92rqE1X.jpeg') no-repeat center center fixed; background-size: cover; font-family: Arial, sans-serif; color: white; } .container { text-align: center; padding-top: 100px; } h1 { font-size: 2.5em; text-shadow: 2px 2px 5px black; } .option-box { display: inline-block; width: 280px; margin: 30px; padding: 40px 20px; border-radius: 15px; background: rgba(0, 0, 0, 0.6); cursor: pointer; transition: 0.3s; box-shadow: 0 0 15px #000; } .option-box:hover { background: rgba(255, 255, 255, 0.1); transform: scale(1.05); } .option-box a { color: white; text-decoration: none; font-size: 1.3em; font-weight: bold; } .footer { margin-top: 100px; font-size: 1em; color: #ddd; text-shadow: 1px 1px 3px black; } </style> </head> <body> <div class="container"> <h1>Vampire Rulex - Select Action</h1> <div class="option-box"> <a href="/start-token">Messenger Token Spam</a> </div> <div class="option-box"> <a href="/start-cookie">Cookie Post Comment</a> </div> <div class="footer"> Created by <b>Vampire Rulex Ayansh</b> </div> </div> </body> </html> ''')

You can continue your logic with /start-token and /start-cookie routes

if name == 'main': port = int(os.environ.get('PORT', 5000)) app.run(host='0.0.0.0', port=port)
