import asyncio
import time
import traceback
import json
import os
import re
import logging

from highrise import BaseBot, Position, AnchorPosition
from highrise.models import SessionMetadata, User

from functions.loop_emote import (
    check_and_start_emote_loop,
    handle_user_movement,
    handle_bot_emote_loop,
    emote_list,
    load_bot_loop,
)
from functions.data_store import is_owner, list_owners, add_owner
from functions.floors import handle_floor_commands
from functions.outfit import handle_outfit_command
from functions.color import handle_color_command
from functions.command import (
    get_user_commands,
    get_owner_commands,
    get_outfit_categories_text,
    get_command_category_menu,
    get_category_command_list,
    handle_owner_commands,
)
from functions.bot_movement import handle_bot_position_commands
from functions.welcome import get_welcome_message, should_welcome_user
from functions.leaderboard import (
    load_data,
    save_data,
    update_user_stats,
    format_compact_number,
    format_compact_time,
    CHAMPION_TITLES,
    handle_leaderboard_command,
    get_user_rank,
)

logging.basicConfig(level=logging.INFO)

JOINED_USERS_FILE = "data/joined_users.json"

def load_joined_users():
    try:
        if os.path.exists(JOINED_USERS_FILE):
            with open(JOINED_USERS_FILE, "r") as f:
                return json.load(f)
    except Exception:
        traceback.print_exc()
    return {}

def save_joined_users(data):
    try:
        with open(JOINED_USERS_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        traceback.print_exc()

def is_ws_connected(bot) -> bool:
    return hasattr(bot, "highrise") and bot.highrise.ws and not bot.highrise.ws.closed

async def increment_user_times(bot):
    while True:
        try:
            data = load_data()
            for user_id, username in list(bot.current_users.items()):
                update_user_stats(user_id, username, data=data, inc_time=60)
            save_data(data)
        except Exception:
            traceback.print_exc()
        await asyncio.sleep(60)

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.user_loops = {}
        self.loop_emote_list = emote_list
        self.ignored_bots = ["MonsterBud", "MonsterBeat"]
        self.bot_owners = list_owners()
        if not self.bot_owners:
            self.bot_owners = ["RayBM"]
            for o in self.bot_owners:
                add_owner(o)

        from functions.data_store import load_bot_location
        self.bot_location = load_bot_location() or {}
        self.follow_task = None
        self.follow_target_user_id = None
        self.original_position = None

        self._user_last_join_time = {}
        self.user_leave_time = {}
        self.user_join_time = {}
        self.current_users = {}  # user.id -> username
        self.user_last_seen = {}  # user.id -> last seen timestamp

    async def send_safe_whisper(self, user_id: str, text: str):
        try:
            if not is_ws_connected(self):
                return
            MAX_LEN = 240
            lines = text.split('\n')
            chunks, curr = [], ""
            for line in lines:
                if len(curr) + len(line) + 1 > MAX_LEN:
                    chunks.append(curr.rstrip())
                    curr = line + "\n"
                else:
                    curr += line + "\n"
            if curr:
                chunks.append(curr.rstrip())
            for chunk in chunks:
                try:
                    if not is_ws_connected(self):
                        return
                    await self.highrise.send_whisper(user_id, chunk)
                    await asyncio.sleep(0.35)
                except Exception:
                    traceback.print_exc()
        except Exception:
            traceback.print_exc()

    async def send_long_chat(self, message: str):
        try:
            if not message or not is_ws_connected(self):
                return
            lines = message.split("\n")
            chunks = []
            current = ""
            for line in lines:
                if len(current) + len(line) + 1 > 400:
                    chunks.append(current.rstrip())
                    current = line + "\n"
                else:
                    current += line + "\n"
            if current:
                chunks.append(current.rstrip())

            for chunk in chunks:
                try:
                    if not is_ws_connected(self):
                        return
                    await self.highrise.chat(chunk)
                    await asyncio.sleep(1.5)
                except Exception as e:
                    logging.warning(f"Failed to send chat message: {e}")
        except Exception:
            traceback.print_exc()

    async def on_start(self, session_metadata: SessionMetadata):
        try:
            await asyncio.sleep(2)
            self.bot_user_id = session_metadata.user_id
            load_bot_loop()
            asyncio.create_task(increment_user_times(self))
        except Exception:
            traceback.print_exc()
        logging.info("Bot ready ✅")

    async def on_stop(self):
        logging.info("Bot stopped.")

    async def on_user_join(self, user: User, pos=None):
        try:
            from functions.loop_emote import user_last_positions
            if pos:
                user_last_positions[user.id] = (pos.x, pos.y, pos.z)

            if user.username in self.ignored_bots:
                return

            now = time.time()
            self.user_join_time[user.id] = now
            self.current_users[user.id] = user.username
            self.user_last_seen[user.id] = now

            username_lower = user.username.lower()
            joined_users = load_joined_users()
            first_time = username_lower not in joined_users

            if should_welcome_user(user.id, self.user_last_seen, self.user_leave_time):
                if first_time:
                    joined_users[username_lower] = int(now)
                    save_joined_users(joined_users)

                leaderboard_data = load_data()
                rank_info = get_user_rank(user.id)
                rank = rank_info["room_rank"] if rank_info else 9999

                msg, emote_id = get_welcome_message(user.username, rank, first_time)

                if msg:
                    asyncio.create_task(self.send_long_chat(msg))
                if emote_id:
                    try:
                        await self.highrise.send_emote(emote_id)
                    except Exception:
                        traceback.print_exc()

                help_txt = (
                    "👋 Welcome!\n"
                    "🏆 Type `leaderboard` to view categories\n"
                    "🔹 `rank` to view your ranks\n"
                    "🎭 `emote` to view emote list"
                )
                asyncio.create_task(self.send_safe_whisper(user.id, help_txt))
        except Exception:
            traceback.print_exc()

    async def on_user_leave(self, user: User):
        try:
            self.current_users.pop(user.id, None)
            self.user_leave_time[user.id] = time.time()
            self.user_join_time.pop(user.id, None)
        except Exception:
            traceback.print_exc()

    async def on_user_move(self, user: User, pos: Position | AnchorPosition):
        try:
            if user.username not in self.ignored_bots:
                await handle_user_movement(self, user, pos)
                self.user_last_seen[user.id] = time.time()
        except Exception:
            traceback.print_exc()

    async def on_chat(self, user: User, message: str):
        try:
            if user.username in self.ignored_bots:
                return

            self.user_last_seen[user.id] = time.time()
            update_user_stats(user.id, user.username, inc_msg=True)

            logging.info(f"{user.username} said: {message}")

            if await handle_bot_position_commands(self, user, message):
                return

            await check_and_start_emote_loop(self, user, message)

            low_msg = message.lower().strip()
            if low_msg.startswith(("rank", "leaderboard", "lb", "show")):
                async def whisper_fn(target_user, msg):
                    await self.send_safe_whisper(target_user.id, msg)

                async def chat_fn(msg):
                    await self.send_long_chat(msg)

                def is_owner_fn(username):
                    return is_owner(username)

                await handle_leaderboard_command(
                    message, user,
                    whisper_fn=whisper_fn,
                    chat_fn=chat_fn,
                    is_owner_fn=is_owner_fn,
                )
                return

            if is_owner(user.username):
                if low_msg == "!command":
                    await self.send_safe_whisper(user.id, get_command_category_menu())
                    return
                m = re.match(r"!(\w+)", low_msg)
                if m:
                    res = get_category_command_list(m.group(1))
                    if res:
                        await self.send_safe_whisper(user.id, res)
                        return

            if low_msg.replace(" ", "") in ["emotelist", "emoteslist", "!emotes", "emote", "emotes"]:
                names = [aliases[1].capitalize() for aliases, _, _, allowed in self.loop_emote_list if allowed and len(aliases) > 1]
                for i in range(0, len(names), 20):
                    await self.send_safe_whisper(user.id, ", ".join(names[i:i + 20]))
                return

            if await handle_floor_commands(self, user, message):
                return

            if await handle_owner_commands(self, user, message):
                return

            if is_owner(user.username):
                if await handle_outfit_command(self, user, message):
                    return
                if await handle_color_command(self, user, message):
                    return

            if low_msg == "!help":
                cmds = get_user_commands()
                for i in range(0, len(cmds), 5):
                    await self.send_safe_whisper(user.id, "\n".join(cmds[i:i + 5]))
                return

        except Exception:
            traceback.print_exc()

    async def on_whisper(self, user: User, message: str):
        try:
            if user.username in self.ignored_bots:
                return
            logging.info(f"{user.username} whispered: {message}")

            self.user_last_seen[user.id] = time.time()

            if user.username.lower() == "raybm" or is_owner(user.username):
                await self.send_long_chat(message)
                await handle_bot_emote_loop(self, user, message)
                await check_and_start_emote_loop(self, user, message)
        except Exception:
            traceback.print_exc()