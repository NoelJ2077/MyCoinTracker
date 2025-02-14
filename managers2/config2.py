# /managers2/config_poly.py
import os, sqlite3
from pathlib import Path

config_path = Path(__file__).resolve().parent
project_root = config_path.parent
DATABASE2 = os.path.join(project_root, 'managers', 'polydb.db')

class DatabaseManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON") # enable foreign key support
        self.conn.commit() # commit the changes


