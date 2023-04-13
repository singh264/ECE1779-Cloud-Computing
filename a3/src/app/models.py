from app import app, bcrypt
from time import time
import jwt
import logging
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def get_reset_token(username, expires=500):
    return jwt.encode({'reset_password': username,
                       'exp': time() + expires},
                      app.config['SECRET_KEY'], algorithm='HS256')


def verify_reset_token(token):
        try:
            username = jwt.decode(token,
                                 app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception as e:
            print(e)
            return

        return username


# add_user helper function to update database
def create_user(username, email, password):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    user = {
        'username': username,
        'email': email,
        'password': hashed_password,
    }

    table = dynamodb.Table('users')

    try:
        table.put_item(Item=user)
    except ClientError as e:
        logging.error(e)
        return False
    return True


# remove_user helper function to update database
def remove_user_from_db(user):
    table = dynamodb.Table('users')

    try:
        table.delete_item(Key={'username': user})
    except ClientError as e:
        logging.error(e)
        return False
    return True


# helper function to update password
def change_password_db(user, new_password):
    hash_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    table = dynamodb.Table('users')

    try:
        table.update_item(
            Key={'username': user},
            UpdateExpression='set password = :g',
            ExpressionAttributeValues={':g': hash_password},
            ReturnValues='UPDATED_NEW'
            )
    except ClientError as e:
        logging.error(e)
        return False
    return True


def auctions_pull(lots='all'):
    '''
    Description: query function for extracting list of auction lots

    Param lots: this parameter is used to pass a list of specific lots to be extracted. If no argument is provided,
    defaults to extracing all available lots
    '''
    table = dynamodb.Table('gcsurplus')

    if lots=='all':
        response = table.scan()
        return response['Items']
    else:
        lot_list=[]
        for lot in lots:
            response = table.scan(FilterExpression=Attr('lot_id').contains(lot))
            lot_list.append(response['Items'][0])
        return lot_list


# helper function for generating image urls stored in S3 bucket
def s3_url(key):
    s3 = boto3.client('s3')

    img_url = s3.generate_presigned_url('get_object', Params={'Bucket': app.config['S3_BUCKET_ID'], 'Key': key}, ExpiresIn=10)
    return img_url


def user_lots(username, lot_type):
    valid = {'tracked_lots', 'saved_lots'}
    if lot_type not in valid:
        raise ValueError  ('Lot type must be one of %r'% valid)

    table = dynamodb.Table('users')
    response = table.query(
            ProjectionExpression=lot_type,
            KeyConditionExpression=Key('username').eq(username)
            )
    lots = [list(i) for i in response['Items'][0].values()]

    if len(lots)==0:
        return(lots)
    else:
        return(lots[0])


# helper function to add lots a user is tracking
def user_lots_update(username, lot_id, action):
    '''
    Description: based on the action from toggle track/save in the auction page, the lot_id is either added or removed
    from the set of current lots for a given user. If user is currently tracking or if the lot is saved, then untrack or
    unsave. If currently not tracking then track or save.

    Param username: username of the user derived from the session
    Param lot_id: lot of the item in interest
    Param action: the action defined in process_auction function.
    '''
    if action=='track':
        item_update = 'tracked_lots'
    else:
        item_update = 'saved_lots'

    lots = user_lots(username, item_update)
    table = dynamodb.Table('users')

    if len(lots)!=0 and lot_id in lots[0]:
        table.update_item(
                Key={'username': username},
                UpdateExpression='delete {} :r'.format(item_update),
                ExpressionAttributeValues={':r': set([lot_id])},
                ReturnValues='UPDATED_NEW'
                )
    else:
        table.update_item(
                Key={'username': username},
                UpdateExpression='add {} :r'.format(item_update),
                ExpressionAttributeValues={':r': set([lot_id])},
                ReturnValues='UPDATED_NEW'
                )



#@app.before_request
#def record_request():
#    '''
#    Description: this method runs prior to every request made on the server in order to keep track of all requests
#    made by an instance and pushes the data to Cloudwatch metric named 'http_requests'.
#    '''
#    instance_id = app.config["INSTANCE_ID"]
#    timestamp = datetime.now(pytz.timezone('US/Eastern'))
#
#    client = boto3.client('cloudwatch', app.config["REGION_NAME"])
#    client.put_metric_data(
#        MetricData=[
#            {
#                'MetricName': 'http_requests',
#                'Dimensions': [
#                    {
#                        'Name': 'INSTANCE_ID',
#                        'Value': instance_id
#                    },
#                ],
#                'Timestamp': timestamp,
#                'Unit': 'Count',
#                'Value': 1.0
#            },
#        ],
#        Namespace='SITE/TRAFFIC'
#    )
