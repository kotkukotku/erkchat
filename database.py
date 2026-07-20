#database.py

import sqlite3
from datetime import datetime

db_name = "chat.db"

def get_connection():
    return sqlite3.connect(db_name)
def init_db():
    conn = get_connection()
    imlec = conn.cursor()
    
    imlec.execute("""
    CREATE TABLE IF NOT EXISTS mesajlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gonderen TEXT NOT NULL,
        mesaj TEXT NOT NULL,
        alici TEXT,
        saat TEXT NOT NULL                 
)
""")
    imlec.execute("""
    CREATE TABLE IF NOT EXISTS kullanicilar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        rol TEXT NOT NULL DEFAULT 'user'            
)
""")
    conn.commit()
    conn.close()
def register(username,password_hash):
    conn = get_connection()
    imlec = conn.cursor()
    try:
        sorgu = "INSERT INTO kullanicilar (username, password_hash) VALUES (?,?)"
        veriler = (username,password_hash)
        imlec.execute(sorgu,veriler)
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        print("Kullanıcı adı zaten var.")
        conn.close()
        return False
def login(username, password_hash):
    conn = get_connection()
    imlec = conn.cursor()
    sorgu = "SELECT rol from kullanicilar WHERE username = ? AND password_hash = ?"
    veriler = (username,password_hash)
    
    imlec.execute(sorgu,veriler)
    sonuc = imlec.fetchone()
    conn.close()
    if sonuc:
        return sonuc[0]
    return None
def add_message(gonderen, mesaj, alici=None):
    conn = get_connection()
    imlec = conn.cursor()
    saat = datetime.now().strftime("%H:%M")

    sorgu = "INSERT INTO mesajlar (gonderen,mesaj,alici,saat) VALUES (?,?,?,?)"
    veriler = (gonderen,mesaj,alici,saat)
    imlec.execute(sorgu,veriler)
    
    conn.commit()
    conn.close()
def update_username(old_username,new_username):
    conn = get_connection()
    imlec = conn.cursor()
    try:
        imlec.execute("UPDATE kullanicilar SET username = ? WHERE username = ?",(new_username,old_username))
        
        if imlec.rowcount == 0:
            conn.close()
            return False
        imlec.execute("UPDATE mesajlar SET gonderen = ? WHERE gonderen = ?",(new_username,old_username))
        imlec.execute("UPDATE mesajlar SET alici = ? WHERE alici = ?", (new_username, old_username))

        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False
def get_last_messages(limit=15):
    conn = get_connection()
    imlec = conn.cursor()

    imlec.execute("SELECT gonderen,mesaj,alici,saat FROM mesajlar ORDER BY id DESC LIMIT ?", (limit,))
    data = imlec.fetchall()
    conn.close()

    return data[::-1]