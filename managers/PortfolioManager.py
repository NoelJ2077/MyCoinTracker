# PortfolioManager.py
import sqlite3, uuid
from flask import flash
from managers.api import api_checkpair
from managers.config import DATABASE, DatabaseManager, getdate

class PortfolioManager:

    def __init__(self, db_name=DATABASE):
        self.db_manager = DatabaseManager(db_name)
        self.cursor = self.db_manager.cursor
    
    # create the tables if they don't exist
    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL)''')
        self.db_manager.conn.commit()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS portfolio (
            portfolio_id TEXT PRIMARY KEY,
            user_id TEXT,
            portfolio_name TEXT NOT NULL,
            coinpair TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id))''')
        self.db_manager.conn.commit()

    # user_id will be taken from the session from the call to this function
    def add_portfolio(self, user_id, portfolio_name):
            portfolio_id = str(uuid.uuid4())
            created_at = getdate()
            self.cursor.execute('''
                INSERT INTO portfolio (portfolio_id, user_id, portfolio_name, created_at)
                VALUES (?, ?, ?, ?)
            ''', (portfolio_id, user_id, portfolio_name, created_at))
            self.db_manager.conn.commit()
    
    # delete a portfolio from the db
    def delete_portfolio(self, user_id, portfolio_id):
        self.cursor.execute('''
            DELETE FROM portfolio WHERE user_id=? AND portfolio_id=?
        ''', (user_id, portfolio_id))
        self.db_manager.conn.commit()

    # rename a portfolio
    def rename_portfolio(self, user_id, portfolio_id, new_name):
        self.cursor.execute('''
            UPDATE portfolio SET portfolio_name=? WHERE user_id=? AND portfolio_id=?
        ''', (new_name, user_id, portfolio_id))
        self.db_manager.conn.commit()
    
    # fetch a portfolio by its id
    def get_portfolio_by_id(self, portfolio_id):
        self.cursor.execute('''
            SELECT portfolio_id, portfolio_name , created_at FROM portfolio WHERE portfolio_id=?
        ''', (portfolio_id,))
        return self.cursor.fetchone()
    
    # fetch all coinpairs based on portfolios of user_id
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

    # fetch all portfolios of user_id
    def get_user_portfolios(self, user_id):
        self.cursor.execute('''SELECT portfolio_id, portfolio_name, coinpair, created_at FROM portfolio WHERE user_id=?''', (user_id,))
        return self.cursor.fetchall()
    
    # add a coinpair to the current portfolio
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
            self.db_manager.conn.commit()
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
                self.db_manager.conn.commit()
                flash("Ticker erfolgreich entfernt.")

