import json
import os
import threading
import traceback

lock = threading.Lock()
DATA_PATH = "data/ranks.json"

# Titles for ranks 1-10
rank_titles = [
    "👑 Legend", "👑 Ruler", "👑 Master", "👑 Conqueror", "👑 Veteran",
    "👑 Icon", "👑 Prodigy", "👑 Star", "👑 Hero", "👑 Pioneer"
]
CHAMPION_TITLES = {i + 1: title for i, title in enumerate(rank_titles)}

def load_data():
    try:
        with lock:
            if not os.path.exists(DATA_PATH):
                return {}
            with open(DATA_PATH, "r") as f:
                return json.load(f)
    except Exception:
        traceback.print_exc()
        return {}

def save_data(data):
    try:
        with lock:
            os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
            with open(DATA_PATH, "w") as f:
                json.dump(data, f, indent=2)
    except Exception:
        traceback.print_exc()

def update_user_stats(user_id, username, data=None, inc_msg=False, inc_time=0):
    try:
        user_id = str(user_id)
        if data is None:
            data = load_data()

        if user_id not in data:
            data[user_id] = {"username": username, "messages": 0, "time": 0}
        else:
            data[user_id]["username"] = username

        if inc_msg:
            data[user_id]["messages"] += 1
        if inc_time > 0:
            data[user_id]["time"] += inc_time

        save_data(data)
    except Exception:
        traceback.print_exc()

def format_compact_number(num: int) -> str:
    try:
        abs_num = abs(num)
        for unit in ['', 'k', 'm', 'b', 't']:
            if abs_num < 1000:
                return f"{int(num)}{unit}"
            abs_num /= 1000
            num /= 1000
        return f"{int(num)}t"
    except Exception:
        return str(num)

def format_compact_time(seconds: int) -> str:
    try:
        minutes, _ = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        parts = []
        if days > 0: parts.append(f"{days}d")
        if hours > 0: parts.append(f"{hours}h")
        if minutes > 0 or not parts: parts.append(f"{minutes}m")
        return ''.join(parts)
    except Exception:
        return "0m"

def get_user_rank(user_id: str):
    try:
        data = load_data()
        user_id = str(user_id)
        if user_id not in data:
            return None

        sorted_msg = sorted(data.items(), key=lambda x: x[1].get('messages', 0), reverse=True)
        sorted_time = sorted(data.items(), key=lambda x: x[1].get('time', 0), reverse=True)

        msg_rank = next((i + 1 for i, (uid, _) in enumerate(sorted_msg) if uid == user_id), None)
        time_rank = next((i + 1 for i, (uid, _) in enumerate(sorted_time) if uid == user_id), None)

        msg_ranks = {uid: i + 1 for i, (uid, _) in enumerate(sorted_msg)}
        time_ranks = {uid: i + 1 for i, (uid, _) in enumerate(sorted_time)}

        combined_scores = {uid: msg_ranks.get(uid, 9999) + time_ranks.get(uid, 9999) for uid in data.keys()}
        combined_sorted = sorted(combined_scores.items(), key=lambda x: x[1])
        room_rank = next((i + 1 for i, (uid, _) in enumerate(combined_sorted) if uid == user_id), None)

        title = CHAMPION_TITLES.get(room_rank, f"#{room_rank}" if room_rank else None)

        return {
            "msg_rank": msg_rank,
            "time_rank": time_rank,
            "room_rank": room_rank,
            "title": title
        }
    except Exception:
        traceback.print_exc()
        return None

async def handle_leaderboard_command(message: str, user, whisper_fn, chat_fn, is_owner_fn):
    try:
        cmd = message.lower().strip()
        parts = cmd.split()
        if not parts:
            return None, None

        command = parts[0]
        arg = parts[1] if len(parts) > 1 else ""

        data = load_data()
        sorted_msg = sorted(data.items(), key=lambda x: x[1].get("messages", 0), reverse=True)
        sorted_time = sorted(data.items(), key=lambda x: x[1].get("time", 0), reverse=True)

        def get_champion_sorted():
            try:
                msg_ranks = {uid: i + 1 for i, (uid, _) in enumerate(sorted_msg)}
                time_ranks = {uid: i + 1 for i, (uid, _) in enumerate(sorted_time)}
                scores = {uid: msg_ranks.get(uid, 9999) + time_ranks.get(uid, 9999) for uid in data}
                sorted_combined = sorted(scores.items(), key=lambda x: x[1])
                return [(uid, data[uid]) for uid, _ in sorted_combined[:10]]
            except Exception:
                traceback.print_exc()
                return []

        if command == "rank":
            mentioned_user = None
            if '@' in message:
                mentioned_username = message.split('@')[-1].strip()
                for uid, u in data.items():
                    if u["username"].lower() == mentioned_username.lower():
                        mentioned_user = {"id": uid, "username": u["username"]}
                        break

            target = mentioned_user if mentioned_user else {"id": user.id, "username": user.username}
            rank_data = get_user_rank(target["id"])
            if not rank_data:
                await whisper_fn(user, f"{target['username']} has no rank yet.")
                return None, None

            msgs = data.get(str(target["id"]), {}).get("messages", 0)
            time_spent = data.get(str(target["id"]), {}).get("time", 0)

            msg_str = format_compact_number(msgs)
            time_str = format_compact_time(time_spent)

            reply = (
                f"📊 Rank for @{target['username']}:\n"
                f"📝 Messages: {msg_str} (#{rank_data['msg_rank']})\n"
                f"🕒 Time: {time_str} (#{rank_data['time_rank']})\n"
                f"👑 Champion: {rank_data['title']}"
            )
            await whisper_fn(user, reply)
            return None, None

        elif command in ["leaderboard", "lb", "show"] and arg in ["1", "2", "3"]:
            cat = int(arg)
            if command == "show" and not is_owner_fn(user.username):
                await whisper_fn(user, "Only owners can use 'show'.")
                return None, None

            if cat == 1:
                label = "🗣️ Most Talkative"
                sorted_list = sorted_msg[:10]
                formatter = lambda u: format_compact_number(u[1].get("messages", 0))
                prefix = ""
            elif cat == 2:
                label = "⏱️ Longest Stay"
                sorted_list = [(uid, udata) for uid, udata in sorted_time if udata.get("time", 0) > 0][:10]
                formatter = lambda u: format_compact_time(u[1].get("time", 0))
                prefix = ""
            else:
                label = "👑 Room Champions"
                sorted_list = get_champion_sorted()
                short_titles = {
                    1: "Lgd", 2: "Rlr", 3: "Mstr", 4: "Cqr", 5: "Vtr",
                    6: "Icn", 7: "Pdg", 8: "Str", 9: "Hro", 10: "Pnr"
                }
                prefix = "👑"

            lines = [f"🏆 {label}:"]
            for i, (uid, udata) in enumerate(sorted_list, 1):
                name = udata.get("username", f"User{i}")
                if cat == 3:
                    title = short_titles.get(i, f"#{i}")
                    lines.append(f"{i}. {prefix}{title} @{name}")
                else:
                    val = formatter((uid, udata))
                    lines.append(f"{i}. @{name} - {val}")

            message = "\n".join(lines)

            # If too long, split into multiple whispers
            if len(message) > 280:
                chunks = [message[i:i + 280] for i in range(0, len(message), 280)]
                for chunk in chunks:
                    await whisper_fn(user, chunk)
            else:
                if command == "show":
                    await chat_fn(message)
                else:
                    await whisper_fn(user, message)
            return None, None

        return None, None
    except Exception:
        traceback.print_exc()
        return None, None