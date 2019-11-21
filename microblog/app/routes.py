from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_password_reset_email
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post

# decorators modify function that follows it
# here the decorators create an association between the URL and the function

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
# in order to require login to view page, use login_required decorator
# redirects to the location assigned in app/__init__.py to the login.login_required function
# in the case of navigating to /index, this makes the complete URL: /login?next=/index, where next indicated where to go after login
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        # but in redirect as otherwise have to deal with how browsers handle refreshes
        # refershes can ask the user if they wish to resibmit the form if a post request with a form submission returns a regular response
        # if using a redirect, the browser is then instructed to send a get request once the form is submitted to grab the page indicated in the redirect, now the last request is not a post and the refresh command works in a more predictable way
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    # using pagination Flask-SQLAlchemy will execute the pagiation class which will limit the number of pages displayed
    # in the thrid flag, if passed True, when an out of range page is requests a 404 error will be returned to the client, if False then an empty list will be returned for out of range pages
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    # pagination has attributes to find the number of the next and previous pages of results (next_num and prev_num respectively) and the existance of previous and next pages can be checked using has_next and has_prev respectively
    # note: when using the url_for function, can add any keyword arguments to it and if the names of those arguments are note references in the URL directly, then Flask will include them in the URL query arguments
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    # using the render_template functino that comes with Jinja2 in Flask
    # note the template file must be in the ./template directory which is not passed here
    return render_template('index.html', title='Home', posts=posts.items, form=form, next_url=next_url, prev_url=prev_url)

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
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestame.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

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
    # pass current_user.username to form as this will be used to check if username change is actually a change or the same before raising duplication error
    form = EditProfileForm(current_user.username)
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

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/explore')
@login_required
def explore():
    # using request.args.get gets the value of the argument in the URL, e.g. .../index?page=1, if no page given then default to 1
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestame.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    # since this page will look a lot like the index page, use the index page as a template to render, but do not want the blog post form and so do not pass this argument
    return render_template("index.html", title='Explore', posts=posts.items,
                          next_url=next_url, prev_url=prev_url)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        # note: flash message about checking email even if it is not found in the database, thus ensuring one cannot query the database for email addresses available
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user)
