# MyCoinTracker - A small Simple Crypto Tracker
A simple Crypto Coin tracker with the Kraken V2 API 
No warranty, but you can open a issue if you find bugs!

# To read the structure properly, open the README file in "code" mode -> https://github.com/NoelJ2077/MyCoinTracker/blob/main/README.md?plain=1
# Project Structure from Root dir (watch this File as "code")
MyCoinTracker/
    __pychache__
    /managers
        -config.py
        -cointracker.db
        -UserManager.py
        -PortfolioManager.py
        -api.py
    /static
        -js
        -ico
        -css
    /templates
        -base.html
        -all html fails
    -gitignore
    -app.py
    -LICENSE
    -README.md
    -rMain.py
    -rUser.py

# Login credentials (you could also just register new user's)
username: TestUser1
password: asdf

# All required Tools can be installed with pip
[https://pypi.org/project/pip/] 
pip install packagename

# Kraken V2 API Documentation
[https://docs.kraken.com/rest/]

# required tools:
Python3.10.xx
Flask
Flask-Assets
Flask-Login
Flask-WTF
