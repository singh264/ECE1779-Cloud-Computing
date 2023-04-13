import argparse
import mysql.connector
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Database config
DB_NAME = 'uSLSzoVPTB'
DB_USERNAME = 'admin'
DB_PASSWORD = 'pass12345'
DB_HOST = 'database-1.cf18wqhdlvtt.us-east-1.rds.amazonaws.com'

# admin account
username = 'admin'
email = 'dn.lerkin@gmail.com'
password = '12345'

parser = argparse.ArgumentParser(description='Manage admin account in database.')
parser.add_argument('--create', dest='create', action='store_true', help='Create admin account')
parser.add_argument('--delete', dest='delete', action='store_true', help='Delete admin account')
args = parser.parse_args()

cnx = mysql.connector.connect(user=DB_USERNAME,
                                   password=DB_PASSWORD,
                                   host=DB_HOST,
                                   database=DB_NAME)
cursor = cnx.cursor()

if args.create:
    query = "INSERT INTO User (username, password, email) Values (%s, %s, %s)"

    hash_password = bcrypt.generate_password_hash(password).decode('utf-8')

    cursor.execute(query, (username, hash_password, email))
    cnx.commit()

    print("Admin account created")

elif args.delete:
    query = "DELETE FROM User WHERE username = %s"

    cursor.execute(query, (username, ))
    cnx.commit()

    print("Admin account deleted")

else:
    print("No action taken")


