#from __future__ import print_function
#import sys
# print('Hello world!', file=sys.stderr)
# sys.stdout.write('')

import os
import time
import validators
import urllib.request, urllib.parse

from flask import render_template
from flask import request, redirect
from flask import session, jsonify, make_response
import boto3
import config
import json


from app__manager import app
from app__manager.models import get_db, aws_util
from app__manager.views.login import sign_in_errcheck
from app__manager.views.api import *

from numpy import random




@app.context_processor
def lb_dns():
    """Displays the load balancer DNS in the navbar"""
    return {'dns_name': aws_util.get_alb_dns_name()}


@app.route("/workers", methods=["GET", "POST"])
def workers():
    '''
    Description:  displays chart of number of workers, and detailed metrics for each worker.
    
    Returns: renders the Worker page template "workers/worker.html".
    '''

    if 'user' not in session:
        return redirect("/sign-in")

    #if request.method == "POST":
    #    return render_template("workers/workers.html", workers=None)

    workers_lst = aws_util.get_alb_target_group_workers()

    return render_template("workers/workers.html", workers=workers_lst)

def get_all_data(points):
    data = [[point.timestamp.timestamp()*1000, point.value] for point in points]

    response = make_response(json.dumps(data))
    response.content_type = 'application/json'

    return response

def get_new_data(points):
    if points is not None and len(points) > 0:
        point = points[-1]
        data = [point.timestamp.timestamp()*1000, point.value]
    else:
        data = []

    response = make_response(json.dumps(data))
    response.content_type = 'application/json'

    return response

@app.route('/cpuutil-data-all/<worker_id>', methods=["GET", "POST"])
def cpuutil_data_all(worker_id):
    points = aws_util.get_cpu_utilization(worker_id)
    return get_all_data(points)

@app.route('/cpuutil-data-new/<worker_id>', methods=["GET", "POST"])
def cpuutil_data_new(worker_id):
    points = aws_util.get_cpu_utilization(worker_id)
    return get_new_data(points)

@app.route('/httpreq-data-all/<worker_id>', methods=["GET", "POST"])
def httpreq_data_all(worker_id):
    points = aws_util.get_http_requests(worker_id)
    return get_all_data(points)

@app.route('/httpreq-data-new/<worker_id>', methods=["GET", "POST"])
def httpreq_data_new(worker_id):
    points = aws_util.get_http_requests(worker_id)
    return get_new_data(points)

@app.route('/healthyworkers-data-all', methods=["GET", "POST"])
def healthyworkers_data_all():
    points = aws_util.get_alb_workers_history()
    return get_all_data(points)

@app.route('/healthyworkers-data-new', methods=["GET", "POST"])
def healthyworkers_data_new():
    points = aws_util.get_alb_workers_history()
    return get_new_data(points)

@app.route('/unhealthyworkers-data-all', methods=["GET", "POST"])
def unhealthyworkers_data_all():
    points = aws_util.get_alb_unhealthy_workers_history()
    return get_all_data(points)

@app.route('/unhealthyworkers-data-new', methods=["GET", "POST"])
def unhealthyworkers_data_new():
    points = aws_util.get_alb_unhealthy_workers_history()
    return get_new_data(points)

