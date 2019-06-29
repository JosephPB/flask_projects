from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# name variable is a Python prededined variable set to the name of the module in which it is used
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app) # database
migrate = Migrate(app, db) # migration engine

# routes module is imported below as it imports from the app variable assigned above
from app import routes, models
# routes are different URLs that the application implements
# models will define the structure of the database
