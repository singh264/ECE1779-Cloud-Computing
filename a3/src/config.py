import os

# set up a class to store configuration variables
class Config(object):
    DEBUG            = False
    TESTING          = False
    SECRET_KEY       = os.environ.get('SECRET_KEY')  # store as environment variable
    S3_BUCKET_ID     = '3urfhofztr'
    STATIC_FOLDER    = 'static'
    TEMPLATES_FOLDER = 'templates'


    # Image uploads
    UPLOAD_PATH        = 'static/uploads'
    UPLOAD_EXTENSIONS  = ['.jpg', '.jpeg', '.bmp', '.png', '.gif']
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 # 2MB upload limit

    DOWNLOAD_PATH      = 'static/downloads'

    # Database
    DB_NAME     = 'uSLSzoVPTB'
    DB_USERNAME = 'admin'
    DB_PASSWORD = 'pass12345'
    DB_HOST = 'database-1.cf18wqhdlvtt.us-east-1.rds.amazonaws.com'

    # Mail configurations for Gmail email account
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT=587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # AWS
    INSTANCE_ID = os.popen('ec2metadata --instance-id').read().strip()
    REGION_NAME = 'us-east-1'
    IMAGE_ID = 'ami-005d3e61ce51b5a83'
    KEY_NAME = 'key'
    SECURITY_GROUPS = ['launch-wizard-3']
    IAM_ROLE = 'arn:aws:iam::552776069481:instance-profile/ec2_s3'
    ALB = 'arn:aws:elasticloadbalancing:us-east-1:552776069481:loadbalancer/app/ece1779-a2-alb/70ce7307f8b90bb9'
    ALB_DNS = 'ece1779-a2-alb-1282510941.us-east-1.elb.amazonaws.com'
    TARGET_GROUP = 'arn:aws:elasticloadbalancing:us-east-1:552776069481:targetgroup/user-app-target-group/c5a146d5484eb21b'
    MANAGER_TAG_NAME = 'ece1779_assignment2_manager'


    #SESSION_COOKIE_SECURE = True

db_config = {'user':     'root',
             'password': 'ece1779pass',
             'host':     '127.0.0.1',
             'database': 'uSLSzoVPTB'}

aws_config = {
    'aws_access_key_id': os.environ.get('aws_access_key_id'),
    'aws_secret_access_key': os.environ.get('aws_secret_access_key'),
    'aws_session_token': os.environ.get('aws_session_token')
}
