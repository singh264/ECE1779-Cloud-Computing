from flask import Flask
from flask_bcrypt import Bcrypt
from config import Config

import subprocess
import sys

app = Flask(__name__)
app.config.from_object(Config)
bcrypt = Bcrypt(app)

#subprocess.Popen([sys.executable, '/home/ubuntu/Documents/ECE1779/manager/auto_scaling.py'])



from app__manager import views
from app__manager import manager


