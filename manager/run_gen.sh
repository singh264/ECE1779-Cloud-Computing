#!/bin/bash

ALB_DNS="http://ece1779-a2-alb-1282510941.us-east-1.elb.amazonaws.com:5000/api/upload"
USER="admin"
PASS="12345"
UPLOAD_RATE_PER_SECOND=1
UPLOAD_COUNT=5
img_folder="/home/ubuntu/Documents/ECE1779/manager/my-photos"

python3 gen.py $ALB_DNS $USER $PASS $UPLOAD_RATE_PER_SECOND $img_folder $UPLOAD_COUNT
