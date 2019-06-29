from flask import Flask
from config import Config

#name variable is a Python prededined variable set to the name of the module in which it is used
app = Flask(__name__)
app.config.from_object(Config)

#routes module is imported below as it imports from the app variable assigned above
from app import routes
#routes are different URLs that the application implements
