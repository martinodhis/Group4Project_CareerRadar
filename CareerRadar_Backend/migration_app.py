from flask import Flask
from config import Config
from app.extensions import db, migrate
from app import models

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)
