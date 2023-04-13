#from __future__ import print_function
#import sys
# print('Hello world!', file=sys.stderr)

import os
import time
import validators
import urllib.request, urllib.parse
import json

from flask import render_template
from flask import request, redirect
from flask import session, jsonify, make_response
import boto3

from app__manager import app
from app__manager.models import get_db, aws_util
from app__manager.views.login import sign_in_errcheck
from app__manager.views.api import *


@app.before_first_request
def before_first_request_func():
    # Update database to reflect default auto scale values before any request is executed
    cnx = get_db()
    cursor = cnx.cursor()
    query = "UPDATE uSLSzoVPTB.Scaler_config SET enable_auto=%s, min_thresh=%s, max_thresh=%s, grow_ratio=%s, shrink_ratio=%s"
    cursor.execute(query,(1, 20, 25, 2, 0.5,))
    cnx.commit()


def update_auto_scaler(enable_auto):
    '''
    Description: a helper function that updates the enable_auto flag in the database, indicating to the auto-scaler
    whether the auto-scaler feature is enabled

    Param enable_auto: defines whether the the auto scaler flag is enabled
    '''
    cnx = get_db()
    cursor = cnx.cursor()

    if enable_auto:
        # Delete all users from the User table, except for the admin
        query = "UPDATE uSLSzoVPTB.Scaler_config SET enable_auto=1;"
        cursor.execute(query)
        cnx.commit()
    else:
        # Delete all data from the Images table
        query = "UPDATE uSLSzoVPTB.Scaler_config SET enable_auto=0;"
        cursor.execute(query)
        cnx.commit()

def auto_scale_errcheck(min_thresh, max_thresh, grow_ratio, shrink_ratio):
    '''
    Description:  helper function for error checking when user sets new auto scaling configs
    Returns: error message if a new configuration did not pass any of the tests".
    '''
    errmsg = []
    if type(min_thresh) == str:
        if min_thresh.isdigit()==False:
            errmsg.append("Please enter a numerical value or a number above 0")
        elif int(min_thresh)<0:
            errmsg.append("Minimum threshold must be above 0")
        elif int(min_thresh)>100:
            errmsg.append("Minimum threshold must be below 100")
        elif int(min_thresh)>int(max_thresh):
            errmsg.append("Minimum threshold must be below Maximum threshold")
    if type(max_thresh) == str:
        if max_thresh.isdigit()==False:
            errmsg.append("Please enter a numerical value or a number above 0")
        elif int(max_thresh)<0:
            errmsg.append("Maximum threshold must be above 0")
        elif int(max_thresh)>100:
            errmsg.append("Maximum threshold must be below 100")
    if type(grow_ratio) == str:
        if grow_ratio.isdigit()==False:
            errmsg.append("Please enter a numerical value or a number above 0")
        elif int(grow_ratio)<0:
            errmsg.append("Grow ratio must be above 0")
    if type(shrink_ratio) == str:
        if shrink_ratio.isdigit()==False:
            errmsg.append("Please enter a numerical value or a number above 0")
        elif int(shrink_ratio)<0:
            errmsg.append("Shrink ratio must be above 0")

    return errmsg



@app.route("/pool", methods=["GET", "POST"])
def pool():
    '''
    Description:  Worker pool controls to grow and shrink the pool, and set auto-scaling policies.

    Returns: renders the Worker page template "controls/pool.html".
    '''

    if 'user' not in session:
        return redirect("/sign-in")

    # Initial values
    if 'autoscale_policy' not in session:
        autoscale_policy = {
            'enable_auto':  True,
            'min_thresh':   20,
            'max_thresh':   25,
            'grow_ratio':   2,
            'shrink_ratio': 0.5
        }
        session['autoscale_policy'] = autoscale_policy

    enable_auto  = session['autoscale_policy']['enable_auto']
    min_thresh   = session['autoscale_policy']['min_thresh']
    max_thresh   = session['autoscale_policy']['max_thresh']
    grow_ratio   = session['autoscale_policy']['grow_ratio']
    shrink_ratio = session['autoscale_policy']['shrink_ratio']

    if request.method == "POST":
        infomsg = None
        errmsg  = None

        if 'plus1' in request.form:
            # Increase workers by 1
            worker = aws_util.grow_worker_pool_size_by_1()
            infomsg = ["New worker " + worker + " started"]

        elif 'minus1' in request.form:
            # Decrease workers by 1
            worker = aws_util.shrink_worker_pool_size_by_1()
            infomsg = ["Worker " + worker + " terminated"]

        elif 'update_auto' in request.form:
            # Params update
            min_thresh   = request.form.get('min_thresh')
            max_thresh   = request.form.get('max_thresh')
            grow_ratio   = request.form.get('grow_ratio')
            shrink_ratio = request.form.get('shrink_ratio')

            # Form fields can be empty, use saved values in this case
            if min_thresh == '':   min_thresh   = session['autoscale_policy']['min_thresh']
            if max_thresh == '':   max_thresh   = session['autoscale_policy']['max_thresh']
            if grow_ratio == '':   grow_ratio   = session['autoscale_policy']['grow_ratio']
            if shrink_ratio == '': shrink_ratio = session['autoscale_policy']['shrink_ratio']

            errmsg = auto_scale_errcheck(min_thresh, max_thresh, grow_ratio, shrink_ratio)

            if len(errmsg)==0:
                # Save form data
                session['autoscale_policy']['min_thresh']   = min_thresh
                session['autoscale_policy']['max_thresh']   = max_thresh
                session['autoscale_policy']['grow_ratio']   = grow_ratio
                session['autoscale_policy']['shrink_ratio'] = shrink_ratio

                cnx = get_db()
                cursor = cnx.cursor()
                if min_thresh != '':
                    query = "UPDATE uSLSzoVPTB.Scaler_config SET min_thresh = %s"
                    cursor.execute(query,(min_thresh,))
                    cnx.commit()
                if max_thresh != '':
                    query = "UPDATE uSLSzoVPTB.Scaler_config SET max_thresh = %s"
                    cursor.execute(query,(max_thresh,))
                    cnx.commit()
                if grow_ratio != '':
                    query = "UPDATE uSLSzoVPTB.Scaler_config SET grow_ratio = %s"
                    cursor.execute(query,(grow_ratio,))
                    cnx.commit()
                if shrink_ratio != '':
                    query = "UPDATE uSLSzoVPTB.Scaler_config SET shrink_ratio = %s"
                    cursor.execute(query,(shrink_ratio,))
                    cnx.commit()

            else:
                # Don't use form data
                min_thresh   = session['autoscale_policy']['min_thresh']
                max_thresh   = session['autoscale_policy']['max_thresh']
                grow_ratio   = session['autoscale_policy']['grow_ratio']
                shrink_ratio = session['autoscale_policy']['shrink_ratio']

            # Turn on/off auto policy
            if 'enable_auto_policy' not in request.form:
                enable_auto = False

            elif len(errmsg)==0:
                enable_auto = True

            update_auto_scaler(enable_auto)
            session['autoscale_policy']['enable_auto'] = enable_auto

        return render_template("controls/pool.html",
            enable_auto=enable_auto, min_thresh=min_thresh, max_thresh=max_thresh, grow_ratio=grow_ratio, shrink_ratio=shrink_ratio,
            infomsg=infomsg, errmsg=errmsg)

    return render_template("controls/pool.html",
        enable_auto=enable_auto, min_thresh=min_thresh, max_thresh=max_thresh, grow_ratio=grow_ratio, shrink_ratio=shrink_ratio)

@app.route('/live-num-workers', methods=["GET", "POST"])
def live_num_workers():
    data = len(aws_util.get_alb_target_group_workers())
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response

# controls helper function to clear the database
def clear_db():
    cnx = get_db()
    cursor = cnx.cursor()

    # Delete all users from the User table, except for the admin
    query1 = "DELETE FROM User WHERE user_id <> %s"
    cursor.execute(query1, (1, ))
    cnx.commit()
    # Delete all data from the Images table
    query2 = "DELETE FROM Images"
    cursor.execute(query2)
    cnx.commit()
    cnx.close()

# controls helper function to clear the s3
def clear_s3():
    errmsg = []

    # Import the list of images currently stored in the db
    cnx = get_db()
    cursor = cnx.cursor()
    query = "SELECT image_title FROM Images"
    cursor.execute(query)
    keys = cursor.fetchall()
    # Format into an Object Identifier format required for boto3 delete_objects method
    objects = [{'Key': key[0]} for key in keys]

    # If object list is not empty, clear s3 and Image table in db
    if len(objects):
        s3 = boto3.client('s3')
        s3.delete_objects(Bucket=app.config['S3_BUCKET_ID'], Delete={'Objects': objects})

        query = "DELETE FROM Images"
        cursor.execute(query)
        cnx.commit()
        cnx.close()
        return errmsg

    else:
        cnx.close()
        errmsg.append("S3 Bucket is already empty")
        return errmsg

@app.route("/controls", methods=["GET", "POST"])
def controls():
    '''
    Description:  General controls to terminate workers and manager, and clears database and S3 bucket.
    
    Returns: renders the Worker page template "controls/controls.html".
    '''

    if 'user' not in session:
        return redirect("/sign-in")

    if request.method == "POST":
        # stop workers button click
        if 'clear_db' in request.form:
            clear_db()
            infomsg = ["Successfully cleared the database"]
            return render_template("controls/controls.html", infomsg=infomsg)
        if 'clear_s3' in request.form:
            errmsg = clear_s3()
            if len(errmsg):
                return render_template("controls/controls.html", errmsg=errmsg)
            else:
                infomsg = ["Successfully cleared S3"]
                return render_template("controls/controls.html", infomsg=infomsg)
        if 'stop_workers' in request.form:
            aws_util.terminate_all_workers()
            infomsg = ["All workers have been terminated"]
            return render_template("controls/controls.html", infomsg=infomsg)
        if 'stop_all' in request.form:
            aws_util.terminate_all_workers()
            aws_util.stop_manager()
            infomsg = ["All processes have been stopped"]
            return render_template("controls/controls.html", infomsg=infomsg)

    return render_template("controls/controls.html")


