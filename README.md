# MyCoinTracker - A small Simple Crypto Tracker
A simple Crypto Coin tracker with the Kraken V2 API 
No warranty, but you can open a issue if you find bugs!

# Project Structure from Root
MyCoinTracker/
    __pychache__
    /static
        -js
        -ico
        -css
    /templates
        -base.html
        -all html fails
    -gitignore
    -api.py     ["api_interactions"]
    -app.py     [/forgotpw,/{e}]
    classDB.py  
    cointracker.db
    LICENSE
    README.md
    rMain.py    [/dashboard,/add_portfolio,/add_coinpair,/change_portfolio,/rename_portfolio,/delete_portfolio,/delete_coinpair,/delete_portfolio,/export_portfolio,/api/search_coinpairs]
    rUser.py    [/login,/register,/logout]

# Login credentials for test (you could also just register)
username: TestUser1
password: asdf

# CSS is not yet optimized for small screens!
Will change in the future

# All required Tools can be installed with pip
[https://pypi.org/project/pip/] 
pip install packagename

# Kraken V2 API Documentation
[https://docs.kraken.com/rest/]

# Programming Lang. 
Python3

# Flask Framework Tools
Flask,
Flask-Login,
Flask-WTF

# System 
Requests,
SQLite3,
uuid,
hashlib,
os,
