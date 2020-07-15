import json
import os

from flask import Flask
from flask_bs4 import Bootstrap, BOOTSTRAP_VERSION

from flask_sqlalchemy import SQLAlchemy

from bricklink import bricklink


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# Supress SQLAlchemy SQLALCHEMY_TRACK_MODIFICAITON depreciation warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Set app variables for SQLite Data Base
app.config['SECRET_KEY'] = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data/inventory.db')

db = SQLAlchemy(app)
db.create_all()

# Initialise Bricklink connetion
auth_json = os.path.join(basedir, 'data/auth.json')
if os.path.isfile(auth_json):
    with open(auth_json) as f:
        auth_params = json.load(f)
        CONSUMER_KEY = auth_params["ConsumerKey"]
        CONSUMER_SECRET = auth_params["ConsumerSecret"]
        TOKEN_VALUE = auth_params["TokenValue"]
        TOKEN_SECRET = auth_params["TokenSecret"]
else:
    print("auth.json file not found, please consult README.md for help.")

bricklinkApi = bricklink.BricklinkApi(bricklink.BricklinkRequester(CONSUMER_KEY, CONSUMER_SECRET, TOKEN_VALUE, TOKEN_SECRET))

# Add Bootstrap 4 to app
Bootstrap(app)
print(BOOTSTRAP_VERSION)

app.config.from_object(__name__)
from app import views