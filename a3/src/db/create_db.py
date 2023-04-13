import boto3
import argparse
from flask_bcrypt import Bcrypt
from botocore.exceptions import ClientError

parser = argparse.ArgumentParser(description='Create database schema.')
parser.add_argument('--create', dest='create', action='store_true', help='Create Schema')
parser.add_argument('--delete', dest='delete', action='store_true', help='Delete Schema')
args = parser.parse_args()

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
bcrypt = Bcrypt()

def create_table():
    table = dynamodb.create_table(
        TableName='users',
        KeySchema=[
            {
                'AttributeName': 'username',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'username',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1,
        }
    )

    return table


def create_admin_user():
    userInput1 = input('Enter email for the Admin account:\n')
    userInput2 = input('Enter password for the Admin account:\n')

    hashed_password = bcrypt.generate_password_hash(userInput2).decode('utf-8')

    user = {
        'username': 'admin',
        'email': userInput1,
        'password': hashed_password,
    }

    table = dynamodb.Table('users')

    try:
        table.put_item(Item=user)
    except ClientError as e:
        print(e)
        return False
    return True


def delete_table():
    table = dynamodb.Table('users')
    table.delete()


if args.create:
    users_table = create_table()
    print("Table status:", users_table.table_status)
    print("Table created\n")

    if create_admin_user():
        print("Admin account created")
    else:
        print("Error when creating Admin account")

elif args.delete:
    delete_table()
    print("Table deleted")

else:
    print("No action taken")
