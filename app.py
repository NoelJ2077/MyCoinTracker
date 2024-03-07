from flask import Flask, render_template, request, redirect, flash, url_for
from flask.helpers import send_file #for export json file
from classDB import DatabaseManager, DATABASE
from flask import session, jsonify
from io import BytesIO
from api import BASE_URL, get_coinpair_data, fetchthousand, export_json
import requests, json
db = DatabaseManager(DATABASE)
db.create_table()
#app.py

app = Flask(__name__)
app.secret_key = 'secret_key'


""" USER MANAGEMENT START"""
def loginfirst():
    if 'user_id' not in session:
        flash('Bitte zuerst anmelden')

# app route for 127.0.0.1 - - [07/Mar/2024 20:53:50] "GET /someshit HTTP/1.1" 404 - || Redirect to /login with flash
@app.errorhandler(404)
def page_not_found(e):
    flash('Vorherige URL existierte nicht!')
    return redirect(url_for('login'))


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
""" USER MANAGEMENT END"""
# blank
""" DASHBOARD"""
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

    current_portfolio_id = session.get('current_portfolio_id') if 'current_portfolio_id' in session else None 
    current_portfolio = db.get_portfolio_by_id(current_portfolio_id) if current_portfolio_id else None
    coinpairs = db.get_coinpairs_by_portfolio_id(current_portfolio_id) if current_portfolio_id else None

    # coinpair_info wird ein leeres Dictionary sein, wenn keine Coinpairs vorhanden sind
    coinpair_info = {}
    try:
        if coinpairs:
            for cp in coinpairs:
                data = get_coinpair_data(cp)
                if data:
                    # Extrahiere die benötigten Informationen aus der API-Antwort und formatiere die Zahlen.
                    coinpair_info[cp] = {
                        'last_trade_price': fetchthousand(data['c'][0]),
                        'volume': fetchthousand(data['v'][0]),
                        'low_price': fetchthousand(data['l'][0]),
                        'high_price': fetchthousand(data['h'][0]),
                        'opening_price': fetchthousand(data['o']),
                        # Da es keinen 'close' in der API gibt, verwende den letzten Handelspreis.
                        'closing_price': fetchthousand(data['c'][0])
                    }
    
                
        return render_template('dashboard.html', portfolios=portfolios, current_portfolio=current_portfolio, coinpairs=coinpairs, coinpair_info=coinpair_info)
    except Exception as e:
            print(e)
""" DASHBOARD END"""
# blank
""" PORTFOLIO MANAGEMENT START"""
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
""" PORTFOLIO MANAGEMENT END"""
# blank
""" COINPAIR MANAGEMENT START"""
@app.route('/delete_coinpair', methods=['POST'])
def delete_coinpair():
    if 'user_id' not in session or 'current_portfolio_id' not in session:
        loginfirst()
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    portfolio_id = session['current_portfolio_id']
    coinpair = request.form.get('coinpair')
    
    if coinpair:
        # Use remove_pair instead of delete_coinpair
        db.remove_pair(user_id, portfolio_id, coinpair)
    
    return redirect(url_for('dashboard'))

@app.route('/add_coinpair', methods=['POST'])
def add_coinpair():
    if 'user_id' not in session:
        loginfirst()
        return jsonify(success=False, message="User not logged in"), 401
    # create variable for coinpair
    coinpair = request.form.get('coinpair_search')
    portfolio_id = request.form.get('portfolio_id')
    if coinpair:
        db.add_coinpair(portfolio_id, coinpair)
    return redirect(url_for('dashboard'))

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
""" COINPAIR MANAGEMENT END"""
# blank
""" API ENDPOINTS"""
@app.route('/api/coinpairs') # get all coinpairs
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

@app.route('/export_portfolio', methods=['POST'])
def export_portfolio():
    if 'current_portfolio_id' in session:
        portfolio_id = session['current_portfolio_id']
        user_id = session['user_id']
        # Fetch the portfolio data from the database, which seems to return a tuple
        current_portfolio_data = db.get_portfolio_by_id(portfolio_id)
        
        if isinstance(current_portfolio_data, tuple):
            portfolio_dict = {
                'portfolio_id': current_portfolio_data[0],
                'user_id': user_id,
                'portfolio_name': current_portfolio_data[1],
                'coinpairs': []  # Initialize coinpairs as an empty list
            }
            
            # Fetch coinpairs for the current portfolio from the database
            coinpairs_data = db.get_coinpairs_by_portfolio_id(portfolio_id)
            if coinpairs_data:
                for coinpair in coinpairs_data:
                    portfolio_dict['coinpairs'].append(coinpair)
            else:
                print("No coinpairs found for the current portfolio.")

            export_data = export_json([portfolio_dict])

            # Write to a buffer
            buffer = BytesIO()
            buffer.write(json.dumps(export_data).encode('utf-8'))
            buffer.seek(0)

            # Trigger file download
            return send_file(
                buffer,
                as_attachment=True,
                download_name='portfolio.json',
                mimetype='application/json'
            )
        else:
            print(f"Unexpected data type: {type(current_portfolio_data)}")
            return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)

