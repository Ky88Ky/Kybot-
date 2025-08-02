# functions/floors.py

import json
import re
from highrise import Position
from functions.data_store import get_path
from functions.data_store import is_owner

FLOOR_FILE = get_path("floors")

# Max floors
MAX_FLOORS = 5

# Data structures
floor_data = {
    "public": {},      # f1 to f5
    "vip": {},         # vip1 to vip5
    "invites": {}      # slot -> [username1, username2]
}

# Load existing
try:
    with open(FLOOR_FILE, "r", encoding="utf-8") as f:
        floor_data.update(json.load(f))
except Exception:
    pass

def save_floors():
    with open(FLOOR_FILE, "w", encoding="utf-8") as f:
        json.dump(floor_data, f, indent=2, ensure_ascii=False)

# === Save floor ===
def set_floor(slot: str, pos: Position):
    floor_data["public"][slot] = {
        "x": pos.x, "y": pos.y, "z": pos.z, "facing": pos.facing
    }
    save_floors()

def set_vip_floor(slot: str, pos: Position):
    floor_data["vip"][slot] = {
        "x": pos.x, "y": pos.y, "z": pos.z, "facing": pos.facing
    }
    save_floors()

# === Reset ===
def reset_floor(slot: str):
    if slot in floor_data["public"]:
        del floor_data["public"][slot]
        save_floors()

def reset_vip_floor(slot: str):
    if slot in floor_data["vip"]:
        del floor_data["vip"][slot]
    if slot in floor_data["invites"]:
        del floor_data["invites"][slot]
    save_floors()

# === Invite system ===
def invite_to_vip(slot: str, usernames: list[str]):
    slot_invites = floor_data["invites"].setdefault(slot, [])
    for user in usernames:
        u = user.lower()
        if u not in slot_invites:
            slot_invites.append(u)
    save_floors()

def is_user_invited(slot: str, username: str) -> bool:
    return username.lower() in [u.lower() for u in floor_data["invites"].get(slot, [])]

# === Command Handler ===
async def handle_floor_commands(bot, user, message: str) -> bool:
    trigger = message.strip().lower()

    # === Owner-only floor saving ===
    if is_owner(user.username):
        if trigger.startswith("!setf"):
            num = trigger.replace("!setf", "").strip()
            if num.isdigit() and 1 <= int(num) <= MAX_FLOORS:
                slot = f"f{num}"
                room_users = await bot.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.username == user.username:
                        set_floor(slot, pos)
                        await bot.highrise.send_whisper(user.id, f"✅ Saved floor `{slot}`.")
                        return True

        if trigger.startswith("!setvipf"):
            num = trigger.replace("!setvipf", "").strip()
            if num.isdigit() and 1 <= int(num) <= MAX_FLOORS:
                slot = f"vip{num}"
                room_users = await bot.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.username == user.username:
                        set_vip_floor(slot, pos)
                        await bot.highrise.send_whisper(user.id, f"✅ Saved VIP floor `{slot}`.")
                        return True

        if trigger.startswith("!resetf"):
            num = trigger.replace("!resetf", "").strip()
            slot = f"f{num}"
            reset_floor(slot)
            await bot.highrise.send_whisper(user.id, f"🧹 Reset floor `{slot}`.")
            return True

        if trigger.startswith("!resetvipf"):
            num = trigger.replace("!resetvipf", "").strip()
            slot = f"vip{num}"
            reset_vip_floor(slot)
            await bot.highrise.send_whisper(user.id, f"🧹 Reset VIP floor `{slot}`.")
            return True

        if trigger.startswith("!invitevip"):
            parts = trigger.split()
            if len(parts) >= 3:
                num = parts[1]
                mentions = re.findall(r"@(\w+)", message)
                if num.isdigit() and 1 <= int(num) <= MAX_FLOORS and mentions:
                    slot = f"vip{num}"
                    invite_to_vip(slot, mentions)
                    await bot.highrise.send_whisper(user.id, f"🎟️ Invited to `{slot}`: " + ", ".join(mentions))
                    return True

    # === Teleport commands (public floors) ===
    for i in range(1, MAX_FLOORS + 1):
        slot = f"f{i}"
        triggers = [
            f"f{i}", f"f {i}", f"floor{i}", f"floor {i}",
            f"F{i}", f"F {i}", f"FLOOR{i}", f"FLOOR {i}"
        ]
        if trigger in triggers and slot in floor_data["public"]:
            await bot.highrise.teleport(user.id, Position(**floor_data["public"][slot]))
            return True

    # === Teleport commands (vip floors) ===
    for i in range(1, MAX_FLOORS + 1):
        slot = f"vip{i}"
        triggers = [
            f"vip{i}", f"vip {i}", f"VIP{i}", f"VIP {i}", f"Vip{i}", f"Vip {i}"
        ]
        if trigger in triggers:
            if slot in floor_data["vip"]:
                if is_owner(user.username) or is_user_invited(slot, user.username):
                    await bot.highrise.teleport(user.id, Position(**floor_data["vip"][slot]))
                else:
                    await bot.highrise.send_whisper(user.id, "⛔ You are not invited to this VIP floor.")
                return True

    return False