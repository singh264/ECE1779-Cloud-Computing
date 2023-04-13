import argparse
import mysql.connector

# Database config
DB_USERNAME = 'root'
DB_PASSWORD = 'ece1779pass'
DB_HOST = '127.0.0.1'

# admin account

parser = argparse.ArgumentParser(description='Create database schema.')
parser.add_argument('--create', dest='create', action='store_true', help='Create admin account')
parser.add_argument('--delete', dest='delete', action='store_true', help='Delete admin account')
args = parser.parse_args()

cnx = mysql.connector.connect(user=DB_USERNAME,
                                   password=DB_PASSWORD,
                                   host=DB_HOST)
cursor = cnx.cursor()

if args.create:
    query = "CREATE DATABASE uSLSzoVPTB"
    cursor.execute(query)
    cnx.commit()

    print("Database created")

elif args.delete:
    query = "DROP DATABASE uSLSzoVPTB"

    cursor.execute(query)
    cnx.commit()

    print("Database deleted")

else:
    print("No action taken")


