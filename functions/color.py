from highrise.models import Item

# Define bot owners (lowercase usernames)
BOT_OWNERS = {"raybm"}

# Valid color-changeable categories mapped from user-friendly names
CATEGORY_MAP = {
    "blush": "blush",
    "body": "body",
    "hair front": "hair_front",
    "hair back": "hair_back",
    "eye": "eye",
    "face hair": "face_hair",
    "mouth": "mouth",
}


async def color(bot, user, message: str):
    if user.username.lower() not in BOT_OWNERS:
        await bot.highrise.send_whisper(user.id, "❌ You do not have permission to use this command.")
        return

    parts = message.strip().split()
    if len(parts) < 3:
        await bot.highrise.send_whisper(user.id, "❌ Usage: !color <category> <palette_number>")
        return

    if parts[0] != "!color":
        return

    # Try to reconstruct multi-word category from first two or three parts
    possible_categories = [
        " ".join(parts[1:3]).lower(),     # e.g., "hair front"
        parts[1].lower(),                 # e.g., "eye"
    ]

    matched_category = None
    for cat in possible_categories:
        if cat in CATEGORY_MAP:
            matched_category = cat
            break

    if not matched_category:
        await bot.highrise.send_whisper(user.id, f"❌ Unknown category. Valid: {', '.join(CATEGORY_MAP.keys())}")
        return

    try:
        palette_number = int(parts[-1])
    except ValueError:
        await bot.highrise.send_whisper(user.id, "❌ Palette number must be a valid integer.")
        return

    internal_category = CATEGORY_MAP[matched_category]
    outfit_resp = await bot.highrise.get_my_outfit()
    outfit = outfit_resp.outfit

    updated = False
    for item in outfit:
        item_cat = item.id.split("-")[0]
        if item_cat == internal_category:
            item.active_palette = palette_number
            updated = True

    if not updated:
        await bot.highrise.send_whisper(user.id, f"❌ The bot isn't wearing any item from category '{matched_category}'.")
        return

    await bot.highrise.set_outfit(outfit)
    await bot.highrise.send_whisper(user.id, f"✅ Changed color of '{matched_category}' to palette #{palette_number}.")


async def handle_color_command(bot, user, message: str) -> bool:
    if message.lower().startswith("!color"):
        await color(bot, user, message)
        return True
    return False