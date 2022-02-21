from email.policy import default
from flask_login import UserMixin
from package import db, login_manager

@login_manager.user_loader
def load_user(user_email):
    return User.query.get(str(user_email))

class User(db.Model, UserMixin):
    email = db.Column(db.String(30), primary_key=True)
    password = db.Column(db.String(50), nullable = False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    watched_movies = db.Column(db.Text, nullable = True)
    def get_id(self):
        return (self.email)

class Movie(db.Model, UserMixin):
    id = db.Column(db.String(100), unique=True, primary_key = True)
    imdb_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable = False)
    original_name = db.Column(db.Text, nullable = False)
    release_year = db.Column(db.String(100), nullable = False)
    posterLink = db.Column(db.Text, unique=True, nullable=False)
    directLink = db.Column(db.Text, unique=True, nullable = False)
    genre = db.Column(db.String(100), nullable = False)
    language = db.Column(db.String(100), nullable = False)
    imdb_rating = db.Column(db.String(100), nullable = False)
    runtime = db.Column(db.String(100), nullable = False)
    is_adult = db.Column(db.Boolean, nullable=False)
    is_archived = db.Column(db.Boolean, nullable=False, default=False)
    watch_count = db.Column(db.String(100), nullable=False, default=0)


class MovieRequest(db.Model, UserMixin):
    id = db.Column(db.String(30), unique=True, primary_key = True)
    imdb_id = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(30), nullable = False)
    original_name = db.Column(db.String(30), nullable = True)
    release_year = db.Column(db.String(10), nullable = False)
