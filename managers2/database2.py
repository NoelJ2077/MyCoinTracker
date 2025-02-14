from managers2.config2 import DatabaseManager, DATABASE2
import sqlite3, os, hashlib, uuid

class DBManager:
    # create a connection to the SQLite database and a cursor object
    def __init__(self, db_name=DATABASE2):
        self.db_manager = DatabaseManager(db_name)
        self.cursor = self.db_manager.cursor
    
    def create_tb(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
            userID INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL)
            created_at TEXT NOT NULL)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Portfolios (
            portfolioID INTEGER PRIMARY KEY,
            userID INTEGER,
            portfolioName TEXT NOT NULL,
            FOREIGN KEY(userID) REFERENCES Users(userID))''') 
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Tickers (
            tickerID INTEGER PRIMARY KEY,
            tickerSym TEXT UNIQUE)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS PortfolioTickers (
            portfolioTickerID INTEGER PRIMARY KEY,
            portfolioID INTEGER,
            tickerID INTEGER,
            FOREIGN KEY(portfolioID) REFERENCES Portfolios(portfolioID),
            FOREIGN KEY(tickerID) REFERENCES Tickers(tickerID))''')
        
        self.db_manager.conn.commit()

        