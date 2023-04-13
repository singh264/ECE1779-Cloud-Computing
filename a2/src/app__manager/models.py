import mysql.connector
from flask import g
from app import app
from app__manager.manager import aws_utils


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

aws_util = aws_utils.AwsUtils()


