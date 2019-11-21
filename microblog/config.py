import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    '''
    There are various ways of storing config variables, including explicitly defining them as keys in app.config.
    A way of keeping them separated is to use a Config class which will then be called and in which all config variables can be stored. You can also have sub-classes in which sub-config variables can be stored
    '''

    # SECRET_KEYS are hard to guess guys which will usually be pased in as environments to protect we forms against Cross-Site Request Forgery
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    # set to False the feature which signals the application every time a change is about to be made in the database which is not needed
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # for error handling - want to be notified by email
    # if email setting are not given int he environment then assume that email error handling should be disabled
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    POSTS_PER_PAGE = 3
    LANGUAGES = ['en', 'es']
