import mysql.connector
from flask import g

from app import app
from config import Config

from time import time
import jwt

app.config.from_object(Config)

def connect_to_database():
    return mysql.connector.connect(user=app.config["DB_USERNAME"],
                                   password=app.config["DB_PASSWORD"],
                                   host=app.config["DB_HOST"],
                                   database=app.config["DB_NAME"])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db


@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def get_reset_token(user_id, expires=500):
    return jwt.encode({'reset_password': user_id,
                       'exp': time() + expires},
                      app.config['SECRET_KEY'], algorithm='HS256')

def verify_reset_token(token):
        try:
            user_id = jwt.decode(token,
                                 app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception as e:
            print(e)
            return

        return user_id
