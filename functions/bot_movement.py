import asyncio
import traceback
from highrise import Position
from functions.data_store import save_bot_location, is_owner

async def handle_bot_position_commands(bot, user, message: str) -> bool:
    msg = message.strip().lower()

    # === !sbot – Save current bot location ===
    if msg == "!sbot" and is_owner(user.username):
        try:
            room_users = await bot.highrise.get_room_users()
            for room_user, pos in room_users.content:
                if room_user.username.lower() == user.username.lower():
                    if hasattr(pos, "x") and hasattr(pos, "y") and hasattr(pos, "z"):
                        bot.bot_location.update(
                            x=pos.x,
                            y=pos.y,
                            z=pos.z,
                            facing=getattr(pos, "facing", 0)
                        )
                        save_bot_location(bot.bot_location)
                        await bot.highrise.send_whisper(user.id, f"📍 Bot position saved: {bot.bot_location}")
                    else:
                        await bot.highrise.send_whisper(user.id, "❌ Invalid position data.")
                    break
        except Exception:
            print("❌ Error saving bot position:")
            traceback.print_exc()
        return True

    # === !base – Return to saved location ===
    if msg == "!base" and is_owner(user.username) and bot.bot_location:
        try:
            await bot.highrise.walk_to(Position(**bot.bot_location))
        except Exception:
            print("❌ Error during !base:")
            traceback.print_exc()
        return True

    # === !follow or !follow @user ===
    if msg.startswith("!follow") and is_owner(user.username):
        if bot.follow_task and not bot.follow_task.done():
            bot.follow_task.cancel()
            bot.follow_task = None
            bot.follow_target_user_id = None

        parts = message.split()
        target_username = parts[1].lstrip("@") if len(parts) > 1 else user.username

        try:
            room_users = await bot.highrise.get_room_users()
            for room_user, pos in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    bot.follow_target_user_id = room_user.id
                    break
            else:
                await bot.highrise.send_whisper(user.id, f"❌ User @{target_username} not found.")
                return True

            bot.original_position = Position(**bot.bot_location) if all(k in bot.bot_location for k in ("x", "y", "z")) else None

            async def follow_loop():
                try:
                    while True:
                        room_users = await bot.highrise.get_room_users()
                        target_pos = None
                        for ru, pos in room_users.content:
                            if ru.id == bot.follow_target_user_id:
                                if hasattr(pos, "x") and hasattr(pos, "y") and hasattr(pos, "z"):
                                    target_pos = pos
                                break

                        if not target_pos:
                            try:
                                await bot.highrise.send_whisper(user.id, f"❌ @{target_username} left the room. Stopping follow.")
                            except Exception:
                                pass
                            break

                        bot_pos = bot.bot_location
                        dist = ((bot_pos.get("x", 0) - target_pos.x) ** 2 +
                                (bot_pos.get("y", 0) - target_pos.y) ** 2 +
                                (bot_pos.get("z", 0) - target_pos.z) ** 2) ** 0.5

                        if dist > 4:
                            new_pos = Position(target_pos.x - 1, target_pos.y, target_pos.z)
                            await bot.highrise.walk_to(new_pos)
                            bot.bot_location.update(x=new_pos.x, y=new_pos.y, z=new_pos.z, facing=0)
                            save_bot_location(bot.bot_location)

                        await asyncio.sleep(0.8)

                except asyncio.CancelledError:
                    if bot.original_position:
                        await bot.highrise.walk_to(bot.original_position)
                        bot.bot_location.update(
                            x=bot.original_position.x,
                            y=bot.original_position.y,
                            z=bot.original_position.z,
                            facing=0,
                        )
                        save_bot_location(bot.bot_location)
                        try:
                            await bot.highrise.send_whisper(user.id, "🛑 Follow stopped. Returned to base.")
                        except Exception:
                            pass
                    raise

            bot.follow_task = asyncio.create_task(follow_loop())
            await bot.highrise.send_whisper(user.id, f"🚶 Following @{target_username}")
        except Exception:
            traceback.print_exc()
        return True

    # === !stop – Cancel follow ===
    if msg == "!stop" and is_owner(user.username):
        if bot.follow_task and not bot.follow_task.done():
            bot.follow_task.cancel()
            bot.follow_task = None
            bot.follow_target_user_id = None
            await bot.highrise.send_whisper(user.id, "🛑 Follow stopped.")
        else:
            await bot.highrise.send_whisper(user.id, "🛑 No follow task is running.")
        return True

    return False