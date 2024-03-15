import sqlite3, uuid, hashlib, os
from flask import flash
from api import api_checkpair
DATABASE = 'cointracker.db'
# for when portfolio is created
def getdate(): # get date in format: dd:mm:yyyy hh:mm:ss
    import datetime
    return datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

class DatabaseManager:
    
    # create a connection to the SQLite database and a cursor object
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON") # enable foreign key support
        self.conn.commit() # commit the changes

    # create the tables if they don't exist
    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL)''')
        self.conn.commit()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS portfolio (
            portfolio_id TEXT PRIMARY KEY,
            user_id TEXT,
            portfolio_name TEXT NOT NULL,
            coinpair TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id))''')
        self.conn.commit()

    # hash the password & create a new salt
    def hash_password(self, password):
        salt = os.urandom(32)  # Erstellen Sie ein neues Salz
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return salt + hashed_password  # Speichern Sie das Salz zusammen mit dem Hash

    # hash the password with the salt
    def salt_password(self, password, salt):
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    
    # insert a new user into the db
    def add_user(self, username, email, password):
        user_id = str(uuid.uuid4())
        password_hash = self.hash_password(password)
        self.cursor.execute('''INSERT INTO users (user_id, username, email, password) VALUES (?, ?, ?, ?)''', (user_id, username, email, password_hash))
        self.conn.commit()
        return user_id
        
    # fetch username from the db
    def check_username(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        return self.cursor.fetchone() is not None
    
    # check user credentials
    def check_credentials(self, username, password):
        self.cursor.execute('''SELECT user_id, username, email, password FROM users WHERE username=?''', (username,))
        user = self.cursor.fetchone()
        if user:
            user_id, username, email, password_hash = user
            salt = password_hash[:32]  # Die ersten 32 Bytes des Hashes sind das Salz
            actual_hash = password_hash[32:]  # Der Rest ist der Hash
            new_hash = self.salt_password(password, salt)
            if new_hash == actual_hash:
                return user_id, username, email  # Benutzer-ID wird zurückgegeben, wenn das Passwort übereinstimmt
        return None

    """PORTFOLIO FUNCTIONS"""
    # user_id will be taken from the session from the call to this function
    def add_portfolio(self, user_id, portfolio_name):
            portfolio_id = str(uuid.uuid4())
            created_at = getdate()
            self.cursor.execute('''
                INSERT INTO portfolio (portfolio_id, user_id, portfolio_name, created_at)
                VALUES (?, ?, ?, ?)
            ''', (portfolio_id, user_id, portfolio_name, created_at))
            self.conn.commit()
    
    # delete a portfolio from the db
    def delete_portfolio(self, user_id, portfolio_id):
        self.cursor.execute('''
            DELETE FROM portfolio WHERE user_id=? AND portfolio_id=?
        ''', (user_id, portfolio_id))
        self.conn.commit()

    # rename a portfolio
    def rename_portfolio(self, user_id, portfolio_id, new_name):
        self.cursor.execute('''
            UPDATE portfolio SET portfolio_name=? WHERE user_id=? AND portfolio_id=?
        ''', (new_name, user_id, portfolio_id))
        self.conn.commit()
    
    # fetch a portfolio by its id
    def get_portfolio_by_id(self, portfolio_id):
        self.cursor.execute('''
            SELECT portfolio_id, portfolio_name , created_at FROM portfolio WHERE portfolio_id=?
        ''', (portfolio_id,))
        return self.cursor.fetchone()
    
    # fetch a portfolio and its coinpairs by portfolio id ^^^ above
    def get_coinpairs_by_portfolio_id(self, portfolio_id):
        self.cursor.execute('''
            SELECT coinpair FROM portfolio WHERE portfolio_id=?
        ''', (portfolio_id,))
        row = self.cursor.fetchone()

        # Check if row is not None and if coinpair is not empty
        if row and row[0]:
            # Split by comma to get coinpairs and filter out any empty strings
            coinpairs = row[0].split(',')
            # Remove empty strings that can be caused by trailing commas
            return [coinpair for coinpair in coinpairs if coinpair.strip()]
        else:
            # If there is no coinpair or it's empty, return an empty list
            flash("Dieses Portfolio enthält noch keine Ticker!")
            return []

    # fetch all portfolios from the db and store them in a list and store each coinpair to each portfolio
    def get_user_portfolios(self, user_id):
        self.cursor.execute('''SELECT portfolio_id, portfolio_name, coinpair, created_at FROM portfolio WHERE user_id=?''', (user_id,))
        return self.cursor.fetchall()
    

    """COINPAIR FUNCTIONS"""
    def add_coinpair(self, portfolio_id, coinpair):
        try:
            # Retrieve the user id from portfolio_id
            self.cursor.execute('''SELECT user_id FROM portfolio WHERE portfolio_id=? LIMIT 1''', (portfolio_id,))
            user_id = self.cursor.fetchone()
            if not user_id:
                print("Kein Benutzer gefunden.")
                return False
            # check if the coinpair is valid value = TRUE || FALSE
            if not api_checkpair(coinpair):
                flash("Dieser Ticker ist ungültig.")
                return False
            
            # Check if the coinpair already exists exactly as it is ! attentation: pairs are comma separated
            self.cursor.execute('''SELECT coinpair FROM portfolio WHERE portfolio_id=?''', (portfolio_id,))
            result = self.cursor.fetchone()
            if result and result[0]:
                coinpairs = result[0].split(',')
                if coinpair in coinpairs:
                    flash("Dieser Ticker ist bereits in diesem Portfolio enthalten.")
                    return False
            
            # Add the coinpair to the portfolio
            self.cursor.execute('''UPDATE portfolio SET coinpair=IFNULL(coinpair, '') || ? WHERE portfolio_id=?''', (coinpair + ',', portfolio_id))
            self.conn.commit()
            flash("Ticker erfolgreich hinzugefügt.")
            return True
        except Exception as e:
            print("Ein Fehler ist aufgetreten:", e)
            return False





    # remove a coinpair from a specific portfolio
    def remove_pair(self, user_id, portfolio_id, coinpair):
        self.cursor.execute('''SELECT coinpair FROM portfolio WHERE user_id=? AND portfolio_id=?''', (user_id, portfolio_id))
        result = self.cursor.fetchone()
        if result and result[0]:
            coinpairs = result[0].split(',')
            if coinpair in coinpairs:
                coinpairs.remove(coinpair)
                updated_coinpairs = ','.join(coinpairs)
                self.cursor.execute('''UPDATE portfolio SET coinpair=? WHERE user_id=? AND portfolio_id=?''', (updated_coinpairs, user_id, portfolio_id))
                self.conn.commit()
                flash("Ticker erfolgreich entfernt.")

