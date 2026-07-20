#auth.py

import hashlib
import database

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password):
    password_hash = hash_password(password)
    return database.register(username,password_hash)

def login(username,password):
    password_hash = hash_password(password)
    return database.login(username,password_hash)