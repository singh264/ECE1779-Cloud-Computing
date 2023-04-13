from flask import render_template, session, redirect, request

from app import app
from app.models import get_db


@app.route("/history", methods=["GET", "POST"])
def image_history():
    '''
    Description:  looks up all the images uploaded by the user in the database, categorizes them into 4 different 
    lists, and outputs the image list depending on the list selected by the user
    
    Returns: renders the History page template "home/history.html"
    '''
    
    if 'user' not in session:
        return redirect("/sign-in")

    cnx = get_db()
    cursor = cnx.cursor()
    query = '''SELECT img_location, faces_detected, faces_with_masks, faces_without_masks
               FROM Images
               WHERE user_id = %s
            '''
    cursor.execute(query, (session['user']['uid'], ))

    images = cursor.fetchall()

    # define 4 lists
    # images with no faces detected
    img_list1 = []
    # images where all faces have masks
    img_list2 = []
    # images where no faces have masks
    img_list3 = []
    # images where some faces have masks
    img_list4 = []

    for image in images:
        filepath, num_faces, num_masks, num_nomasks = image
        imgurl  = '/static' + filepath.split('static')[1]
        imgdata = [imgurl, num_faces, num_masks, num_nomasks]
        if num_faces == 0:
            img_list1.append(imgdata)
        elif num_faces == num_masks:
            img_list2.append(imgdata)
        elif num_faces == num_nomasks:
            img_list3.append(imgdata)
        else:
            img_list4.append(imgdata)


    if request.method == "POST":
        category = request.form.get("history_category", None)
        if category != None:
            if category == 'list1' and len(img_list1)>0:
                return render_template("home/history.html", image_list=img_list1, history_category=category)
            elif category == 'list2' and len(img_list2)>0:
                return render_template("home/history.html", image_list=img_list2, history_category=category)
            elif category == 'list3' and len(img_list3)>0:
                return render_template("home/history.html", image_list=img_list3, history_category=category)
            elif category == 'list4' and len(img_list4)>0:
                return render_template("home/history.html", image_list=img_list4, history_category=category)
            else:
                return render_template("home/history.html", image_list=None, history_category=category)

    return render_template("home/history.html")
