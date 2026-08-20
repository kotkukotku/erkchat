#auth.py

import hashlib
import database
import json
import secrets
from protocol import send_json

def handle_client_auth(conn, f, nicknames, lock, broadcast):
    while True:
        raw = f.readline()

        if not raw:
            return None, None, None

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

            user_id, role = login(username, password)

            if not user_id:
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


            return username, user_id, role
def hash_password(password,salt):
    return hashlib.scrypt(password.encode("utf-8"),salt=salt, n=16384,r=8,p=1).hex()

def register(username, password):
    salt = secrets.token_bytes(16)
    password_hash = hash_password(password,salt)
    return database.register(username,password_hash, salt.hex())

def login(username, password):
    creds = database.get_user_credentials(username)
    if not creds:
        return None, None
    stored_hash, salt = creds
    password_hash = hash_password(password, bytes.fromhex(salt))
    res = database.login(username, password_hash)
    if not res:
        return None, None
    return res