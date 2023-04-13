import os
import datetime

from flask import render_template
from flask import request, redirect
from flask import session, jsonify
from app import app
from app.views.api import *
from app.models import auctions_pull, s3_url, user_lots, user_lots_update


@app.template_filter()
def date_format(closing_date):
    """Converts the closing date into datetime format and returns the date"""
    date_time_obj = datetime.datetime.strptime(closing_date, "%Y-%m-%dT%H:%M:%S")
    return date_time_obj.date()


@app.route("/auctions", methods=["GET", "POST"])
def auctions():
    '''
    Description: List of auctions and search/filtering options.

    Returns: Renders the auctions page template "auctions/auctions.html".
    '''

    signed_in = 'user' in session

    # Extract list of auctions
    auction_list = auctions_pull()

    # Generate a list of image by generating image urls from images stored in S3 bucket
    image_list = {}
    for lot in auction_list:
        key = lot['lot_id']
        image_list[key] = s3_url(key)

    # Extract list of unique models, makes and year to pass into the template
    make_list = set()
    model_list = set()
    year_list = set()

    for i in auction_list:
        make_list.add(i['make'])
        model_list.add(i['model'])
        year_list.add(i['year'])

    if signed_in:
        username = session['user']['username']

        # dummy auctions (for now)
        #auction_list = []
        # list items: id, is_tracked, is_saved, year, model, make, mileage (with units), url, image url
        #auction_list.append(['id_1', False, False, '2013', 'Toyota', 'Highlander Hybrid', '96294 km', 'https://www.gcsurplus.ca/mn-eng.cfm?snc=wfsav&sc=enc-bid&scn=385442&lcn=534095&lct=L&srchtype=&lci=&str=1&lotnf=1&frmsr=1&sf=ferm-clos', 'https://www.gcsurplus.ca/ic-ci/images/535793-990916.jpg'])
        #auction_list.append(['id_2', True, True, '2011', 'Jeep', 'Patriot', '26824 km', 'https://www.gcsurplus.ca/mn-eng.cfm?snc=wfsav&sc=enc-bid&scn=385445&lcn=534098&lct=L&srchtype=&lci=&str=1&lotnf=1&frmsr=1&sf=ferm-clos', 'https://www.gcsurplus.ca/ic-ci/images/535766-990977.jpg'])
        # an example to show that image URL can be left as None
        #auction_list.append(['id_3', True, False, '2014', 'Ford', 'Escape', '117485 km', 'https://www.gcsurplus.ca/mn-eng.cfm?snc=wfsav&sc=enc-bid&scn=385373&lcn=534035&lct=L&srchtype=&lci=&str=1&lotnf=1&frmsr=1&sf=ferm-clos', None])

        tracked_lots = user_lots(username, 'tracked_lots')
        saved_lots = user_lots(username, 'saved_lots')

        return render_template("auctions/auctions.html", auction_list=auction_list, image_list=image_list,
                tracked_lots=tracked_lots, saved_lots=saved_lots, make_list=sorted(make_list), model_list=sorted(model_list))

    if request.method == "POST":
        car_make = request.form.get("car_make", None)
        if car_make != None:
            filtered_auction_list=[]
            for i in auction_list:
                if i['make']=='BMW':
                    filtered_auction_list.append(i)

            return render_template("auctions/auctions.html", auction_list=filtered_auction_list, image_list=image_list,
                    make_list=sorted(make_list), model_list=sorted(model_list))

    return render_template("auctions/auctions.html", auction_list=auction_list, image_list=image_list,
                    make_list=sorted(make_list), model_list=sorted(model_list))


@app.route("/process-auction", methods=["POST"])
def process_auction():
    if 'user' not in session:
        return jsonify({'errmsg': 'Error: Please sign in to perform actions on auctions'})

    username = session['user']['username']

    if request.method == "POST":
        lot_id = request.form['id']
        action = request.form['action']

        user_lots_update(username, lot_id, action)

    return jsonify({})


@app.route("/saved-auctions", methods=["GET", "POST"])
def saved_auctions():
    if 'user' not in session:
        return redirect("/auctions")

    username = session['user']['username']

    # Extract list of saved auction lots
    user_saved_lots = user_lots(username, 'saved_lots')
    auction_list = auctions_pull(user_saved_lots)

    # Generate a list of images by generating image urls from images stored in S3 bucket
    image_list = {}
    for lot in auction_list:
        key = lot['lot_id']
        image_list[key] = s3_url(key)

    return render_template("auctions/saved_auctions.html", auction_list=auction_list, image_list=image_list)

