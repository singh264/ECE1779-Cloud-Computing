#from __future__ import print_function
#import sys
# print('Hello world!', file=sys.stderr)

from datetime import timedelta
from flask import render_template
from flask import request, redirect
from flask import session
import re
from app import app, bcrypt
from app.models import get_reset_token, verify_reset_token, create_user, remove_user_from_db, change_password_db
from app.views.api import *
from app.email import send_email
from config import Config
import boto3
from boto3.dynamodb.conditions import Attr


dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

app.config.from_object(Config)

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)


# helper function to error check user credentials for signing in
def sign_in_errcheck(username, password):
    errmsg = []
    table = dynamodb.Table('users')
    response = table.get_item(Key={'username': username})

    if not username:
        errmsg.append("Please enter username")
    if not password:
        errmsg.append("Please enter password")
    if len(errmsg):
        return errmsg
    if 'Item' not in response:
        errmsg.append("Username does not exist")
        return errmsg

    if not bcrypt.check_password_hash(response['Item']['password'], password):
        errmsg.append("Password is wrong")
        return errmsg

    return errmsg


@app.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    if 'user' in session:
        return redirect("/auctions")

    if request.method == "POST":
        # signin button click
        if 'signin' in request.form:
            username = request.form.get("username")
            password = request.form.get("password")

            errmsg = sign_in_errcheck(username, password)
            if len(errmsg):
                return render_template("login/sign_in.html", errmsg=errmsg)

            user_session = {'username': username}
            session['user'] = user_session
            return redirect("/auctions")

        if 'reset' in request.form:
            return redirect("/password-reset-request")

    return render_template("login/sign_in.html")


@app.route("/sign-out")
def sign_out():
   session.pop('user', None)
   return redirect("/auctions")


# add_user helper function to perform error checking
def add_user_errcheck(username, email, password, skip_email=False):
    errmsg = []

    if not username or not password or (not skip_email and not email):
        errmsg.append("Empty form field(s)")
        return errmsg

    table = dynamodb.Table('users')
    response = table.get_item(Key={'username': username})

    if 'Item' in response:
        errmsg.append("Username already exists")
    if not re.search(r'^[A-Za-z0-9]+$', username):
        errmsg.append('Username must contain only characters and numbers')
    if not skip_email and not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        errmsg.append("Email is invalid")

    return errmsg


@app.route("/add-user", methods=["GET", "POST"])
def add_user():
    if 'user' not in session or session['user']['username'] != 'admin':
        return redirect("/auctions")

    if request.method == "POST":
        # adduser button click
        if 'adduser' in request.form:
            username = request.form.get("username")
            email    = request.form.get("email")
            password = request.form.get("password")

            errmsg = add_user_errcheck(username, email, password)
            if len(errmsg):
                return render_template("account/add_user.html", errmsg=errmsg)

            if create_user(username, email, password):
                infomsg = ["Successfully added new user"]
                return render_template("account/add_user.html", infomsg=infomsg)

    return render_template("account/add_user.html")


@app.route("/remove-user", methods=["GET", "POST"])
def remove_user():
    if 'user' not in session or session['user']['username'] != 'admin':
        return redirect("/auctions")

    table = dynamodb.Table('users')
    response = table.scan(
        ProjectionExpression='username, email',
        FilterExpression=Attr('username').ne('admin')
        )
    users = response['Items']

    if request.method == "POST":
        # remove_user button click
        user = request.form.get("username")
        if remove_user_from_db(user):
            infomsg = ["Successfully removed user {}".format(user)]
            return render_template("account/remove_users.html", infomsg=infomsg)

    return render_template("account/remove_users.html", data=users)


# change password helper function to perform error checking
def change_password_errcheck(new_password, username):
    errmsg = []

    if not new_password:
        errmsg = ["Please enter your new password"]
        return errmsg
    if not re.fullmatch(r'[A-Za-z0-9!@#$%^&+=]{6,}', new_password):
        errmsg = ["Make sure your password is at least 6 characters long, and contains at least one upper case "
                "letter, a digit and special character"]
        return errmsg

    # Make sure new password is different from old
    table = dynamodb.Table('users')
    response = table.get_item(Key={'username': username})
    old_password = response['Item']['password']
    if bcrypt.check_password_hash(old_password, new_password):
        errmsg = ["Please enter a different password"]
        return errmsg

    return errmsg

@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if 'user' not in session:
        return redirect("/auctions")

    if request.method == "POST":
        # password reset button click
        if 'reset' in request.form:
            new_password = request.form.get("password")
            errmsg = change_password_errcheck(new_password, session['user']['username'])
            if len(errmsg):
                return render_template('account/change_password.html', errmsg=errmsg)
            else:
                if change_password_db(session['user']['username'], new_password):
                    infomsg = ["Password reset successfully"]
                    return render_template('account/change_password.html', infomsg=infomsg)

    return render_template('account/change_password.html')


@app.route('/password-reset-request', methods=['GET', 'POST'])
def password_reset_request():
    '''
    Description:  renders the template where the user can enter their email to reset the password. The function generates the token 
    and sends out the initial email with the token to the user.
    
    Returns: renders the Password Reset Request page 'login/password_reset_request.html'
    '''

    if 'user' in session:
        # If already signed in, user can use the simpler Change Password mechanism instead
        return redirect("/change-password")

    if request.method == "POST":
        # email reset button click
        if 'reset' in request.form:
            email = request.form.get("email")
            table = dynamodb.Table('users')
            response = table.scan(
                    ProjectionExpression='username',
                    FilterExpression=Attr('email').eq(email))

            user = [i['username'] for i in response['Items']]

            if not email:
                errmsg = ["Please enter your email"]
                return render_template('login/password_reset_request.html', errmsg=errmsg)
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                errmsg = ["Email is invalid"]
                return render_template('login/password_reset_request.html', errmsg=errmsg)
            if not user:
                errmsg = ["Username does not exist"]
                return render_template('login/password_reset_request.html', errmsg=errmsg)
            else:
                token = get_reset_token(user[0])
                send_email('Reset Your Password',
                           sender=app.config["MAIL_USERNAME"],
                           recipients=[email],
                           text_body=render_template('email/reset_password.txt', user=user[0], token=token),
                           html_body=render_template('email/reset_password.html', user=user[0], token=token))

        if 'return' in request.form:
            # Go back button - return to sign-in page
            return redirect("/sign-in")

    return render_template('login/password_reset_request.html')


@app.route('/password-reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    '''
    Description:  verifies the token and renders the template where the user can enter their new password.
    Parameters: token
    Returns: renders the Password Reset page 'login/password_reset.html'.
    '''
    if 'user' in session:
        return redirect("/auctions")

    user = verify_reset_token(token)
    if not user:
        return redirect("/sign-in")

    if request.method == "POST":
        # password reset button click
        if 'reset' in request.form:
            new_password = request.form.get("password")

            errmsg = change_password_errcheck(new_password, user)
            if len(errmsg):
                return render_template('login/password_reset.html', errmsg=errmsg)
            else:
                if change_password_db(user, new_password):
                    return redirect("/sign-in")

    return render_template('login/password_reset.html')


