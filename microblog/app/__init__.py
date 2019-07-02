from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# name variable is a Python prededined variable set to the name of the module in which it is used
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app) # database
migrate = Migrate(app, db) # migration engine
login = LoginManager(app)
# to be able to give certain pages that he user must login to see, Flask-Login needs to know what the view function is that handles logins - pass the login page to login.login_view
login.login_view = 'login'

# routes module is imported below as it imports from the app variable assigned above
from app import routes, models
# routes are different URLs that the application implements
# models will define the structure of the database
