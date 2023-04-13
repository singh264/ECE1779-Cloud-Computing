#!/bin/bash

cp lambda_function.py .venv/lib/python3.8/site-packages/
cd .venv/lib/python3.8/site-packages/
zip -r9 ~/lambda_function.zip .
cd ../../../..

aws lambda update-function-code --function-name test2 --zip-file fileb://~/lambda_function.zip
