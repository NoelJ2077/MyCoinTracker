# rMain.py
from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, send_file, session, request
from io import BytesIO
from classDB import DATABASE, DatabaseManager
from api import ERRORURL, get_coinpair_data, fetchthousand, export_json
import json, requests

db = DatabaseManager(DATABASE)
main = Blueprint('main', __name__, static_folder="static", template_folder="templates")

# check if user is logged in
def userIDset():
    if 'user_id' not in session:
        flash('Bitte zuerst anmelden')
        return False
    return True

# dashboard with user required
@main.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Check if the user is logged in
    if not userIDset():
        return redirect(url_for('user.login'))

    user_id = session['user_id']
    portfolios = db.get_user_portfolios(user_id)
    coinpairs = None
    current_portfolio = None  # Initialize current_portfolio

    # Default to the first portfolio if it exists
    if 'current_portfolio_id' not in session and portfolios:
        session['current_portfolio_id'] = portfolios[0][0]

    # Fetch current portfolio and coinpairs
    current_portfolio_id = session.get('current_portfolio_id')
    if current_portfolio_id:
        try:
            current_portfolio = db.get_portfolio_by_id(current_portfolio_id)
            coinpairs = db.get_coinpairs_by_portfolio_id(current_portfolio_id)
        except Exception as e:
            print(f"Error fetching portfolio data: {e}")
            return redirect(ERRORURL + f"?title=Error fetching portfolio data: {e}")

    # Fetch coinpair information via API
    coinpair_info = {}
    if coinpairs:
        try:
            for cp in coinpairs:
                data = get_coinpair_data(cp)
                if data:
                    # Extract and format the necessary information from the API response
                    coinpair_info[cp] = {
                        'last_trade_price': fetchthousand(data['c'][0]),
                        'volume': fetchthousand(data['v'][0]),
                        'low_price': fetchthousand(data['l'][0]),
                        'high_price': fetchthousand(data['h'][0]),
                        'opening_price': fetchthousand(data['o']),
                        'closing_price': fetchthousand(data['c'][0])  # Use last trade price as closing price
                    }
        except Exception as e:
            print(f"Error fetching coinpair data: {e}")
            return redirect(ERRORURL + f"?title=Error fetching coinpair data: {e}")
        
    # return render with the data:
    return render_template('dashboard.html', portfolios=portfolios, current_portfolio=current_portfolio, coinpairs=coinpairs, coinpair_info=coinpair_info)
    
# add portfolio btn
@main.route('/add_portfolio', methods=['POST'])
def add_portfolio():
    try:
        # check if user is logged in
        userIDset()

        portfolio_name = request.form.get('portfolio_name')
        if portfolio_name:
            db.add_portfolio(session['user_id'], portfolio_name)
            # load the new portfolio
            session['current_portfolio_id'] = db.get_user_portfolios(session['user_id'])[-1][0]
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        print(f"Error in add_portfolio: {e}")
        return redirect(ERRORURL)

# add coinpair btn
@main.route('/add_coinpair', methods=['POST'])
def add_coinpair():
    try:
        userIDset()
        # create variable for coinpair
        coinpair = request.form.get('coinpair_search')
        portfolio_id = request.form.get('portfolio_id')
        if coinpair:
            db.add_coinpair(portfolio_id, coinpair)
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        print(f"Error in add_coinpair: {e}")
        return redirect(ERRORURL)
       
# change current portfolio btn
@main.route('/change_portfolio', methods=['POST'])
def change_portfolio():
    try:
        userIDset()
        portfolio_id = request.form.get('portfolio_id')
        if portfolio_id:
            session['current_portfolio_id'] = portfolio_id
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        print(f"Error in change_portfolio: {e}")
        return redirect(ERRORURL)

# rename portfolio btn
@main.route('/rename_portfolio', methods=['POST'])
def rename_portfolio():
    try:
        userIDset()
        user_id = session['user_id']
        portfolio_id = request.form.get('portfolio_id')
        new_name = request.form.get('new_name')
        if portfolio_id and new_name:
            db.rename_portfolio(user_id, portfolio_id, new_name)
            flash("Portfolio Erfolgreich umbenannt")
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        print(f"Error in rename_portfolio: {e}")
        return redirect(ERRORURL)
    
# delete coinpair btn
@main.route('/delete_coinpair', methods=['POST'])
def delete_coinpair():
    try:
        userIDset()
        
        user_id = session['user_id']
        portfolio_id = session['current_portfolio_id']
        coinpair = request.form.get('coinpair')
        
        if coinpair:
            # Use remove_pair instead of delete_coinpair
            db.remove_pair(user_id, portfolio_id, coinpair)
        
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        print(f"Error in delete_coinpair: {e}")
        return redirect(ERRORURL)

# delete portfolio btn
@main.route('/delete_portfolio', methods=['POST'])
def delete_portfolio():
    try:
        userIDset()
        user_id = session['user_id']
        portfolio_id = request.form.get('portfolio_id')
        if portfolio_id:
            db.delete_portfolio(user_id, portfolio_id)
        # Löschen des Portfolios aus der Session, wenn es das aktuelle Portfolio ist
        if 'current_portfolio_id' in session and session['current_portfolio_id'] == portfolio_id:
            flash('Portfolio deleted')
            del session['current_portfolio_id']

        return redirect(url_for('main.dashboard'))
    except Exception as e:
        print(f"Error in delete_portfolio: {e}")
        return redirect(ERRORURL)  
    
# export btn
@main.route('/export_portfolio', methods=['POST'])
def export_portfolio():
    try:
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
                # Write the JSON data to the buffer
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
                return redirect(url_for('main.dashboard'))
        else:
            return redirect(url_for('main.dashboard'))
    except Exception as e:
        print(f"Error in export_portfolio: {e}")
        return redirect(ERRORURL)

# talk to API to get coinpairs dropdown
@main.route('/api/search_coinpairs')

# listener after 2 CHAR input in search bar
def search_coinpairs():
    try:  
        query = request.args.get('query', '')  # Get the query parameter
        # require a query parameter eg: /api/search_coinpairs?query=ethusdt to work
        if not query:
            return jsonify(error="No query parameter provided"), 400
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
    except Exception as e:
        print(f"Error in search_coinpairs: {e}")
        return jsonify(error="An error occurred"), 500

