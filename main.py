import asyncio
from highrise import BaseBot, Position
from highrise.models import SessionMetadata, User, AnchorPosition

from functions.loop_emote import check_and_start_emote_loop, handle_user_movement
from functions.json import bot_location

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.user_loops = {}

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        if bot_location:
            try:
                await self.highrise.walk_to(Position(**bot_location))
                print("Bot moved to saved position.")
            except Exception as e:
                print("Error moving to saved position:", e)
        print("Bot is ready.")

    async def on_chat(self, user: User, message: str):
        print(f"[CHAT] {user.username}: {message}")
        await check_and_start_emote_loop(self, user, message)

        # حفظ موقع البوت
        if message == "!sbot" and user.username == "RayBM":
            try:
                room_users = await self.highrise.get_room_users()
                for room_user, pos in room_users.content:
                    if room_user.username == user.username:
                        bot_location["x"] = pos.x
                        bot_location["y"] = pos.y
                        bot_location["z"] = pos.z
                        bot_location["facing"] = pos.facing
                        await self.highrise.send_whisper(user.id, f"تم حفظ موقع البوت بنجاح: {bot_location}")
                        break
            except Exception as e:
                print("خطأ في حفظ موقع البوت:", e)

        # العودة للموقع المحفوظ
        if message == "!base":
            try:
                if bot_location:
                    await self.highrise.walk_to(Position(**bot_location))
            except Exception as e:
                print("خطأ في تنفيذ !base:", e)

        # أوامر التنقل للطوابق
        msg = message.lower().replace(" ", "")
        if msg in ("-floor1", "!floor1", "floor1", "/floor1", "f1", "-1"):
            await self.highrise.teleport(user.id, Position(9.5, 0.0, 16.5))

        elif msg in ("-floor2", "!floor2", "floor2", "/floor2", "f2", "-2"):
            await self.highrise.teleport(user.id, Position(14.5, 9.0, 6.0))

        elif msg in ("-floor3", "!floor3", "floor3", "/floor3", "f3", "-3"):
            await self.highrise.teleport(user.id, Position(12.5, 19.25, 6.5))

    async def on_whisper(self, user: User, message: str):
        print(f"[WHISPER] {user.username}: {message}")
        await check_and_start_emote_loop(self, user, message)

    async def on_user_move(self, user: User, pos: Position | AnchorPosition) -> None:
        await handle_user_movement(self, user, pos)

    async def on_stop(self):
        print("Bot stopped.")
