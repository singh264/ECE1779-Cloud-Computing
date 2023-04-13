from app__manager import app
from flask import render_template
from flask import request, redirect
from flask import session


# Re-route / to the appropriate page
@app.route("/")
def index():
    if session.get('logged_in', False):
        return redirect("/workers")
    return redirect("/sign-in")


from app__manager.views import login
from app__manager.views import workers
from app__manager.views import controls
