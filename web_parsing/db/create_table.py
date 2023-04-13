import boto3
import argparse

parser = argparse.ArgumentParser(description='Create database schema.')
parser.add_argument('--create', dest='create', action='store_true', help='Create Schema')
parser.add_argument('--delete', dest='delete', action='store_true', help='Delete Schema')
args = parser.parse_args()

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def create_table(dynamodb):
    table = dynamodb.create_table(
        TableName='gcsurplus',
        KeySchema=[
            {
                'AttributeName': 'lot_id',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'lot_id',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 100,
            'WriteCapacityUnits': 100,
        }
    )

    return table


def delete_table(dynamodb):
    table = dynamodb.Table('gcsurplus')
    table.delete()


if args.create:
    gcsurplus_table = create_table(dynamodb)
    print("Table status:", gcsurplus_table.table_status)
    print("Database created")

elif args.delete:
    delete_table(dynamodb)
    print("Database deleted")

else:
    print("No action taken")
