from flask import Flask
from flask import Config
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate
import os 
basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__, static_url_path='')
app.secret_key = "dshf89we5"
app.config["SQLALCHEMY_DATABASE_URI"] = \
    'sqlite:///' + os.path.join(basedir, 'app.db')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import routes
from app import routes, models

