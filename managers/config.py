# managers/config.py
import sqlite3, os, datetime
from pathlib import Path

config_path = Path(__file__).resolve().parent
project_root = config_path.parent
DATABASE = os.path.join(project_root, 'managers', 'database.db')

def getdate(): # get date in format: dd:mm:yyyy hh:mm:ss
    return datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

class DatabaseManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON") # enable foreign key support
        self.conn.commit() # commit the changes


# struct of the managers:
""" UserManager.py
class UserManager:

def __init__(self, db_name=DATABASE):
        self.db_manager = DatabaseManager(db_name)
        self.cursor = self.db_manager.cursor
def create_table(self)
def hash_password(self, password)
def salt_password(self, password, salt)
def add_user(self, username, email, password)
def check_username(self, username)
def check_credentials(self, username, password)

PortfolioManager.py
class PortfolioManager:

def __init__(self, db_name=DATABASE):
        self.db_manager = DatabaseManager(db_name)
        self.cursor = self.db_manager.cursor
def create_table(self)
def add_portfolio(self, user_id, portfolio_name)
def delete_portfolio(self, user_id, portfolio_id)
def rename_portfolio(self, user_id, portfolio_id, new_name)
def get_portfolio_by_id(self, portfolio_id)
"""
