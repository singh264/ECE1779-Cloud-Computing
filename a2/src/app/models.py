import mysql.connector
from flask import g
from app import app
from time import time
import jwt
from datetime import datetime
import pytz
import boto3

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

@app.before_request
def record_request():
    '''
    Description: this method runs prior to every request made on the server in order to keep track of all requests
    made by an instance and pushes the data to Cloudwatch metric named 'http_requests'.
    '''
    instance_id = app.config["INSTANCE_ID"]
    timestamp = datetime.now(pytz.timezone('US/Eastern'))

    client = boto3.client('cloudwatch', app.config["REGION_NAME"])
    client.put_metric_data(
        MetricData=[
            {
                'MetricName': 'http_requests',
                'Dimensions': [
                    {
                        'Name': 'INSTANCE_ID',
                        'Value': instance_id
                    },
                ],
                'Timestamp': timestamp,
                'Unit': 'Count',
                'Value': 1.0
            },
        ],
        Namespace='SITE/TRAFFIC'
    )
