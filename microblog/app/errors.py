from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    # 500 error occur when there is a database error, meaning that you want to undo changes made to the database so that they don't interfere with other session - apply rollback
    db.session.rollback()
    return render_template('500.html'), 500
