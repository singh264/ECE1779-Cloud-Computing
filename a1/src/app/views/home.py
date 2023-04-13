#from __future__ import print_function
#import sys
# print('Hello world!', file=sys.stderr)

import os
import time
import validators
import urllib.request, urllib.parse
from werkzeug.utils import secure_filename
import requests
import mimetypes
import cv2

from flask import render_template
from flask import request, redirect
from flask import session, jsonify

from app import app
from app.models import get_db
from app.views.login import sign_in_errcheck
from app.views.api import *
# TODO resolve this import path once we finalize location of AI model
from app.ai.pytorch_infer import inference


# helper function to generate a unique filename
def upload_gen_uniq_filename(user_id):
    user_id       = str(session['user']['uid'])
    filename_uniq = user_id + "_" + time.strftime("%Y%m%d%H%M%S")
    return filename_uniq

# helper function to error check an uploaded image
def upload_file_errcheck(uploaded_file):
    errmsg = []

    if not uploaded_file:
        errmsg.append("File not specified")
        return errmsg

    # Error check filename
    filename = secure_filename(uploaded_file.filename)
    if filename == '':
        errmsg.append("Filename cannot be empty")
        return errmsg

    # Error check file extension
    file_ext = os.path.splitext(filename)[1]
    if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
        errmsg.append("Unrecognized file extension")
        return errmsg

    return errmsg    

# helper function to run AI and update database with uploaded image
def upload_run_ai_and_update_db(uid, title, filepath):
    # Run AI inference, save output image, extract results
    img = cv2.imread(filepath)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img, info = inference(img, target_shape=(360, 360))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(filepath, img)
    num_masks = 0
    num_nomasks = 0
    num_faces = len(info)
    for i in info:
        class_id, confidence = i[0], i[1]
        # for class_id meaning, refer to id2class in pytorch_infer.py
        if class_id == 0:
            num_masks += 1
        elif class_id == 1:
            num_nomasks += 1

    # Update database with image location
    cnx = get_db()
    cursor = cnx.cursor()
    query = '''INSERT INTO Images
               (user_id, image_title, img_location, faces_detected, faces_with_masks, faces_without_masks)
               Values (%s, %s, %s, %s, %s, %s)
            '''
    cursor.execute(query,(uid, title, filepath, num_faces, num_masks, num_nomasks))
    cnx.commit()

    return num_faces, num_masks, num_nomasks

@app.route("/home", methods=["GET", "POST"])
def home():
    '''
    Description:  provides image upload functionality from the local computer as well as from a URL. 
    Uploaded images get assigned a filename and filepath that get stored in the database, and the images are loaded to a static uploads folder.
    
    Returns: renders the Home page template "home/home.html".
    '''
        
    if 'user' not in session:
        return redirect("/sign-in")

    user_id = session['user']['uid']

    if request.method == "POST":
        imgsrc_option = request.form.get("imgsrc")

        # upload file
        if imgsrc_option == 'imgsrc_file':
            uploaded_file = request.files.get("imgfile")

            errmsg = upload_file_errcheck(uploaded_file)
            if len(errmsg):
                return render_template("home/home.html", errmsg=errmsg)

            filename      = secure_filename(uploaded_file.filename)
            file_ext      = os.path.splitext(filename)[1]
            filename_uniq = upload_gen_uniq_filename(user_id)
            filepath      = os.path.join(app.root_path, app.config['UPLOAD_PATH'], filename_uniq + file_ext)

            # Download image
            uploaded_file.save(filepath)

            num_faces, num_masks, num_nomasks = upload_run_ai_and_update_db(user_id, filename_uniq, filepath)

            # Render image
            imgurl = os.path.join('/', app.config['UPLOAD_PATH'], filename_uniq + file_ext)
            return render_template("home/home.html", imgurl=imgurl, num_faces=num_faces, num_masks=num_masks, num_nomasks=num_nomasks)

        # upload_url button click
        elif imgsrc_option == 'imgsrc_url':
            errmsg = []

            imgurl = request.form.get('imgurl')

            # Error check if valid URL string
            if not validators.url(imgurl):
                errmsg.append("Invalid URL")
                return render_template("home/home.html", errmsg=errmsg)

            # Error check file extension
            #response = requests.get(imgurl)
            #content_type = response.headers['content-type']
            #file_ext = mimetypes.guess_extension(content_type)
            urlpath = urllib.parse.urlparse(imgurl).path
            file_ext = os.path.splitext(urlpath)[1]

            if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
                errmsg.append("Unrecognized file extension")
                return render_template("home/home.html", errmsg=errmsg)

            filename_uniq = upload_gen_uniq_filename(user_id)
            filepath      = os.path.join(app.root_path, app.config['UPLOAD_PATH'], filename_uniq + file_ext)

            # Download image
            urllib.request.urlretrieve(imgurl, filepath)

            num_faces, num_masks, num_nomasks = upload_run_ai_and_update_db(user_id, filename_uniq, filepath)

            # Render image
            imgurl = os.path.join('/', app.config['UPLOAD_PATH'], filename_uniq + file_ext)
            return render_template("home/home.html", imgurl=imgurl, num_faces=num_faces, num_masks=num_masks, num_nomasks=num_nomasks)

    return render_template("home/home.html")

@app.route("/api/upload", methods=["POST"])
def api_upload():
    if request.method == "POST":
        username      = request.form.get("username")
        password      = request.form.get("password")
        uploaded_file = request.files.get("file")

        errmsg1, user_id = sign_in_errcheck(username, password)
        errmsg2          = upload_file_errcheck(uploaded_file)
        errmsg           = errmsg1 + errmsg2
        if len(errmsg):
            return jsonify(api_error_json(400, '. '.join(errmsg)))

        filename      = secure_filename(uploaded_file.filename)
        file_ext      = os.path.splitext(filename)[1]
        filename_uniq = upload_gen_uniq_filename(user_id)
        filepath      = os.path.join(app.root_path, app.config['UPLOAD_PATH'], filename_uniq + file_ext)

        # Download image
        uploaded_file.save(filepath)

        num_faces, num_masks, num_nomasks = upload_run_ai_and_update_db(user_id, filename_uniq, filepath)
        return jsonify(api_upload_json(num_faces, num_masks, num_nomasks))

    return jsonify(api_error_json(403, 'Unrecognized upload request'))

