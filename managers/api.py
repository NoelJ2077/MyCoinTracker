# KRAKEN API V2
import requests
# API URL KRAKEN
BASE_URL = 'https://api.kraken.com/0/public/Ticker?pair='
# Error url -> create new issue with {e} as title
ERRORURL = 'https://github.com/NoelJ2077/MyCoinTracker/issues/new'

# get coins from the API with input data
def get_coinpair_data(coinpair):
    response = requests.get(BASE_URL + coinpair)
    if response.status_code == 200:
        data = response.json()
        # Check if there are no errors and the coinpair exists in the result
        if not data['error'] and coinpair in data['result']:
            return data['result'][coinpair]
    return None

# check if the coinpair exists in the API
def api_checkpair(coinpair):
    try:
        response = requests.get(BASE_URL + coinpair)
        if response.status_code == 200:
            data = response.json()
            # Prüfen Sie, ob es keine Fehler gibt und das Resultat den gesuchten Coinpair enthält
            if not data['error'] and coinpair in data['result']:
                return True
            else:
                return False
        else:
            print(f"Error with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# from raw to: 1'000.00, 10'000.00 etc... | <= 999 = not changed
def fetchthousand(value):
    # convert the value to a float
    try:
        num = float(value)
    except ValueError:
        # If the value is not a number, return it as is
        return value
    
    # If the number is greater than or equal to 1000
    if num >= 1000:
        # example output: 1'000.00, 10'000.00 etc...
        # make 2 nachkommastellen
        num = round(num, 2)
        # format the number with a comma as a thousands separator apostrphe  eg: 1'000.00
        return f"{num:,.2f}".replace(',', "'")
    
    else:
        # If the number is less than 1000, return it is from JSON response
        return f"{num:.8f}".rstrip('0').rstrip('.') if '.' in value else str(int(num))

# export the portfolios as a JSON file
def export_json(portfolios):

    export_data = []
    
    for portfolio in portfolios:
        # Überprüfen, ob 'coinpairs' ein Schlüssel im Dictionary ist und eine Liste ist
        if 'coinpairs' in portfolio and isinstance(portfolio['coinpairs'], list):
            coinpair_list = portfolio['coinpairs']
        else:
            coinpair_list = []
        
        # Erstellen Sie das Dictionary für das aktuelle Portfolio
        export_data.append({
            "portfolio_id": portfolio['portfolio_id'],
            "user_id": portfolio['user_id'],
            "portfolio_name": portfolio['portfolio_name'],
            "coinpair": coinpair_list
        })
    return export_data

