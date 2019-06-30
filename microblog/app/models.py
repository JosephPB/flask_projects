from datetime import datetime
from app import db

class User(db.Model):
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

    def __repr__(self):
        'Tells Python how to print objects of this class) - useful for debugging'
        return '<User {}>'.format(self.username)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestame = db.Column(db.Integer, index=True, default=datetime.utcnow)
    # note is it good to work with utc time as then they are alway the same for the user and will be formatted into local time whereever the user is
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
