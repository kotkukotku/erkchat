from datetime import datetime
import database
from protocol import send_json

def handle_message(conn, text, nicknames, user_ids, lock, broadcast_room, room_name):
    with lock:
        sender = nicknames.get(conn, "Unknown")
        sender_id = user_ids.get(conn)
    current_time = datetime.now().strftime("%H:%M")
    new_msg = {
        "type": "chat",
        "text": f"[{current_time}] [{room_name}] {sender}: {text}",
    }
    database.add_message(sender_id, text, None, room_name)
    broadcast_room(room_name, new_msg, conn)
    send_json(conn,new_msg)
def handle_dm(conn, target_name, text, nicknames, user_ids, lock, get_nickname):
    target_conn = None
    with lock:
        users = list(nicknames.items())
    for c, name in users:
        if name == target_name:
            target_conn = c
            break
    if target_conn:
        sender = get_nickname(conn)
        with lock:
            sender_id = user_ids.get(conn)
            receiver_id = user_ids.get(target_conn)
            database.add_message(sender_id, text, receiver_id, room=None)
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
