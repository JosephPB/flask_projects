import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap

# name variable is a Python prededined variable set to the name of the module in which it is used
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app) # database
migrate = Migrate(app, db) # migration engine
login = LoginManager(app)
# to be able to give certain pages that he user must login to see, Flask-Login needs to know what the view function is that handles logins - pass the login page to login.login_view
login.login_view = 'login'
mail = Mail(app)
# bootstrap is the flask_bootstap extension that gives a ready to use base template
# flask is also fully compatible with CSS classes and bootstrap.min.js etc.
bootstap = Bootstrap(app)

# routes module is imported below as it imports from the app variable assigned above
from app import routes, models, errors
# routes are different URLs that the application implements
# models will define the structure of the database


if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    # keep a log file
    if not os.path.exists('logs'):
        os.mkdir('logs')
    # RotatingGileHandler keeps logs up to a maximum amout and the last backupCount number of logs
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')
