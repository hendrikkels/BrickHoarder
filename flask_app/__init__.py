# Import flask and template operators
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bs4 import Bootstrap, BOOTSTRAP_VERSION

app = Flask(__name__)

# Configurations
app.config.from_object('config')

db = SQLAlchemy(app)
db.create_all()

Bootstrap(app)
print(BOOTSTRAP_VERSION)

import flask_app.views