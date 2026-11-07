
from datetime import datetime

import database
from protocol import send_json


def handle_message(
    conn,
    text,
    nicknames,
    user_ids,
    lock,
    broadcast_room,
    room_name
):
    with lock:
        sender = nicknames.get(conn, "Unknown")
        sender_id = user_ids.get(conn)

    current_time = datetime.now().strftime("%H:%M")

    new_msg = {
        "type": "chat",
        "username": sender,
        "text": text,
        "room": room_name,
        "timestamp": current_time
    }

    database.add_message(sender_id, text, None, room_name)

    broadcast_room(room_name, new_msg, conn)
    send_json(conn, new_msg)


def handle_dm(
    conn,
    target_name,
    text,
    nicknames,
    user_ids,
    lock,
    get_nickname
):
    target_conn = None

    with lock:
        users = list(nicknames.items())

    for client, name in users:
        if name == target_name:
            target_conn = client
            break

    if not target_conn:
        send_json(conn, {
            "type": "system",
            "text": "Kullanıcı bulunamadı."
        })
        return

    sender = get_nickname(conn)
    current_time = datetime.now().strftime("%H:%M")

    with lock:
        sender_id = user_ids.get(conn)
        receiver_id = user_ids.get(target_conn)

        database.add_message(
            sender_id,
            text,
            receiver_id,
            room=None
        )

    my_msg = {
        "type": "dm",
        "username": target_name,
        "text": text,
        "timestamp": current_time,
        "direction": "outgoing"
    }

    sender_msg = {
        "type": "dm",
        "username": sender,
        "text": text,
        "timestamp": current_time,
        "direction": "incoming"
    }

    send_json(conn, my_msg)
    send_json(target_conn, sender_msg)

