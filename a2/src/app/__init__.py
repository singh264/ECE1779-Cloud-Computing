from flask import Flask
from config import Config
from flask_bcrypt import Bcrypt
import os

from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)
bcrypt = Bcrypt(app)

mail = Mail(app)
mail.init_app(app)

from app import views

