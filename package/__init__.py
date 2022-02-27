from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

app = Flask(__name__)

#Normal config
uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri

#For connecting postgres
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")

#For local database upgrade
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tasks.db"

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
OMDB_API_KEY = os.environ.get("OMDB_API_KEY")
imdb_title_prefix = "https://www.imdb.com/title/"
imdb_image_prefix = "https://image.tmdb.org/t/p/w500"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
SQLALCHEMY_TRACK_MODIFICATIONS = False
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from package import route
from package.commands import createAdmin, dropnCreateDb, createUser, initialize

app.cli.add_command(createAdmin)
app.cli.add_command(dropnCreateDb)
app.cli.add_command(createUser)
app.cli.add_command(initialize)