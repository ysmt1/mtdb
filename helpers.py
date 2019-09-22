import os
import boto3
import re
from datetime import date

from flask import Flask, session, request, g
from werkzeug.exceptions import abort

from mtdb.database import db

current_date = date.today()
allowed_extensions = ['png','jpg','jpeg','gif']

def calc_days(length, unit):
    """ Calculate amount of days from different measures of time """

    if unit == 'Days' or unit == 'Day':
        return length
    elif unit == 'Weeks' or unit == 'Week':
        return 7*length
    elif unit == 'Months' or unit == 'Month':
        return 30 * length
    elif unit == 'Years' or unit == 'Year':
        return 365 * length

def has_liked(review_id):
    """Return True if logged in user has liked a specific post"""

    if db.execute("SELECT * FROM likes WHERE review_id = :review_id AND user_id = :user_id", {"review_id": review_id, "user_id": g.user['id']}).rowcount > 0:
        return True

def getS3():
    """Get Objects from S3 bucket"""

    bucketName = 'muaythaidb'
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(bucketName)
    
    objects = my_bucket.objects.all()

    return objects

def getImages(gymName, objects):
    """ Get all images from S3 bucket and filter to a certain gym name.  Return a list of image links """
    
    img_links = []
    bucketName = 'muaythaidb'
    
    for obj in objects:
        if any(extension in obj.key for extension in allowed_extensions) and gymName in obj.key:
            url = f'https://{bucketName}.s3.amazonaws.com/{obj.key}'
            url = url.replace(' ', '+')
            img_links.append(url)
            
    return img_links

def delImages(gymName, username, objects):
    """ Delete images from S3 bucket """

    for obj in objects:
        if f'{gymName}/Uploads/{username}' in obj.key:
            obj.delete()


def get_review(id, check_author=True):
    """ Get review details from review id """

    review = db.execute("""SELECT r.id, r.gym_id, r.rating, r.rating_training, r.rating_facility, r.rating_location, r.review, r.review_date, 
                            r.stay_length, user_id, g.gym as gym_name, u.username as username
                            FROM reviews r JOIN users u on r.user_id = u.id JOIN gyms g on r.gym_id = g.id WHERE r.id = :id""", {"id": id}).fetchone() 
    
    if review is None:
        abort(404, "Review id {0} doesn't exist.".format(id))
    
    if check_author and review['user_id'] != g.user['id']:
        abort(403)

    return review

def get_gym(id):
    """ Return object containing review id and gym id from a review id """

    gym = db.execute("SELECT r.id AS review_id, g.id AS gym_id FROM reviews r JOIN gyms g ON r.gym_id = g.id WHERE r.id = :id", {"id": id}).fetchone()
    return gym

def get_gymname(id):
    """ Return gym name from gym id """

    gym = db.execute("SELECT id, gym, location FROM gyms WHERE id = :id", {'id': id}).fetchone()
    return gym['gym']

def allowed_file(filename):
    """ Limit file types that are uploaded to ones in allow_extensions list """

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_filesize(file):
    """ Return a file size in bytes """

    if file.content_length:
        return file.content_length

    try:
        pos = file.tell()
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(pos)
        return size
    except (AttributeError, IOError):
        pass

    return 0

def get_liked_count(review_id):
    """ Return number of likes for a certain review """

    count = db.execute("SELECT COUNT(liked) AS count FROM likes WHERE review_id = :review_id", {"review_id": review_id}).fetchone()

    if count is not None:
        return count['count']
    else:
        return 0

def valid_username(username):
    """ Restrict username to certain length and characters """

    if len(username) < 3 or len(username) > 20 or re.match("^[a-zA-Z0-9_]+$", username) is None:
        return False

    return True

def valid_password(password):
    """ Restrict password to certain length and characters """
    
    if len(password) < 4 or len(password) > 30 or re.match("^[a-zA-Z0-9!@#$%^&*-_=+?<>.]+$", password) is None:
        return False

    return True
