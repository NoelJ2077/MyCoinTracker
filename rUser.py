# rUser.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from managers.config import DATABASE, DatabaseManager
from managers.UserManager import UserManager
from managers.api import ERRORURL
import os
# create a new instance of the DatabaseManager class
db = UserManager(DATABASE)

user = Blueprint('user', __name__, static_folder="static", template_folder="templates")

# rUser.py
@user.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            if db.check_username(username):  # prüfen ob der Username bereits existiert
                flash('Benutzername bereits vergeben!') # wird in jinja2 entsprechend angezeigt mit Block
                return redirect(url_for('user.register'))

            # insert new user into the database
            db.add_user(username, email, password)
            flash('Konto erfolgreich erstellt, bitte anmelden.')
            return redirect(url_for('user.login'))
        # if is GET eg: if the user is not registered
        return render_template('register.html')
    except Exception as e:
        print(f"Error in register: {e}")
        return redirect(ERRORURL)
    
@user.route('/login', methods=['GET', 'POST'])
def login():
    
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user_info = db.check_credentials(username, password)
            if user_info:
                session['user_id'] = user_info[0]  # Der Index 0 enthält die user_id
                # safe email and username for disaplying in navbar
                session['username'] = user_info[1]
                session['email'] = user_info[2]
                flash('Anmeldung erfolgreich')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Falsche Anmeldedaten')
                return redirect(url_for('user.login'))
        # print if login.html was found
        print(f"Path for login.html: {os.path.join(user.template_folder, 'login.html')}")
        return render_template('login.html')
    
@user.route('/logout')
def logout():
    try:
        # remove the username from the session if it is there
        session.pop('user_id', None)
        session.pop('username', None)
        session.pop('email', None)
        session.clear()
        flash('Abmeldung ausgeführt')
        return redirect(url_for('user.login'))
    except Exception as e:
        print(f"Error in logout: {e}")
        return redirect(ERRORURL)
    

