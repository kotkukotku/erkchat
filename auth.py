#auth.py

import hashlib
import database
import json
from protocol import send_json

def handle_client_auth(conn, f, nicknames, lock, broadcast):
    while True:
        raw = f.readline()

        if not raw:
            return None, None

        try:
            data = json.loads(raw.strip())
        except json.JSONDecodeError:
            continue

        if data.get("type") != "auth":
            continue

        action = data.get("action")
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        if not username or not password:
            send_json(conn, {
                "type": "auth_response",
                "success": False,
                "message": "Kullanıcı adı veya şifre boş olamaz."
            })
            continue

        if action == "register":

            if register(username, password):
                send_json(conn, {
                    "type": "auth_response",
                    "success": True,
                    "message": "Kayıt başarılı! Şimdi giriş yapın."
                })

            else:
                send_json(conn, {
                    "type": "auth_response",
                    "success": False,
                    "message": "Hata: Kullanıcı adı zaten alınmış."
                })

            continue
        elif action == "login":

            role = login(username, password)

            if not role:
                send_json(conn, {
                    "type": "auth_response",
                    "success": False,
                    "message": "Hatalı kullanıcı adı veya şifre!"
                })
                continue


            with lock:
                if username in nicknames.values():

                    send_json(conn, {
                        "type": "auth_response",
                        "success": False,
                        "message": "Bu hesap şu an zaten aktif!"
                    })

                    continue

                nicknames[conn] = username


            send_json(conn, {
                "type": "auth_response",
                "success": True,
                "message": f"Giriş Başarılı!"
            })


            return username, role
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password):
    password_hash = hash_password(password)
    return database.register(username,password_hash)

def login(username,password):
    password_hash = hash_password(password)
    return database.login(username,password_hash)