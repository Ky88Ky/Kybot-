import json
import os
import time
from datetime import datetime

DATA_PATH = "functions/data/user_stats.json"


def load_stats():
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def save_stats(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)


def update_message_count(user_id: str):
    data = load_stats()
    if user_id not in data:
        data[user_id] = {"messages": 0, "time": 0, "last_seen": time.time()}
    data[user_id]["messages"] += 1
    save_stats(data)


def update_time_spent(current_users: list):
    data = load_stats()
    now = time.time()

    for user in current_users:
        user_id = user.id
        if user_id not in data:
            data[user_id] = {"messages": 0, "time": 0, "last_seen": now}
        last_seen = data[user_id].get("last_seen", now)
        session_time = now - last_seen

        if session_time >= 60:  # Only count if stayed for 1 minute+
            data[user_id]["time"] += session_time
            data[user_id]["last_seen"] = now

    save_stats(data)


def format_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    mins = minutes % 60
    if hours < 24:
        return f"{hours}h{mins}m" if mins else f"{hours}h"
    days = hours // 24
    hrs = hours % 24
    return f"{days}d{hrs}h" if hrs else f"{days}d"


def format_count(number: int) -> str:
    if number >= 1_000_000_000:
        return f"{number // 1_000_000_000}b"
    elif number >= 1_000_000:
        return f"{number // 1_000_000}m"
    elif number >= 1_000:
        return f"{number // 1_000}k"
    return str(number)


def get_user_rank(user_id: str):
    data = load_stats()
    if user_id not in data:
        return 9999  # First time join

    # Get ranking lists
    by_msg = sorted(data.items(), key=lambda x: x[1]["messages"], reverse=True)
    by_time = sorted(data.items(), key=lambda x: x[1]["time"], reverse=True)

    # Find message rank
    msg_rank = next((i + 1 for i, (uid, _) in enumerate(by_msg) if uid == user_id), None)
    time_rank = next((i + 1 for i, (uid, _) in enumerate(by_time) if uid == user_id), None)

    return {
        "rank": min(msg_rank, time_rank),
        "message_rank": msg_rank,
        "time_rank": time_rank,
        "messages": data[user_id]["messages"],
        "time": data[user_id]["time"]
    }