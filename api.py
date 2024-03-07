# KRAKEN API V2
import requests, json
from flask import session
from classDB import DatabaseManager, DATABASE
# API URL
BASE_URL = 'https://api.kraken.com/0/public/Ticker?pair='


# fetch the coinpair data from the Kraken API
def get_coinpair_data(coinpair):
    response = requests.get(BASE_URL + coinpair)
    return response.json()

