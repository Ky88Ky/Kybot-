import os
import json

# === JSON Paths ===
BASE_PATH = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(BASE_PATH, exist_ok=True)

PATHS = {
    "owners": os.path.join(BASE_PATH, "bot_owners.json"),
    "bot_location": os.path.join(BASE_PATH, "bot_location.json"),
    "saved_fits": os.path.join(BASE_PATH, "saved_fits.json"),
    "free_items": os.path.join(BASE_PATH, "free_items.json"),
    "floors": os.path.join(BASE_PATH, "floors.json"),
    "ranks": os.path.join(BASE_PATH, "ranks.json"),
}

# === Helpers ===
def ensure_json(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)

def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

# === Init all files once ===
ensure_json(PATHS["owners"], [])
ensure_json(PATHS["bot_location"], {})
ensure_json(PATHS["saved_fits"], {})
ensure_json(PATHS["free_items"], {})
ensure_json(PATHS["floors"], {})
ensure_json(PATHS["ranks"], {})

# === Owner Handling ===
def list_owners() -> list[str]:
    return sorted(load_json(PATHS["owners"], []))

def is_owner(username: str) -> bool:
    return username.lower() in [u.lower() for u in list_owners()]

def add_owner(username: str) -> bool:
    owners = set(list_owners())
    if username.lower() not in owners:
        owners.add(username.lower())
        save_json(PATHS["owners"], sorted(owners))
        return True
    return False

def remove_owner(username: str) -> bool:
    owners = set(list_owners())
    if username.lower() in owners:
        owners.remove(username.lower())
        save_json(PATHS["owners"], sorted(owners))
        return True
    return False

# === Bot Location ===
def load_bot_location() -> dict:
    return load_json(PATHS["bot_location"], {})

def save_bot_location(data: dict):
    save_json(PATHS["bot_location"], data)

# === Floors ===
def load_floors() -> dict:
    return load_json(PATHS["floors"], {})

def save_floors(data: dict):
    save_json(PATHS["floors"], data)

# === Outfit ===
def get_saved_fits_path() -> str:
    return PATHS["saved_fits"]

def get_free_items_path() -> str:
    return PATHS["free_items"]

def get_path(name: str) -> str:
    return PATHS.get(name)

# === Ranks ===
def load_ranks_data() -> dict:
    return load_json(PATHS["ranks"], {})

def save_ranks_data(data: dict):
    save_json(PATHS["ranks"], data)