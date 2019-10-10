from hashlib import md5
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
# import UserMixin class from Flask-Login which includes generic implementations for the four required items needed by Flask-Login and are appropriate for most standard database modes
from flask_login import UserMixin
import time
import jwt
from app import app

# Flask-Login needs application's help in loading a user. Extension expects application to configure a user loader function, that can be called to load a user given the ID
# The user loader is registered with Flask-Login with a decorator
@login.user_loader
def load_user(id):
    'The ID passed to the function is going to be a string and so it needs to be converted to an int'
    return User.query.get(int(id))

# to store the relationship between followers and those who are followe, create a table that stores all os the followers
# this table is not in a model class since it only contains foreign keys
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

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
    
    followed = db.relationship(
        # User is the right side entity of the relationship (the left side entity is the parent class). Since this is self-referential, same class if used on both sides
        # secondary configures association table configured below outside the class
        'User', secondary=followers,
        # primaryjoin is the condition that links the left side with the association table
        # followers.c.follower_id references the follower_id column of the assocation table
        primaryjoin = (followers.c.follower_id == id),
        # secondaryjoin indicates the column that links the right side entity
        secondaryjoin = (followers.c.followed_id == id),
        # backref defiens how the relationship will be ccessed from the right side entity. From the left side, relationship is named followed, so from the right side using the name followers to represent all the left side users that are linked to the target user in the right side.
        # in general, lazy = 'dynamic', as in posts, sets up the query to not run until specifically requested
        backref = db.backref('followers', lazy='dynamic'), lazy = 'dynamic')
    
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

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        'return timestamp ordered posts of those followed'
        # first, create a database join, merging by the post and followers tables by the condition that the ids of those being followed by a follower matches the id of the writer of the post - this gives a table of all posts, the, who wrote them and then person who followers that person
        # second, retrieve all the posts where the person who follows that person is self
        # finally, order by timestamp - using .desc() orders in descending order
        # note, handling things using database calls like this can be much more efficient than by doing it in individual steps such as: finding all the people one followers, retieveing all their blog posts and then timestamp ordering
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        # also retieve all of self posts for display
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestame.desc())
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8') # decoding necessary since wkt returns token as a byte sequence

    # a static method means that the function can e invoked directly from the class
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id=jwt.decode(token, app.config['SECRET_KEY'],
                          algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestame = db.Column(db.Integer, index=True, default=datetime.utcnow)
    # note is it good to work with utc time as then they are alway the same for the user and will be formatted into local time whereever the user is
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
