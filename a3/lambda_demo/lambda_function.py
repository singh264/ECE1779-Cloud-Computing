import json
import requests
import logging

def lambda_handler(event, context):
    r = requests.get("https://ifconfig.me")
    logging.debug(r.text)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda! ') + r.text
    }
