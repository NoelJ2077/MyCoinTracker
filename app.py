from flask import Flask, render_template, request, redirect, flash, url_for
from classDB import DatabaseManager, DATABASE
from flask import session
from api import BASE_URL
from flask import jsonify
import requests
db = DatabaseManager(DATABASE)
db.create_table()
# insert sample once db is created


app = Flask(__name__)
app.secret_key = 'secret_key'

def loginfirst():
    if 'user_id' not in session:
        flash('Bitte zuerst anmelden')

# default route
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if db.check_username(username):  # prüfen ob der Username bereits existiert
            flash('Benutzername bereits vergeben!') # wird in jinja2 entsprechend angezeigt mit Block
            return redirect(url_for('register'))

        # insert new user into the database
        db.add_user(username, email, password)
        flash('Konto erfolgreich erstellt, bitte anmelden.')
        return redirect(url_for('login'))
    # if is GET eg: if the user is not registered
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.check_credentials(username, password)
        if user:
            session['user_id'] = user[0]  # Der Index 0 enthält die user_id
            # safe email and username for disaplying in navbar
            session['username'] = user[1]
            session['email'] = user[2]
            flash('Anmeldung erfolgreich')
            return redirect(url_for('dashboard'))
        else:
            flash('Falsche Anmeldedaten')
    return render_template('login.html')

@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('email', None)
    # flash message
    session.clear()
    flash('Abmeldung ausgeführt')
    return redirect(url_for('login'))

@app.route('/forgotpw')
def forgotpw():
    flash('This is currently not implemented, sorry! Contact: noelgamemc@gmail.com for help.')
    return render_template('forgotpw.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        loginfirst()
        return redirect(url_for('login'))

    user_id = session['user_id']
    portfolios = db.get_user_portfolios(user_id)

    # Standardmäßig das erste Portfolio auswählen, falls vorhanden
    if 'current_portfolio_id' not in session and portfolios:
        session['current_portfolio_id'] = portfolios[0][0]

    current_portfolio_id = session.get('current_portfolio_id')
    current_portfolio = db.get_portfolio_by_id(current_portfolio_id) if current_portfolio_id else None
    coinpairs = db.get_coinpairs_by_portfolio_id(current_portfolio_id) if current_portfolio_id else None

    return render_template('dashboard.html', portfolios=portfolios, current_portfolio=current_portfolio, coinpairs=coinpairs)


@app.route('/add_portfolio', methods=['POST'])
def add_portfolio():
    # check if user is logged in
    if 'user_id' not in session:
        loginfirst()
        return redirect(url_for('login'))

    portfolio_name = request.form.get('portfolio_name')
    if portfolio_name:
        flash('Portfolio ' + portfolio_name + ' Erstellt!')
        db.add_portfolio(session['user_id'], portfolio_name)
        # load the new portfolio
        session['current_portfolio_id'] = db.get_user_portfolios(session['user_id'])[-1][0]


    return redirect(url_for('dashboard'))

@app.route('/change_portfolio', methods=['POST'])
def change_portfolio():
    if 'user_id' not in session:
        loginfirst()
        return jsonify(success=False, message="User not logged in"), 401

    portfolio_id = request.form.get('portfolio_id')
    if portfolio_id:
        session['current_portfolio_id'] = portfolio_id
    return redirect(url_for('dashboard'))

@app.route('/rename_portfolio', methods=['POST'])
def rename_portfolio():
    if 'user_id' not in session:
        flash("Please log in to continue.")
        return redirect(url_for('login'))
    user_id = session['user_id']
    portfolio_id = request.form.get('portfolio_id')
    new_name = request.form.get('new_name')
    if portfolio_id and new_name:
        db.rename_portfolio(user_id, portfolio_id, new_name)
        flash("Portfolio renamed successfully.")
    return redirect(url_for('dashboard'))

# route to add a coinpair to the current portfolio
@app.route('/delete_portfolio', methods=['POST'])
def delete_portfolio():
    if 'user_id' not in session:
        loginfirst()
        return jsonify(success=False, message="User not logged in"), 401

    user_id = session['user_id']
    portfolio_id = request.form.get('portfolio_id')
    if portfolio_id:
        db.delete_portfolio(user_id, portfolio_id)
    # Löschen des Portfolios aus der Session, wenn es das aktuelle Portfolio ist
    if 'current_portfolio_id' in session and session['current_portfolio_id'] == portfolio_id:
        flash('Portfolio deleted')
        del session['current_portfolio_id']

    return redirect(url_for('dashboard'))

# delete_coinpair route
@app.route('/delete_coinpair', methods=['POST'])
def delete_coinpair():
    if 'user_id' not in session:
        return jsonify(success=False, message="User not logged in"), 401

    coinpair = request.form.get('coinpair')
    if coinpair:
        db.delete_coinpair(session['current_portfolio_id'], coinpair)

    return jsonify(success=True, message="Coinpair deleted successfully")

# add_coinpair route
@app.route('/add_coinpair', methods=['POST'])
def add_coinpair():
    if 'user_id' not in session:
        loginfirst()
        return jsonify(success=False, message="User not logged in"), 401
    # get the coinpair from the form
    coinpair = request.form.get('coinpair')
    # check if coinpair is not empty
    print(f"checkpair: {coinpair}")
    if coinpair:
        db.add_coinpair(session['current_portfolio_id'], coinpair)
    return redirect(url_for('dashboard'))

@app.route('/api/coinpairs')
def get_coinpairs():
    response = requests.get(BASE_URL + 'AssetPairs')
    if response.status_code == 200:
        data = response.json()
        print(data)  # Fügen Sie dies hinzu, um die Struktur der Antwort zu überprüfen.
        # Nun überprüfen Sie, ob 'result' in data vorhanden ist.
        if 'result' in data:
            # Extrahieren Sie die Coin-Pairs aus der Antwort und formatieren Sie sie als Liste
            coinpairs = [{'name': key, 'value': value} for key, value in data['result'].items()]
            return jsonify(coinpairs=coinpairs)
        else:
            # Falls 'result' nicht vorhanden ist, geben Sie die gesamte Antwort zurück
            return jsonify(data)
    else:
        return jsonify(error="Failed to fetch coinpairs"), response.status_code

@app.route('/api/search_coinpairs')
def search_coinpairs():
    query = request.args.get('query', '')  # Get the query parameter
    response = requests.get('https://api.kraken.com/0/public/AssetPairs')
    if response.status_code == 200:
        data = response.json()
        if 'error' in data and data['error']:
            return jsonify(error=data['error']), 400
        if 'result' in data:
            # Filter the pairs based on the query
            filtered_pairs = {k: v for k, v in data['result'].items() if query.lower() in k.lower()}
            coinpairs = [{'name': k, 'altname': v['altname']} for k, v in filtered_pairs.items()]
            return jsonify(coinpairs=coinpairs)
        else:
            return jsonify(error="No results found"), 404
    else:
        return jsonify(error="Failed to fetch coinpairs"), response.status_code














if __name__ == '__main__':
    app.run(debug=True)

