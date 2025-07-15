import json
import os

CHAT_DIR = "chats"
os.makedirs(CHAT_DIR, exist_ok=True)

def get_chat_path(chat_id):
    return os.path.join(CHAT_DIR, f"{chat_id}.json")

def save_chat(chat_id, chat_data):
    with open(get_chat_path(chat_id), "w", encoding="utf-8") as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=2)

def load_chat(chat_id):
    with open(get_chat_path(chat_id), "r", encoding="utf-8") as f:
        return json.load(f)

def list_all_saved_chats():
    chats = []
    for filename in os.listdir(CHAT_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(CHAT_DIR, filename), "r", encoding="utf-8") as f:
                chats.append(json.load(f))
    return sorted(chats, key=lambda c: c.get("created_at", ""), reverse=True)

