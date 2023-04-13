#!/bin/bash

cp lambda_function.py .venv/lib/python3.8/site-packages/
cd .venv/lib/python3.8/site-packages/
zip -r9 ~/lambda_function.zip .
cd ../../../..

aws lambda create-function --function-name test2 --runtime python3.8 --zip-file fileb://~/lambda_function.zip --handler lambda_function.lambda_handler --role arn:aws:iam::187864651079:role/a3-role --region us-east-1
