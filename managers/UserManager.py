import sqlite3, os, hashlib, uuid
from managers.config import DatabaseManager, DATABASE
from managers2.services import getdate, hashdata, salts

class UserManager:
    # create a connection to the SQLite database and a cursor object
    def __init__(self, db_name=DATABASE):
        self.db_manager = DatabaseManager(db_name)
        self.cursor = self.db_manager.cursor

    # create the tables if they don't exist
    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
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
        self.db_manager.conn.commit()
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

