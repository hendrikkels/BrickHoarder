import json
import pathlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

from bricklink import bricklink

# Set variables for bricklink REST API
mydir = pathlib.Path(__file__).parent
auth_json = mydir / "static/auth.json"
if auth_json.is_file():
    with auth_json.open() as f:
        auth_params = json.load(f)
        CONSUMER_KEY = auth_params["ConsumerKey"]
        CONSUMER_SECRET = auth_params["ConsumerSecret"]
        TOKEN_VALUE = auth_params["TokenValue"]
        TOKEN_SECRET = auth_params["TokenSecret"]
bricklinkApi = bricklink.BricklinkApi(
    bricklink.BricklinkRequester(CONSUMER_KEY, CONSUMER_SECRET, TOKEN_VALUE, TOKEN_SECRET))


# Set variables for SQLite Data Base
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'mydatabase.db')
db = SQLAlchemy(app)
db.create_all()



app.config.from_object(__name__)
from app import views