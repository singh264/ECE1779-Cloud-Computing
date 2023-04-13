import datetime
import urllib
import logging
import boto3
from botocore.exceptions import ClientError
import os
from boto3.dynamodb.conditions import Attr

BUCKET_NAME = '3urfhofztr'

today = datetime.date.today()


def create_lot(dynamodb, lot, closing_date, year, make, model, mileage, url):
    lot = {
        'lot_id': lot,
        'closing_date': closing_date,
        'year': year,
        'make': make,
        'model': model,
        'mileage': mileage,
        'url': url,
    }

    table = dynamodb.Table('gcsurplus')
    table.put_item(Item=lot)


def delete_lot(dynamodb):
    table = dynamodb.Table('gcsurplus')

    response = table.scan(
        ProjectionExpression='lot_id',
        FilterExpression=Attr('closing_date').lt(str(today))
        )

    old_lots = response['Items']

    for lot in old_lots:
        table.delete_item(
            Key={'lot_id': "".join(lot.values())}
        )

    objects = [{'Key': "".join(lot.values())} for lot in old_lots]

    # If object list is not empty, clear s3 and Image table in db
    if len(objects):
        s3 = boto3.client('s3')
        s3.delete_objects(Bucket=BUCKET_NAME, Delete={'Objects': objects})

    return len(old_lots)


def s3_upload(file_name, bucket_name, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3 = boto3.client('s3')
    try:
        response = s3.upload_file(file_name, bucket_name, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def upload_file(filename, imgurl):
    filepath = os.path.join(os.getcwd(), filename)

    # Download image
    urllib.request.urlretrieve(imgurl, filepath)

    # Upload image to s3 bucket
    s3_upload(filepath, BUCKET_NAME, filename)

    #os.remove(filepath)
