import os

# set up a class to store configuration variables
class Config(object):
    DEBUG            = False
    TESTING          = False
    SECRET_KEY       = os.environ.get('SECRET_KEY')  # store as environment variable
    STATIC_FOLDER    = 'static'
    TEMPLATES_FOLDER = 'templates'


    # Image uploads
    UPLOAD_PATH        = 'static/uploads'
    UPLOAD_EXTENSIONS  = ['.jpg', '.jpeg', '.bmp', '.png', '.gif']
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 # 2MB upload limit

    # Database
    DB_NAME     = 'uSLSzoVPTB'
    DB_USERNAME = 'root'
    DB_PASSWORD = 'ece1779pass'
    DB_HOST     = '127.0.0.1'

    # AWS
    #AWS_SECRET_KEY
    #AWS_KEY_ID

    # Mail configurations for Gmail email account
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT=587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')



    #SESSION_COOKIE_SECURE = True

db_config = {'user':     'root',
             'password': 'ece1779pass',
             'host':     '127.0.0.1',
             'database': 'uSLSzoVPTB'}

