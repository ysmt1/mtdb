import functools
import os
import mtdb.helpers as helpers

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from mtdb.database import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route("/register", methods = ["POST", "GET"])
def register():
    """Route to register user.

    Check if username already exists, and 
    check if username/password has valid characters and length
    """

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        error = None

        if not username:
            error = "No username provided!"
        elif not helpers.valid_username(username):
            error = "Invalid Username! (Only letters, numbers and underscores allowed)"
        elif not password:
            error = "No password provided!"
        elif not helpers.valid_password(password):
            error = "Invalid Password!"
        elif db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 1:
            error =  f"Sorry, username {username} already taken"

        if error is None:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", 
                {"username":username, "password": generate_password_hash(password)})

            db.commit()
            
            session.clear()

            flash('Successful Registration!', category='success')
            
            return redirect(url_for('index'))     
        
        flash(error, 'error')

    return render_template("auth/register.html")
     
@bp.route("/login", methods = ["POST", "GET"])
def login():
    """Login route

    Check if user exists and if password correct
    If login successful, store user in session
    """

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        error = None

        user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()

        if user is None:
            error =  f"Username: {username} does not exist"
        elif not check_password_hash(user['password'], password):
            error =  "Incorrect password"

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            flash('Successful Login!', category='success')
            return redirect(url_for('index'))

        flash(error, 'error')

    return render_template("auth/login.html")
       
@bp.before_app_request
def load_logged_in_user():
    """Load logged in user before each request"""

    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db.execute('SELECT * FROM users WHERE id = :id', {"id" : user_id}).fetchone()


@bp.route('/logout')
def logout():
    """Logout user by clearing session"""
    
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    """Limit routes with login_requred decorator to logged in users"""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return render_template("error.html", message = "Must be logged in!")

        return view(**kwargs)

    return wrapped_view