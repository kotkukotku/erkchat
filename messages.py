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