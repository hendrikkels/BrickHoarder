# Import flask and template operators
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configurations
app.config.from_object('config')

db = SQLAlchemy(app)
db.create_all()

import flask_app.views