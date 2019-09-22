import os

from flask import Flask, session, render_template, request, redirect, url_for, g
from flask_session import Session
import redis

def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY","prod")
    # Configure session to use filesystem
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_REDIS"] = redis.from_url(os.environ.get("REDIS_URL"))
    app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024
    Session(app)

    from mtdb import auth
    app.register_blueprint(auth.bp)

    from mtdb import main_app
    app.register_blueprint(main_app.bp)
    app.add_url_rule('/', endpoint='index')

    from mtdb import database
    database.init_app(app)

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return render_template('error.html'), 413

    return app