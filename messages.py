from datetime import datetime
import database
from protocol import send_json

def handle_message(conn, text, nicknames, lock, broadcast):
    with lock:
        sender = nicknames.get(conn, "Unknown")
    current_time = datetime.now().strftime("%H:%M")
    new_msg = {
        "type": "chat",
        "text": f"[{current_time}] {sender}: {text}",
    }
    database.add_message(sender, text, None)
    broadcast(new_msg,conn)
    send_json(conn,new_msg)
def handle_dm(conn, target_name, text, nicknames, lock, get_nickname):
    target_conn = None
    with lock:
        users = list(nicknames.items())
    for c, name in users:
        if name == target_name:
            target_conn = c
            break
    if target_conn:
        sender = get_nickname(conn)
        sender_msg = {
            "type": "dm",
            "text": f"\n(DM) {sender}: {text}",
        }
        my_msg = {
            "type":"dm",
            "text":f"(DM -> {target_name}): {text}"
        }
        send_json(conn,my_msg)
        send_json(target_conn, sender_msg)
    else:
        send_json(conn, {
            "type": "system",
            "text": "Kullanıcı bulunamadı.",
        })