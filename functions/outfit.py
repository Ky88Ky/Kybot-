import json
import os
import random
from typing import Tuple
from highrise.models import Item
from functions.data_store import get_free_items_path, get_saved_fits_path, is_owner

FREE_ITEMS_PATH = get_free_items_path()
SAVED_FITS_PATH = get_saved_fits_path()

# === Load free items ===
try:
    with open(FREE_ITEMS_PATH, "r", encoding="utf-8") as f:
        free_items = json.load(f)
except Exception:
    free_items = {}

# === Load saved fits ===
if os.path.exists(SAVED_FITS_PATH):
    try:
        with open(SAVED_FITS_PATH, "r", encoding="utf-8") as f:
            saved_fits = json.load(f)
    except Exception:
        saved_fits = {}
else:
    saved_fits = {}

# === Category Aliases ===
category_aliases = {
    "hair front": "hair_front",
    "hair back": "hair_back",
    "face_hair": "face_hair",
    "eyebrow": "eyebrow",
    "eye": "eye",
    "nose": "nose",
    "mouth": "mouth",
    "shirt": "shirt",
    "pants": "pants",
    "skirt": "skirt",
    "shoes": "shoes",
    "sock": "sock",
    "gloves": "gloves",
    "glasses": "glasses",
    "bag": "bag",
    "earrings": "earrings",
    "necklace": "necklace",
    "watch": "watch",
    "handbag": "handbag",
    "freckle": "freckle",
    "blush": "blush"
}

category_emojis = {
    "hair front": "💇‍♀️",
    "hair back": "🎀",
    "face_hair": "🧔",
    "eyebrow": "🪒",
    "eye": "👁️",
    "nose": "👃",
    "mouth": "👄",
    "shirt": "👕",
    "pants": "👖",
    "skirt": "👗",
    "shoes": "👟",
    "sock": "🧦",
    "gloves": "🧤",
    "glasses": "🕶️",
    "bag": "👜",
    "earrings": "📿",
    "necklace": "💎",
    "watch": "⌚",
    "handbag": "👜",
    "freckle": "🌟",
    "blush": "🌸"
}

# === Stackable Categories ===
stackable_categories = {
    "face_hair", "freckle", "blush", "accessories", "earrings", "necklace", "watch", "gloves", "glasses"
}

# === Helpers ===

def get_canonical_category(alias: str) -> str | None:
    return category_aliases.get(alias.lower())

def get_category_prefix(category: str) -> str:
    return category.split("_")[0]

def _save_fits():
    os.makedirs(os.path.dirname(SAVED_FITS_PATH), exist_ok=True)
    with open(SAVED_FITS_PATH, "w", encoding="utf-8") as f:
        json.dump(saved_fits, f, indent=2, ensure_ascii=False)

# === Outfit Equipping ===

async def equip_item(bot, category_alias: str, index: int) -> Tuple[bool, str]:
    category = get_canonical_category(category_alias)
    if not category or category not in free_items:
        return False, f"❌ Invalid category '{category_alias}'."

    items = list(free_items[category].keys())
    if not (1 <= index <= len(items)):
        return False, f"❌ Invalid index for '{category_alias}'. Range: 1–{len(items)}"

    item_id = items[index - 1]
    current_outfit = (await bot.highrise.get_my_outfit()).outfit

    new_outfit = []
    for item in current_outfit:
        item_prefix = item.id.split("-")[0]
        if category in stackable_categories or item_prefix != category:
            new_outfit.append(item)

    new_outfit.append(Item(type="clothing", id=item_id, amount=1, account_bound=False, active_palette=0))
    await bot.highrise.set_outfit(new_outfit)
    return True, f"✅ Equipped {category} item #{index}."

async def remove_category(bot, category_alias: str) -> Tuple[bool, str]:
    category = get_canonical_category(category_alias)
    if not category:
        return False, f"❌ Unknown category '{category_alias}'"

    prefix = get_category_prefix(category)
    current_outfit = (await bot.highrise.get_my_outfit()).outfit
    new_outfit = [item for item in current_outfit if not item.id.startswith(prefix)]

    await bot.highrise.set_outfit(new_outfit)
    return True, f"✅ Removed items from category '{category_alias}'."

# === Saved Fits ===

def list_saved_fits() -> str:
    if not saved_fits:
        return "📦 No saved fits found."
    lines = ["📁 Saved fits:"]
    for slot, data in sorted(saved_fits.items(), key=lambda x: int(x[0])):
        categories = ", ".join(data.keys())
        lines.append(f"• Slot {slot}: {categories}")
    return "\n".join(lines)

async def save_fit(bot, slot: int) -> Tuple[bool, str]:
    slot_str = str(slot)
    if slot_str in saved_fits:
        return False, f"❌ Slot {slot} already used. Use !fit remove {slot} first."

    outfit = (await bot.highrise.get_my_outfit()).outfit
    fit_data = {}
    for item in outfit:
        cat = item.id.split("-")[0]
        fit_data[cat] = {
            "id": item.id,
            "color": item.active_palette if item.active_palette is not None else 0
        }

    saved_fits[slot_str] = fit_data
    _save_fits()
    return True, f"✅ Fit saved in slot {slot}."

async def load_fit(bot, slot: int) -> Tuple[bool, str]:
    slot_str = str(slot)
    if slot_str not in saved_fits:
        return False, f"❌ No fit found in slot {slot}."

    outfit = []
    for cat, data in saved_fits[slot_str].items():
        item_id = data["id"]
        color = data.get("color", 0)
        outfit.append(Item(type="clothing", id=item_id, amount=1, account_bound=False, active_palette=color))

    await bot.highrise.set_outfit(outfit)
    return True, f"✅ Loaded fit from slot {slot}."

async def remove_fit(slot: int) -> Tuple[bool, str]:
    slot_str = str(slot)
    if slot_str not in saved_fits:
        return False, f"❌ No fit in slot {slot}."
    del saved_fits[slot_str]
    _save_fits()
    return True, f"✅ Removed fit from slot {slot}."

# === Random Outfit from Free Items ===

async def load_random_items_from_free(bot) -> Tuple[bool, str]:
    if not free_items:
        return False, "❌ No free items available."

    # Required facial features (Highrise won't load without them)
    required = ["eye", "eyebrow", "nose", "mouth"]
    outfit = []

    for cat in required:
        if cat in free_items and free_items[cat]:
            item_id = random.choice(list(free_items[cat].keys()))
            outfit.append(Item(type="clothing", id=item_id, amount=1, account_bound=False, active_palette=0))

    # Always add body-flesh
    outfit.append(Item(type="clothing", id="body-flesh", amount=1, account_bound=False, active_palette=0))

    # Optional random fashion items
    optional_cats = [
        "hair_front", "face_hair", "freckle", "shirt", "shoes"
    ]
    optional_cats.append(random.choice(["pants", "skirt"]))

    for cat in optional_cats:
        if cat in free_items and free_items[cat]:
            item_id = random.choice(list(free_items[cat].keys()))
            outfit.append(Item(type="clothing", id=item_id, amount=1, account_bound=False, active_palette=0))

            if cat == "hair_front":
                front_suffix = item_id.replace("hair_front", "")
                back_dict = free_items.get("hair_back", {})
                for back_id in back_dict:
                    if back_id.endswith(front_suffix):
                        outfit.append(Item(type="clothing", id=back_id, amount=1, account_bound=False, active_palette=0))
                        break

    await bot.highrise.set_outfit(outfit)
    return True, "🎲 Random outfit equipped from free items."

# === Help ===

def get_fit_help_text() -> list[str]:
    return [
        "🎽 Outfit Commands:",
        "• !<category> <number> – Equip item (e.g., !shirt 2)",
        "• !remove <category> – Remove category",
        "• !fit save <1–50> – Save current outfit",
        "• !fit <1–50> – Load outfit",
        "• !fit remove <1–50> – Delete saved outfit",
        "• !fit list – Show saved outfits",
        "• !fit random – Load random outfit",
        "• !fit command – Show this help",
        "• !outfit list – Show all outfit categories"
    ]

def get_outfit_categories_text() -> str:
    lines = ["👗 Available Outfit Categories:"]
    for alias in category_aliases.keys():
        emoji = category_emojis.get(alias, "")
        lines.append(f"{emoji} {alias}")
    return "\n".join(lines)

# === Handler ===

async def handle_outfit_command(bot, user, message: str) -> bool:
    if not is_owner(user.username):
        return False

    trigger = message.strip().lower()

    for cat_alias in category_aliases:
        if trigger.startswith(f"!{cat_alias} "):
            try:
                index = int(trigger[len(f"!{cat_alias} "):])
                success, msg = await equip_item(bot, cat_alias, index)
                await bot.highrise.send_whisper(user.id, msg)
            except ValueError:
                await bot.highrise.send_whisper(user.id, f"❌ Invalid number for !{cat_alias}")
            return True

    if trigger.startswith("!remove "):
        cat_alias = trigger[len("!remove "):].strip()
        success, msg = await remove_category(bot, cat_alias)
        await bot.highrise.send_whisper(user.id, msg)
        return True

    if trigger == "!fit command":
        for i in range(0, len(get_fit_help_text()), 5):
            await bot.highrise.send_whisper(user.id, "\n".join(get_fit_help_text()[i:i+5]))
        return True

    if trigger == "!fit list":
        await bot.highrise.send_whisper(user.id, list_saved_fits())
        return True

    if trigger == "!fit random":
        success, msg = await load_random_items_from_free(bot)
        await bot.highrise.send_whisper(user.id, msg)
        return True

    if trigger.startswith("!fit save "):
        try:
            slot = int(trigger.split()[2])
            if not (1 <= slot <= 50):
                raise ValueError()
            success, msg = await save_fit(bot, slot)
            await bot.highrise.send_whisper(user.id, msg)
        except Exception:
            await bot.highrise.send_whisper(user.id, "❌ Usage: !fit save <1–50>")
        return True

    if trigger.startswith("!fit remove "):
        try:
            slot = int(trigger.split()[2])
            if not (1 <= slot <= 50):
                raise ValueError()
            success, msg = await remove_fit(slot)
            await bot.highrise.send_whisper(user.id, msg)
        except Exception:
            await bot.highrise.send_whisper(user.id, "❌ Usage: !fit remove <1–50>")
        return True

    if trigger.startswith("!fit "):
        parts = trigger.split()
        if len(parts) == 2 and parts[1].isdigit():
            slot = int(parts[1])
        elif len(parts) == 3 and parts[1] == "load" and parts[2].isdigit():
            slot = int(parts[2])
        else:
            return False
        if not (1 <= slot <= 50):
            await bot.highrise.send_whisper(user.id, "❌ Slot must be between 1–50")
            return True
        success, msg = await load_fit(bot, slot)
        await bot.highrise.send_whisper(user.id, msg)
        return True

    if trigger == "!outfit list":
        await bot.highrise.send_whisper(user.id, get_outfit_categories_text())
        return True

    return False