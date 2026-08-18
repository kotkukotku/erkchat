#database.py

import sqlite3
from datetime import datetime
from pathlib import Path

db_name = Path(__file__).with_name("chat.db")
DEFAULT_ROOM = "lobby"

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
    CREATE TABLE IF NOT EXISTS odalar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL
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
    imlec.execute(
        "INSERT OR IGNORE INTO odalar (name, created_at) VALUES (?, ?)",
        (DEFAULT_ROOM, datetime.now().strftime("%H:%M"))
    )

    imlec.execute("PRAGMA table_info(mesajlar)")
    columns = [row[1] for row in imlec.fetchall()]
    if "room" not in columns:
        imlec.execute(
            "ALTER TABLE mesajlar ADD COLUMN room TEXT NOT NULL DEFAULT 'lobby'"
        )

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
def add_room(room_name):
    conn = get_connection()
    imlec = conn.cursor()
    saat = datetime.now().strftime("%H:%M")

    imlec.execute(
        "INSERT OR IGNORE INTO odalar (name, created_at) VALUES (?, ?)",
        (room_name, saat)
    )

    conn.commit()
    conn.close()

def get_room_names():
    conn = get_connection()
    imlec = conn.cursor()
    imlec.execute("SELECT name FROM odalar ORDER BY name")
    room_names = [row[0] for row in imlec.fetchall()]
    conn.close()
    return room_names

def add_message(gonderen, mesaj, alici=None, room=DEFAULT_ROOM):
    conn = get_connection()
    imlec = conn.cursor()
    saat = datetime.now().strftime("%H:%M")

    add_room(room)
    sorgu = "INSERT INTO mesajlar (gonderen,mesaj,alici,saat,room) VALUES (?,?,?,?,?)"
    veriler = (gonderen,mesaj,alici,saat,room)
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
def get_last_messages(limit=15, room=None):
    conn = get_connection()
    imlec = conn.cursor()

    if room is None:
        imlec.execute(
            "SELECT gonderen,mesaj,alici,saat,room FROM mesajlar ORDER BY id DESC LIMIT ?",
            (limit,)
        )
    else:
        imlec.execute(
            "SELECT gonderen,mesaj,alici,saat,room FROM mesajlar WHERE room = ? ORDER BY id DESC LIMIT ?",
            (room,limit)
        )
    data = imlec.fetchall()
    conn.close()

    return data[::-1]
