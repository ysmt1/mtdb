import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.environ.get("DATABASE_URL", None):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.environ.get("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def close_db(e=None):
    db.remove()

def init_app(app):
    app.teardown_appcontext(close_db)