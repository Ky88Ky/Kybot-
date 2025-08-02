import re
from functions.outfit import category_aliases
from functions.data_store import is_owner, add_owner, remove_owner, list_owners

# === User Command List ===
def get_user_commands() -> list[str]:
    return [
        "🧍 User Commands:",
        "• !rank — See your top leaderboard ranks",
        "• leaderboard — Show leaderboard categories",
        "• leaderboard <number|name> — View a leaderboard",
        "• emote — Show emote list",
        "• f1 / f2 / f3 — Teleport to floors",
        "• vip1 / vip2 — Teleport to VIP floors (if invited)",
        "• !help — Show this command list"
    ]

# === Owner Command Entry Point ===
def get_owner_commands() -> list[str]:
    return [
        "📚 Bot Owner Commands:",
        "Type !command to show owner command categories"
    ]

# === Owner Command Category Menu ===
def get_command_category_menu() -> str:
    return (
        "📂 Owner Command Categories:\n"
        "• !floors\n"
        "• !botlocation\n"
        "• !owner\n"
        "• !outfit\n"
        "• !leaderboard"
    )

# === Detailed Commands Per Category ===
def get_category_command_list(category: str) -> str | None:
    if category == "leaderboard":
        return (
            "📊 Leaderboard Commands:\n"
            "• leaderboard — View leaderboard menu\n"
            "• leaderboard <number|name> — View top 10\n"
            "• !rank — Your leaderboard summary\n"
            "• !resetlb — Reset all leaderboards\n"
            "• !resetlb <number|name> — Reset one leaderboard\n"
            "• !removelb @user — Remove user from leaderboard\n"
            "• !unremovelb @user — Restore user to leaderboard\n"
            "• !removedlist — View removed users"
        )
    elif category == "outfit":
        return (
            "👕 Outfit Commands:\n"
            "• !<category> <number> — Equip item (e.g. !shirt 2, !hair front 3)\n"
            "• !remove <category> — Remove items from category (e.g. !remove hair front)\n"
            "• !fit save <1–50> — Save your current outfit\n"
            "• !fit <1–50> — Load a saved outfit\n"
            "• !fit remove <1–50> — Delete a saved outfit\n"
            "• !fit list — View your saved outfits\n"
            "• !fit random — Load a random outfit\n"
            "• !fit command — Show outfit help\n"
            "• !outfit list — View available categories"
        )
    elif category == "floors":
        return (
            "🏠 Floor Commands:\n"
            "• f1 / f2 / f3 — Teleport to saved floors\n"
            "• vip1 / vip2 / vip3 — Teleport to VIP floors (if invited)\n"
            "• !setf1 / !setf2 / !setf3 — Save floor position\n"
            "• !setvipf1 / !setvipf2 / !setvipf3 — Save VIP floor position\n"
            "• !resetf1 / !resetvipf1 — Reset public or VIP floor\n"
            "• !invitevip 1 @user — Invite user to VIP floor 1\n"
            "• !uninvitevip 1 @user — Remove user from VIP floor 1"
        )
    elif category == "botlocation":
        return (
            "🤖 Bot Position Commands:\n"
            "• !sbot — Save bot’s current position\n"
            "• !base — Move bot to saved position\n"
            "• !follow @user — Bot follows user\n"
            "• !stop — Stop following"
        )
    elif category == "owner":
        return (
            "👑 Owner Access Commands:\n"
            "• !addo @user — Add owner\n"
            "• !removeo @user — Remove owner\n"
            "• !olist — View current owners"
        )
    return None

# === Outfit Category Viewer ===
def get_outfit_categories_text() -> str:
    return (
        "👗 Outfit Categories:\n"
        "• 🧑‍🦱 hair front, 🔙 hair back, 🧔 face_hair, 🪞 eyebrow\n"
        "• 👁️ eye, 👃 nose, 👄 mouth\n"
        "• 👕 shirt, 👖 pants, 👗 skirt\n"
        "• 👟 shoes, 🧦 sock, 🧤 gloves\n"
        "• 🕶️ glasses, 🎒 bag, 💎 earrings, 📿 necklace\n"
        "• ⌚ watch, 👜 handbag\n"
        "• 🧸 freckle, 🌸 blush"
    )

# === Owner Commands Handler ===
async def handle_owner_commands(bot, user, message: str) -> bool:
    if not is_owner(user.username):
        return False

    msg = message.strip()
    lower = msg.lower()

    if lower.startswith("!addo"):
        mentions = re.findall(r"@(\w+)", msg)
        if not mentions:
            await bot.highrise.send_whisper(user.id, "❌ Usage: `!addo @username`")
            return True

        added = []
        for u in mentions:
            if add_owner(u):
                added.append(u)

        if added:
            await bot.highrise.send_whisper(user.id, f"✅ Added to owner list: {', '.join(added)}")
        else:
            await bot.highrise.send_whisper(user.id, "⚠️ No new owners were added.")
        return True

    elif lower.startswith("!removeo"):
        mentions = re.findall(r"@(\w+)", msg)
        if not mentions:
            await bot.highrise.send_whisper(user.id, "❌ Usage: `!removeo @username`")
            return True

        removed = []
        for u in mentions:
            if remove_owner(u):
                removed.append(u)

        if removed:
            await bot.highrise.send_whisper(user.id, f"🗑️ Removed: {', '.join(removed)}")
        else:
            await bot.highrise.send_whisper(user.id, "⚠️ No owners were removed.")
        return True

    elif lower in ("!olist", "!listo"):
        owners = list_owners()
        if owners:
            await bot.highrise.send_whisper(user.id, "👑 Bot Owners:\n" + ", ".join(f"@{o}" for o in owners))
        else:
            await bot.highrise.send_whisper(user.id, "⚠️ No owners found.")
        return True

    elif lower == "!outfit list":
        await bot.highrise.send_whisper(user.id, get_outfit_categories_text())
        return True

    return False