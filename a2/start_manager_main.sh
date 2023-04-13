#!/usr/bin/env bash
sudo fuser -n tcp -k 5000
python3.7 -m venv src/ven
source src/ven/bin/activate
pip3 install --upgrade pip
pip3 install -r src/requirements.txt
export SECRET_KEY='key'
export MAIL_USERNAME="dn.lerkin@gmail.com"
export MAIL_PASSWORD="bush1054"
export S3_BUCKET_ID="3urfhofztr"
python /home/ubuntu/Documents/ECE1779/manager/aws_utils.py
python /home/ubuntu/Documents/ECE1779/manager/auto_scaling.py &
gunicorn --bind 0.0.0.0:5000 --workers=1 --timeout 300 --chdir src app__manager:app --reload
