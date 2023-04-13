#!/usr/bin/env bash
python3.7 -m venv src/ven
source src/ven/bin/activate
pip3 install --upgrade pip
pip3 install -r src/requirements.txt
export SECRET_KEY='key'
export MAIL_USERNAME="dn.lerkin@gmail.com"
export MAIL_PASSWORD="bush1054"

python src/run.py
