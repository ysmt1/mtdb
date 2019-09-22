import os
import boto3
import mtdb.helpers as helpers

from flask import Flask, session, render_template, request, redirect, url_for, g, Blueprint, flash, current_app, jsonify
from flask_session import Session
from werkzeug.utils import secure_filename

from mtdb.auth import login_required
from mtdb.database import db

bp = Blueprint('main_app', __name__)

@bp.route("/")
def index():
    """Route for homepage. 
    
    Query DB for all gyms w/info to display in table
    """

    gyms = db.execute("""SELECT gyms.id, gyms.gym, locations.city, ROUND(AVG(reviews.rating)::numeric,1) as average,
                         COUNT(reviews.rating) as count, SUM(reviews.stay_days) as sum_days FROM gyms JOIN locations on locations.id = gyms.location
                        LEFT JOIN reviews on gyms.id = reviews.gym_id GROUP BY gyms.id, locations.city ORDER BY gyms.gym""").fetchall()
                        
    return render_template("main_app/index.html", gyms = gyms)

@bp.route("/gyms/<int:gym_id>")
def gym(gym_id):
    """Route for specific gym page

    Get all ratings, in addition to all images associated with the gym
    """

    gym = db.execute("SELECT * FROM gyms JOIN locations ON locations.id = gyms.location WHERE gyms.id = :id", {"id": gym_id}).fetchone()
    if gym is None:
        return render_template("error.html", message = "Gym does not exist")

    ratings = db.execute("""SELECT gym_id, reviews.rating, reviews.rating_training, reviews.rating_facility, 
                            reviews.rating_location, reviews.review, reviews.review_date, users.username, 
                            users.id AS userid, reviews.stay_length, reviews.id AS reviewid, COUNT(likes.liked) as count
                            FROM reviews 
                            JOIN users ON users.id = reviews.user_id 
                            LEFT JOIN likes ON reviews.id = likes.review_id
                            WHERE gym_id = :gym_id 
                            GROUP BY reviews.id, users.username, users.id
                            ORDER BY reviews.review_date DESC""", {"gym_id": gym_id}).fetchall()
    
    s3objects = helpers.getS3()
    images = helpers.getImages(gym['gym'], s3objects)

    return render_template("main_app/gym.html", gym = gym, ratings = ratings, func = helpers.has_liked, images = images)

@bp.route("/reviewgym", methods = ["POST", "GET"])
@login_required
def reviewgym():
    """Route to review gym page

    Validate all inputs and if images are attached,
    Make sure images are of valid size and type
    """

    gyms = db.execute("SELECT * FROM gyms ORDER BY gym").fetchall()

    if request.method == "POST":
        
        error = None
        units_of_time = ['Days', 'Weeks', 'Months', 'Years']

        gym_id = int(request.form.get("gym_id"))
        review = request.form.get("review")
        unit_stay = request.form.get('unit_stay')
        ratings_form_name = ["rate_training", "rate_facility", "rate_locationcost", "rate_overall"]
        ratings_dict = {}
        files = request.files.getlist('upload-image')

        if db.execute("SELECT * FROM gyms WHERE id = :id", {"id": gym_id}).rowcount == 0:
            error = "No gym with that ID"

        if not unit_stay in units_of_time:
            error =  "Please choose a unit of time"
        elif not review:
            error = "No Review Provided!"

        try:
            length_stay = int(request.form.get('length_stay'))
            if length_stay == 0:
                raise ValueError
        except ValueError:
            error = "Invalid Length of Stay!"

        for rating in ratings_form_name:
            if request.form.get(rating):
                try:
                    rating_input = int(request.form.get(rating))
                    if not 0 <= rating_input <= 5:
                        raise ValueError
                except ValueError:
                    error = "Invalid rating!"
                else:
                    ratings_dict[rating] = rating_input
            else:
                error = "Please include all ratings!"
        
        if error is None:

            if files:

                file_size_list = [helpers.get_filesize(file) for file in files]
                if sum(file_size_list) > 15728640:
                    flash('Your images have exceeded the maximum combined total size (15mb)', 'error')
                    return render_template("main_app/reviewpage.html", gyms = gyms)

                client = boto3.client('s3')
                bucket = 'muaythaidb'

                for file in files:
                    if helpers.get_filesize(file) > 3145728:
                        flash(f'{file.filename} is too large', 'error')
                        return render_template("main_app/reviewpage.html", gyms = gyms)

                    if not helpers.allowed_file(file.filename):
                        flash(f'{file.filename} is not a valid filetype', 'error')
                        return render_template("main_app/reviewpage.html", gyms = gyms)

                    filename = secure_filename(file.filename)
                    gym_name = helpers.get_gymname(gym_id)
                    client.upload_fileobj(file, bucket, f"{gym_name}/Uploads/{g.user['username']}/{filename}")

            if length_stay == 1:
                unit_stay = unit_stay[:-1]

            total_stay = str(length_stay) + ' ' + unit_stay
            stay_days = helpers.calc_days(length_stay, unit_stay)

            db.execute("""INSERT INTO reviews (rating, review, gym_id, review_date, user_id, rating_training, rating_facility, rating_location, stay_length, stay_days) 
                        VALUES (:rating, :review, :gym_id , :review_date, :user_id, :rating_training, :rating_facility, :rating_location, :stay_length, :stay_days)""", 
                        {"rating": ratings_dict["rate_overall"], "review": review, "gym_id": gym_id, "review_date": helpers.current_date, "user_id": g.user['id'], 
                        "rating_training": ratings_dict["rate_training"], "rating_facility": ratings_dict["rate_facility"], 
                        "rating_location": ratings_dict["rate_locationcost"], "stay_length": total_stay, "stay_days": stay_days})
            db.commit()

            flash('You have successfully posted a review', category='success')
            return redirect(url_for('index'))

        flash(error, 'error')

    return render_template("main_app/reviewpage.html", gyms = gyms)
    
@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Route to delete review
    Delete any images associated with review
    """

    review = helpers.get_review(id)
    
    s3_objects = helpers.getS3()
    helpers.delImages(review['gym_name'], review['username'], s3_objects)

    db.execute("DELETE FROM reviews WHERE id = :id", {"id": id})
    db.commit()
    flash('Review Deleted!', category='success')
    return redirect(url_for('index'))

@bp.route('/<int:id>/update', methods = ["POST", "GET"])
@login_required
def update(id):
    """Route to update review"""

    old_review = helpers.get_review(id)

    if request.method == "POST":
        
        error = None
        units_of_time = ['Days', 'Weeks', 'Months', 'Years']

        gym_id = old_review['gym_id']
        review = request.form.get("review")
        unit_stay = request.form.get('unit_stay')
        ratings_form_name = ["rate_training", "rate_facility", "rate_locationcost", "rate_overall"]
        ratings_dict = {}

        if not unit_stay in units_of_time:
            error = "Please choose a unit of time"
        elif not review:
            error = "No Review Provided!"

        try:
            length_stay = int(request.form.get('length_stay'))
        except ValueError:
            error = "Invalid Length of Stay!"

        for rating in ratings_form_name:
            if request.form.get(rating):
                try:
                    rating_input = int(request.form.get(rating))
                    if not 0 <= rating_input <= 5:
                        raise ValueError
                except ValueError:
                    error =  "Invalid rating!"
                else:
                    ratings_dict[rating] = rating_input
            else:
                error = "Please include all ratings!"

        if error is None:

            if length_stay == 1:
                unit_stay = unit_stay[:-1]

            total_stay = str(length_stay) + ' ' + unit_stay
            stay_days = helpers.calc_days(length_stay, unit_stay)
        
            db.execute("""UPDATE reviews SET rating = :rating, review = :review, gym_id = :gym_id, review_date = :review_date, user_id = :user_id, 
                        rating_training = :rating_training, rating_facility = :rating_facility, rating_location = :rating_location, stay_length = :stay_length, stay_days = :stay_days
                        WHERE id = :id""", 
                        {"rating": ratings_dict["rate_overall"], "review": review, "gym_id": gym_id, "review_date": helpers.current_date, "user_id": g.user['id'], 
                        "rating_training": ratings_dict["rate_training"], "rating_facility": ratings_dict["rate_facility"], 
                        "rating_location": ratings_dict["rate_locationcost"], "stay_length": total_stay, "stay_days": stay_days, "id": id})
            
            db.commit()
            
            flash('Review Edited!', category='success')

            return redirect(url_for('index'))

        flash(error, 'error')

    return render_template("main_app/update.html", old_review = old_review)

@bp.route('/user/edit/<username>', methods = ["POST","GET"])
@login_required
def edit_user_profile(username):
    """Route to edit user profile"""

    profile = db.execute("""SELECT users.id, username, name, email, users.location, experience, fighter, checkin, gyms.gym as gymname
                             FROM users LEFT JOIN gyms on users.checkin = gyms.id WHERE username = :username""", 
                            {"username": username}).fetchone()
    gyms = db.execute("SELECT id, gym FROM gyms ORDER BY gym").fetchall()

    if request.method == "POST":

        error = None

        form_items = ["realname","email","location","experience","fighter", "checkin"]
        form_dict = {}

        for item in form_items:

            form_input = request.form.get(item)

            if not form_input or form_input == '':
                form_input = None

            form_dict[item] = form_input

        if error is None:

            db.execute("UPDATE users SET name = :name, email = :email, location = :location, experience = :experience, fighter = :fighter, checkin = :checkin WHERE username = :username", 
            {"name": form_dict["realname"], "email": form_dict["email"], "location":form_dict["location"], "experience":form_dict["experience"], "checkin":form_dict["checkin"], "fighter":form_dict["fighter"], "username": username})
            db.commit()

            flash('Profile Updated!', category='success')

            return redirect(url_for('main_app.edit_user_profile', username = username))

    return render_template("main_app/editprofile.html", profile = profile, gyms = gyms)

@bp.route('/user/view/<username>', methods = ["GET"])
@login_required
def view_user_profile(username):
    """Route to view user profile"""

    profile = db.execute("""SELECT users.id, username, name, email, users.location, experience, fighter, checkin, gyms.gym as gymname
                             FROM users LEFT JOIN gyms on users.checkin = gyms.id WHERE username = :username""", 
                            {"username": username}).fetchone()
                            
    if profile is None:
        flash("User does not exist", 'error')

    return render_template("main_app/viewprofile.html", profile = profile)

@bp.route('/<int:id>/like', methods=['POST'])
@login_required
def like_review(id):
    """Route to like a review
    
    Return a JSON object to update like counter asynchronously
    """

    error = None
    user_id = session.get('user_id')

    if db.execute("SELECT * FROM likes WHERE review_id = :review_id AND user_id = :user_id", {"review_id": id, "user_id": user_id}).rowcount != 0:
        error = "You already liked this review!"

    if error is None:
        db.execute("INSERT INTO likes (review_id, user_id, liked) VALUES (:review_id, :user_id, :liked)", {"review_id": id, "user_id": user_id, "liked": "1"})
        db.commit()

        like_count = helpers.get_liked_count(id)

        return jsonify({'success': like_count})

    return jsonify({'error': error})
    
@bp.route('/<int:id>/unlike', methods=['POST'])
@login_required
def unlike_review(id):
    """Route to unlike a review
    
    Return a JSON object to update like counter asynchronously
    """

    error = None
    user_id = session.get('user_id')

    if db.execute("SELECT * FROM likes WHERE review_id = :review_id AND user_id = :user_id", {"review_id": id, "user_id": user_id}).rowcount == 0:
        error = "You have not liked this review!"

    if error is None:
        db.execute("DELETE FROM likes WHERE review_id = :review_id AND user_id = :user_id", {"review_id": id, "user_id": user_id})
        db.commit()

        like_count = helpers.get_liked_count(id)

        return jsonify({'success': like_count})

    return jsonify({'error': error})