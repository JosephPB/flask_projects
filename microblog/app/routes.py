from app import app

# decorators modify function that follows it
# here the decorators create an association between the URL and the function

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"
