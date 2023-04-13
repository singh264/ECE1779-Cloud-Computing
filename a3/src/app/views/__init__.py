from app import app
from flask import render_template
from flask import request, redirect
from flask import session


# Re-route / to the appropriate page
@app.route("/")
def index():
    return redirect("/auctions")


from app.views import login
from app.views import auctions
