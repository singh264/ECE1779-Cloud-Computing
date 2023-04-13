#from __future__ import print_function
#import sys
# print('Hello world!', file=sys.stderr)

from datetime import timedelta
from flask import render_template
from flask import request, redirect
from flask import session, flash, jsonify
import re
import os
from app import app, bcrypt
from app.models import get_db, get_reset_token, verify_reset_token
from app.views.api import *
from app.email import send_email
from config import Config

app.config.from_object(Config)

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

# helper function to error check user credentials for signing in
def sign_in_errcheck(username, password):
    errmsg = []

    if not username:
        errmsg.append("Please enter username")
    if not password:
        errmsg.append("Please enter password")
    if len(errmsg):
        return errmsg, None

    cnx    = get_db()
    cursor = cnx.cursor()
    query  = "SELECT user_id, username, password FROM User WHERE username = %s"
    cursor.execute(query, (username,))
    data   = cursor.fetchone()
    #cnx.close()
    if not data:
        errmsg.append("Username does not exist")
        return errmsg, None

    user_id, user, psswrd = data[0], data[1], data[2]
    if not (user and bcrypt.check_password_hash(psswrd, password)):
        errmsg.append("Password is wrong")
        return errmsg, None

    return errmsg, user_id

@app.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    if 'user' in session:
        return redirect("/home")

    if request.method == "POST":
        # signin button click
        if 'signin' in request.form:
            username = request.form.get("username")
            password = request.form.get("password")

            errmsg, user_id = sign_in_errcheck(username, password)
            if len(errmsg):
                return render_template("login/sign_in.html", errmsg=errmsg)

            user_session = {'uid': user_id, 'username': username}
            session['user'] = user_session
            return redirect("/home")

        if 'reset' in request.form:
            return redirect("/password-reset-request")

    return render_template("login/sign_in.html")

# add_user helper function to perform error checking
def add_user_errcheck(username, email, password, skip_email=False):
    errmsg = []

    if not username or not password or (not skip_email and not email):
        errmsg.append("Empty form field(s)")
        return errmsg

    cnx = get_db()
    cursor = cnx.cursor()
    query = "SELECT * FROM User WHERE username = %s"
    cursor.execute(query, (username, ))
    account = cursor.fetchone()
    if account:
        errmsg.append("Username already exists")
    if not re.search(r'^[A-Za-z0-9]+$', username):
        errmsg.append('Username must contain only characters and numbers')
    if not skip_email and not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        errmsg.append("Email is invalid")

    return errmsg

# add_user helper function to update database
def add_user_update_db(username, email, password):
    # Generate a hashed password to store in the database
    hash_password = bcrypt.generate_password_hash(password).decode('utf-8')

    cnx = get_db()
    cursor = cnx.cursor()
    query = "INSERT INTO User (username, email, password) Values (%s, %s, %s)"
    cursor.execute(query, (username, email, hash_password))
    cnx.commit()
    #cnx.close()

@app.route("/add-user", methods=["GET", "POST"])
def add_user():
    if 'user' not in session:
        return redirect("/sign-in")
    if session['user']['username'] != 'admin':
        return redirect("/home")

    if request.method == "POST":
        # adduser button click
        if 'adduser' in request.form:
            username = request.form.get("username")
            email    = request.form.get("email")
            password = request.form.get("password")

            errmsg = add_user_errcheck(username, email, password)
            if len(errmsg):
                return render_template("home/add_user.html", errmsg=errmsg)

            add_user_update_db(username, email, password)
            infomsg = ["Successfully added new user"]
            return render_template("home/add_user.html", infomsg=infomsg)

    return render_template("home/add_user.html")



# remove_user helper function to update database
def remove_user_update_db(user):
    cnx = get_db()
    cursor = cnx.cursor()
    query = "DELETE FROM User WHERE username = %s"
    cursor.execute(query, (user, ))
    cnx.commit()
    #cnx.close()

@app.route("/remove-user", methods=["GET", "POST"])
def remove_user():
    if 'user' not in session:
        return redirect("/sign-in")
    if session['user']['username'] != 'admin':
        return redirect("/home")

    cnx = get_db()
    cursor = cnx.cursor()
    query = "SELECT username, email FROM User WHERE username != %s"
    cursor.execute(query, ('admin', ))
    users = cursor.fetchall()

    if request.method == "POST":
        # remove_user button click
        user = request.form.get("username")
        remove_user_update_db(user)
        return redirect("/remove-user")

    return render_template("home/remove_users.html", data=users)



@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    cnx = get_db()
    cursor = cnx.cursor()

    if 'user' not in session:
        return redirect("/sign-in")

    if request.method == "POST":
        # password reset button click
        if 'reset' in request.form:
            new_password = request.form.get("password")
            if not new_password:
                errmsg = ["Please enter your new password"]
                return render_template('home/change_password.html', errmsg=errmsg)
            if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', new_password):
                errmsg = ["Make sure your password is at least 8 characters long, and contains at least one upper case "
                          "letter, a digit and special character"]
                return render_template('home/change_password.html', errmsg=errmsg)

            # Make sure new password is different from old
            query = "SELECT password FROM User WHERE user_id = %s"
            cursor.execute(query, (session['user']['uid'], ))
            old_password = cursor.fetchone()[0]
            if bcrypt.check_password_hash(old_password, new_password):
                errmsg = ["Please enter a different password"]
                return render_template('home/change_password.html', errmsg=errmsg)

            else:
                hash_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

                query = "UPDATE User SET password = %s WHERE user_id = %s"
                cursor.execute(query, (hash_password, session['user']['uid'], ))
                cnx.commit()
                #cnx.close()

                infomsg = ["Password reset successfully"]
                return render_template('home/change_password.html', infomsg=infomsg)

    return render_template('home/change_password.html')



@app.route("/api/register", methods=["POST"])
def api_register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        errmsg = add_user_errcheck(username, None, password, skip_email=True)
        if len(errmsg):
            return jsonify(api_error_json(400, '. '.join(errmsg)))

        add_user_update_db(username, "", password)
        return jsonify(api_register_json())

    return jsonify(api_error_json(403, 'Unrecognized register request'))

@app.route("/sign-out")
def sign_out():
   session.pop('user', None)
   return redirect("/sign-in")


@app.route('/password-reset-request', methods=['GET', 'POST'])
def password_reset_request():
    '''
    Description:  renders the template where the user can enter their email to reset the password. The function generates the token 
    and sends out the initial email with the token to the user.
    
    Returns: renders the Password Reset Request page 'login/password_reset_request.html'
    '''
    cnx = get_db()
    cursor = cnx.cursor()

    if 'user' in session:
        return redirect("/home")

    if request.method == "POST":
        # email reset button click
        if 'reset' in request.form:
            email = request.form.get("email")

            query = "SELECT user_id, username, email FROM User WHERE email = %s"
            cursor.execute(query, (email, ))
            user = cursor.fetchone()
            #cnx.close()

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
                           recipients=[user[2]],
                           text_body=render_template('email/reset_password.txt', user=user[1], token=token),
                           html_body=render_template('email/reset_password.html', user=user[1], token=token))

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
        
    cnx = get_db()
    cursor = cnx.cursor()

    if 'user' in session:
        return redirect("/home")

    user = verify_reset_token(token)
    if not user:
        return redirect("/sign-in")

    if request.method == "POST":
        # password reset button click
        if 'reset' in request.form:
            new_password = request.form.get("password")
            if not new_password:
                errmsg = ["Please enter your new password"]
                return render_template('login/password_reset.html', errmsg=errmsg)
            if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', new_password):
                errmsg = ["Make sure your password is at least 8 characters long, and contains at least one upper case "
                          "letter, a digit and special character"]
                return render_template('login/password_reset.html', errmsg=errmsg)
            else:
                hash_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

                query = "UPDATE User SET password = %s WHERE user_id = %s"
                cursor.execute(query, (hash_password, user, ))
                cnx.commit()
                #cnx.close()

                return redirect("/sign-in")

    return render_template('login/password_reset.html')




