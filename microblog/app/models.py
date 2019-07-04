from hashlib import md5
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
# import UserMixin class from Flask-Login which includes generic implementations for the four required items needed by Flask-Login and are appropriate for most standard database modes
from flask_login import UserMixin

# Flask-Login needs application's help in loading a user. Extension expects application to configure a user loader function, that can be called to load a user given the ID
# The user loader is registered with Flask-Login with a decorator
@login.user_loader
def load_user(id):
    'The ID passed to the function is going to be a string and so it needs to be converted to an int'
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    '''
    The class inherits from db.Model, which is a base class for all models from Flask-SQLAlchemy. It defines several fields as class variables. Fields are created as instances of the db.Column class, which takes the field type as an argument, plus other optional arguments that, for examples, allowthe indication of which fields are uniques and indexed, which is important so that database searches are effieicnt
    '''
    
    # indexing is set to True for database fields that can be looked up
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # this is not an actuayl database field, but a high-leel view of the relationship between users and posts
    # backref argument defines the name of a field that will be added to the objects of the "many" class that points back to the "one" object (in a "many-to-one" relationship
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        'Tells Python how to print objects of this class) - useful for debugging'
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        'Pulls in an avatar, if registered on Gravatar, or, alternatively, generates an identicon'
        # input is an MD5 hash which is generated from lowering the email address, converting it to bytes and then passing it into the hash function
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestame = db.Column(db.Integer, index=True, default=datetime.utcnow)
    # note is it good to work with utc time as then they are alway the same for the user and will be formatted into local time whereever the user is
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
