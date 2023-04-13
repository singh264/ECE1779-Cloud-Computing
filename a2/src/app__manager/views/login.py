#from __future__ import print_function
#import sys
# print('Hello world!', file=sys.stderr)

from datetime import timedelta
from flask import render_template
from flask import request, redirect
from flask import session, flash
import re
import os
from app__manager import app, bcrypt
from app__manager.models import get_db
from app__manager.views.api import *
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
    cnx.close()
    if not data:
        errmsg.append("Username does not exist")
        return errmsg, None

    user_id, user, psswrd = data[0], data[1], data[2]
    if not (user and bcrypt.check_password_hash(psswrd, password)):
        errmsg.append("Password is wrong")
        return errmsg, None

    if username != 'admin':
        errmsg.append("Only admin can sign in")
        return errmsg, None

    return errmsg, user_id

@app.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    if 'user' in session:
        return redirect("/workers")

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
            return redirect("/workers")

    return render_template("login/sign_in.html")

@app.route("/sign-out")
def sign_out():
   session.pop('user', None)
   return redirect("/sign-in")

