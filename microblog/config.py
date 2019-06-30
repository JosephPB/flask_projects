import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    '''
    There are various ways of storing config variables, including explicitly defining them as keys in app.config.
    A way of keeping them separated is to use a Confid class which will then be called and in which all config variables can be stored. You can also have sub-classes in which sub-config variables can be stored
    '''

    # SECRET_KEYS are hard to guess guys which will usually be pased in as environments to protect we forms against Cross0Site Request Forgery
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    # set to False the feature which signals the application every time a change is about to be made in the database which is not needed
    SQLALCHEMY_TRACK_MODIFICATIONS = False
