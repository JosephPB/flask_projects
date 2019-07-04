from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User

# decorators modify function that follows it
# here the decorators create an association between the URL and the function

@app.route('/')
@app.route('/index')
# in order to require login to view page, use login_required decorator
# redirects to the location assigned in app/__init__.py to the login.login_required function
# in the case of navigating to /index, this makes the complete URL: /login?next=/index, where next indicated where to go after login
@login_required
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Averngers movie was so cool!'
        }
    ]
    # using the render_template functino that comes with Jinja2 in Flask
    # note the template file must be in the ./template directory which is not passed here
    return render_template('index.html', title='Home', posts=posts)

# add methods attribute to highlight how function now accepts GET and POST requirests
# GET requests return information to the client
# POST requests are typically used when the client submits form data to the server
@app.route('/login', methods=['GET', 'POST'])
def login():
    # In case user who is already logged in tries to go back to login page redirct to index
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()

    # when browser sends GET request to recieve web page with form, validate_on_submit is False
    # when the browser sends POST request after user presses submit button returns True
    # if data is missing then also returns False
    if form.validate_on_submit():
        # query database by username
        # calling first completes query - know that the`re will either be 0 or 1 results returned
        # have used .all() in place of .first() before but
        # if username does not exist, then returns None
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        # request.args presentes content of the information the client sent as a dictionary
        next_page = request.args.get('next')
        # check if next_page has a value, or if ir does have a value, that the page is relative and not absoluted
        # not allowing absolute paths makes the site more secure as an attacker could input a malicious site in the next argument
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        # else return to the next_page
        return redirect(next_page)
        # flash shows message to the user
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# when a route has a dynamic component, Flask will accept any test in that portion of the URL, and will invoke the view function with the actual text as an argument               
@app.route('/user/<username>')
@login_required
def user(username):
    # useing first_or_404 saves having to check if the query returned a usere in order to find ot if the user exists as if returns None then show 404
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

# before_request decorator regusters view funcytion to be used before any view function in an application
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        # no ned to have db/session.add() before commit as referencing current_user, Flask-Login will invoke the user loader callback function, which wil run a database query that will put the target user in the database session, so you can add the user again in this function, but it is not necessary becuase it is already there
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    # validate_on_submit might return False if browser just sent a GET request, which needs to be responded to be providing an initial version of the form template, or it can be when the browser sends a POST request with form data, but something in that data is invalid
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    # if form is being requested with a GET requiest, wan to pre-populate the fields with the data that is stored in the databse
    # by checking request.method, it will be GET for the initial request, and POST for a submission and therefore will separate some errors
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
