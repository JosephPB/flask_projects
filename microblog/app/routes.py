from flask import render_template
from app import app

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

