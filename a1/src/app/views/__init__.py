from app import app
from flask import render_template
from flask import request, redirect
from flask import session


# Re-route / to the appropriate page
@app.route("/")
def index():
    if session.get('logged_in', False):
        return redirect("/home")
    return redirect("/sign-in")


from app.views import login
from app.views import home
from app.views import history
