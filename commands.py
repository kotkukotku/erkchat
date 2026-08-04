from protocol import send_json
import database

def handle_nick(conn, new_name, nicknames, lock, broadcast):
    old_nickname = nicknames.get(conn)
    new_user = new_name.strip()
    with lock:
        nick_taken = new_user in nicknames.values()
    if not new_user:
        send_json(conn, {
            "type": "system",
            "text": "Kullanıcı ismi boş olamaz.\n",
        })
        return
    if nick_taken:
        send_json(conn, {
            "type":"system",
            "text": "Bu kullanıcı adı şu an aktif birinde zaten var.\n"
        })
        return
    elif old_nickname == new_user:
        send_json(conn, {
            "type": "system",
            "text": "Lütfen farklı bir kullanıcı adı girin.\n",
        })
        return
    else:
        if database.update_username(old_nickname, new_user):
            with lock:
                nicknames[conn] = new_user
            new_msg = f"{old_nickname} ismini {new_user} olarak değiştirdi."
            send_json(conn, {
                "type": "system",
                "text": "İsminiz değiştirildi.\n",
            })
            broadcast({
                "type": "system",
                "text": new_msg,
            }, conn)
            return
        else:
            send_json(conn,{"type":"system",
            "text":"Bu kullanıcı adı veritabanında kayıtlı.\n"})
def handle_users(conn, nicknames,lock):
    with lock:
        user_list = "\n".join(nicknames.values())
        users_msg = {
            "type": "system",
            "text": f"Online users:\n{user_list}\n",
        }
    send_json(conn,users_msg)

def handle_help(conn):
    help_text = (
        "\nKomutlar:\n"
        "/users: Online kullanıcılar\n"
        "/nick (isim): İsim değiştirir\n"
        "/msg (user) (mesaj): DM'den mesaj atar\n"
        "/whoami: Kullanıcı adı ve rolü gösterir.\n"
        "/ping: Sunucuya ping atıp gecikmeyi ölçer.\n"
        "exit: Çıkış\n"
    )
    send_json(conn, {
        "type": "system",
        "text": help_text,
    })
def handle_whoami(conn,nicknames,role):
    text = f"Kullanıcı adı: {nicknames.get(conn,"Unknown")}\nRol: {role}\n"
    send_json(conn, {
        "type": "system",
        "text": text
    })