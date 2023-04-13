import mysql.connector
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Database config
DB_NAME     = 'uSLSzoVPTB'
DB_USERNAME = 'admin'
DB_PASSWORD = 'pass12345'
DB_HOST = 'database-1.cf18wqhdlvtt.us-east-1.rds.amazonaws.com'

# admin account
username = 'user1'
password = '12345'

cnx = mysql.connector.connect(user=DB_USERNAME,
                                   password=DB_PASSWORD,
                                   host=DB_HOST,
                                   database=DB_NAME)

cursor = cnx.cursor()
cursor.execute("SELECT * FROM Scaler_config")
configs = cursor.fetchall()

#new_password = 'Pa$$word12345'
#print(bcrypt.check_password_hash(old_password[0], new_password))

print(configs)
