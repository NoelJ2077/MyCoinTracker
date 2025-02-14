import uuid, hashlib, os


def getdate(): # get date in format: dd:mm:yyyy hh:mm:ss
    import datetime
    return datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

def hashdata(data):
    salt = os.urandom(32)  # create a new salt
    hashed_data = hashlib.pbkdf2_hmac('sha256', data.encode(), salt, 100000)
    return salt + hashed_data  # store the salt together with the hash

def salts(data, salt):
    return hashlib.pbkdf2_hmac('sha256', data.encode(), salt, 100000)


