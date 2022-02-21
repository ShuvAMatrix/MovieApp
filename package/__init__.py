from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('/')
load_dotenv(os.path.join(project_folder, '.env'))

app = Flask(__name__)
app.config['SECRET_KEY'] = "918916ff978d6d51bcb433f758e25d38f51d4b6c"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tasks.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
imdb_title_prefix = "https://www.imdb.com/title/"
imdb_image_prefix = "https://image.tmdb.org/t/p/w500"
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from package import route