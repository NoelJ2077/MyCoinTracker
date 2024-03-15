# app.py
from flask import Flask, flash, render_template
from rUser import db, user
from rMain import main

db.create_table()

app = Flask(__name__) # register flask app with app blueprint
app.register_blueprint(user, url_prefix='/user') # register blueprint with FLask object
app.register_blueprint(main, url_prefix='/') # register blueprint with FLask object
app.secret_key = 'use a secret key here!'

# forgotpw btn
@app.route('/forgotpw')
def forgotpw():
    flash('This is currently not implemented, sorry! Contact: co0095426@gmail.com for help.')
    return render_template('forgotpw.html')
 
# 404 error page 
@app.errorhandler(404)
def page_not_found(e):
    flash('Vorherige URL existierte nicht!')
    return render_template('404.html'), 404

@app.errorhandler(405)
def method_not_allowed(e):
    flash('The method is not allowed for the requested URL.')
    return render_template('405.html'), 405

# launch the app
if __name__ == '__main__':
    # print routes
    #print(app.url_map)
    # listening on all local IPv4 addresses
    app.run(host='0.0.0.0', port=5000, debug=True)

