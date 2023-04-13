# ECE1779 Assignment 1
Web Development

## Description

This web application is designed to run a mask detection model on images in order to identify whether people detected in the image are wearing masks. The application provides a full user experience, enabling registered users the ability to login, upload images to detect masks, and view all of their previously uploaded images categorized by the number of people wearing masks. Additionally, users can also reset their password in case they have forgotten it. The application offers additional user management capabilities specific to the administrator, who can register new users.

## Prerequisites

Software requirements:
- Python version 3.5 or older
- MySQL

The following Python packages are required to run the application
- flask
- flask-bcrypt
- mysql-connector
- flask_mail
- pyjwt
- gunicorn
- validators
- Requests

Packages required for running the mask detection model:
- opencv-python
- torch
- torchvision


## Installation:

1. Start the EC2 incstance i-0833970283180168a in AWS and note the Public IPv4 address

2. Connect to the EC2 instance, using the provided AWS pair key and the IPv4 adressed acquired at step 1 
```shell
ssh -i ece1779_dnoskov.pem ubuntu@<Public IPv4 address>
```

3. Database
```shell
# TODO verify to make sure the database "uSLSzoVPTB" is installed by accessing MySQL and running query:
mysql> SHOW DATABASES;

# If not, follow these steps
# TODO, run the following command
$ cd Documents/assignment_1/a1/src/db
$ python create_db.py --create

# TODO next open MySQL Workbench file containing the schema design and synchronize the model to the newly created table “uSLSzoVPTB”
~/user_authentication_schema.mwb
```

4. Run application
```shell
# Change directory to the project
$ cd Documents/assignment_1/a1

#Run the bash script “~/start_main.sh”, which initializes the web application. The script opens the virtual environment, installs any 
# necessary Python packages and launches the application with gunicorn.

$ ./start_main.sh
```

## Architecture:

You can refer to the documentation.pdf file for additional details regarding the architecture of the application.


## Contact:

Denis Noskov - denis.noskov@mail.utoronto.ca
Sheran Cardoza - sheran.cardoza@mail.utoronto.ca

