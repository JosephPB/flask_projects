from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

# decorators modify function that follows it
# here the decorators create an association between the URL and the function

@app.route('/')
@app.route('/index')
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
    return render_template('index.html', title='Home', user=user, posts=posts)

# add methods attribute to highlight how function now accepts GET and POST requirests
# GET requests return information to the client
# POST requests are typically used when the client submits form data to the server
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # when browser sends GET request to recieve web page with form, validate_on_submit is False
    # when the browser sends POST request after user presses submit button returns True
    # if data is missing then also returns False
    if form.validate_on_submit():
        # flash shows message to the user
        flash('Login request for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        # note: flash messages are stored but not automatically rendered unless shown how to do so by a template - we modify base template for this
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

