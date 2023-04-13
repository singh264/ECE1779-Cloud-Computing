#!/usr/bin/env bash
sudo fuser -n tcp -k 5000
python3.7 -m venv src/ven
source src/ven/bin/activate
pip3 install --upgrade pip
pip3 install -r src/requirements.txt
export SECRET_KEY='key'
export MAIL_USERNAME="dn.lerkin@gmail.com"
export MAIL_PASSWORD="bush1054"

gunicorn --bind 0.0.0.0:5000 --workers=2 --chdir src app:app --reload
