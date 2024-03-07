import sqlite3, uuid, hashlib, os
from flask import Flask, render_template, request, redirect
from flask import session
DATABASE = 'cointracker.db'

class DatabaseManager:
    
    # create a connection to the SQLite database and a cursor object
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON") # enable foreign key support
        self.conn.commit() # commit the changes

    # Erstellen der Benutzer-, Portfolio- und Coinpair-Tabellen
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
            FOREIGN KEY(user_id) REFERENCES users(user_id))''')
        self.conn.commit()

    # hash password with bcrypt
    def hash_password(self, password):
        salt = os.urandom(32)  # Erstellen Sie ein neues Salz
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return salt + hashed_password  # Speichern Sie das Salz zusammen mit dem Hash

    # salt the password
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
    
    # fetch user from the db
    def get_user_by_id(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return self.cursor.fetchone()
    
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
            self.cursor.execute('''
                INSERT INTO portfolio (portfolio_id, user_id, portfolio_name)
                VALUES (?, ?, ?)
            ''', (portfolio_id, user_id, portfolio_name))
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
            SELECT portfolio_id, portfolio_name FROM portfolio WHERE portfolio_id=?
        ''', (portfolio_id,))
        return self.cursor.fetchone()
    
    # fetch all portfolios from the db
    def get_coinpairs_by_portfolio_id(self, portfolio_id):
        self.cursor.execute('''
            SELECT coinpair FROM portfolio WHERE portfolio_id=?
        ''', (portfolio_id,))
        return self.cursor.fetchone()
    
    
    # fetch all coinpairs from the db
    def get_user_portfolios_with_coinpairs(self, user_id):
        self.cursor.execute('''SELECT p.portfolio_id, p.portfolio_name, c.coinpair 
                            FROM portfolio p
                            LEFT JOIN coinpairs c ON p.portfolio_id = c.portfolio_id
                            WHERE p.user_id=?''', (user_id,))
        return self.cursor.fetchall()
    
    # fetch all portfolios from the db and store them in a list and store each coinpair to each portfolio
    def get_user_portfolios(self, user_id):
        self.cursor.execute('''SELECT portfolio_id, portfolio_name, coinpair FROM portfolio WHERE user_id=?''', (user_id,))
        return self.cursor.fetchall()
    

    """COINPAIR FUNCTIONS"""
    def add_coinpair(self, user_id, coinpair):
        print("Adding coinpair to portfolio")
        try:
            # Retrieve the user's portfolio id 
            self.cursor.execute('''SELECT portfolio_id FROM portfolio WHERE user_id=? LIMIT 1''', (user_id,))
            portfolio = self.cursor.fetchone()
            if not portfolio:
                print("Kein Portfolio gefunden.")
                return False

            portfolio_id = portfolio[0]
            # Check if the coinpair already exists
            self.cursor.execute('''SELECT * FROM coinpairs WHERE portfolio_id=? AND coinpair=?''', (portfolio_id, coinpair))
            if self.cursor.fetchone():
                print("Coinpair existiert bereits.")
                return False

            # Add the coinpair to the user's portfolio
            self.cursor.execute('''INSERT INTO coinpairs (portfolio_id, coinpair) VALUES (?, ?)''', (portfolio_id, coinpair))
            self.conn.commit()
            return True
        except Exception as e:
            print("Ein Fehler ist aufgetreten:", e)
            return False





    # remove a coinpair from a specific portfolio
    def remove_pair(self, user_id, coinpair):
        self.cursor.execute('''SELECT coinpair FROM portfolio WHERE user_id=?''', (user_id,))
        result = self.cursor.fetchone()
        if result and result[0]:
            coinpairs = result[0].split(',')
            coinpairs.remove(coinpair)
            updated_coinpairs = ','.join(coinpairs)
            self.cursor.execute('''UPDATE portfolio SET coinpair=? WHERE user_id=?''', (updated_coinpairs, user_id))
            self.conn.commit()

    

    
    
    


    



        
