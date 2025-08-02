import asyncio
import traceback
import json
import os
import random
from highrise import BaseBot
from highrise.models import User, Position, AnchorPosition
from highrise import ResponseError


BOT_LOOP_FILE = "bot_emote_loop.json"

emote_list: list[tuple[list[str], str, float, bool]] = [
    (['1', 'ghostfloat','Ghost'], 'emote-ghost-idle', 18.20, True),
    (["2", "laidback", "laid"], "sit-open", 24.025963, True),
    (['3', 'relaxed', 'relax'], 'idle_layingdown2', 20.55, True),
    (["4", "repose", "reposing"], "sit-relaxed", 28.889858, True),  
    (['5', 'relaxing', 'Relaxin'], 'idle-floorsleeping2', 16.25, True),
    (['6', 'cozynap', 'Nap'], 'idle-floorsleeping', 12.50, True), 
    (['7', 'attentive', 'Attentive'], 'idle_layingdown', 23.55, True),
    (['8', 'enthused', 'Enthused'], 'idle-enthusiastic', 14.60, True),
    (['9', 'hipshake', 'Hip Shake'], 'dance-hipshake', 11.60, True), 
    (['10', 'laploop', 'TapLoop'], 'idle-loop-tapdance', 5.50, True),
    (['11', 'chill', 'chillin'], 'idle-loop-happy', 18.00, True),
    (['12', 'annoyed', 'Annoying'], 'idle-loop-annoyed', 16.06, True),
    (['13', 'aerobic', 'Aerobics'], 'idle-loop-aerobics', 7.51, True),
    (['14', 'ponder','lookup'], 'idle-lookup', 21.00, True),
    (["15", "push it", "PushIt"], "dance-employee", 6.10, True),
    (['16', 'sleepy', 'Sleepy'], 'idle-sleep', 22.62, True),
    (['17', 'pouty', 'Pouty Face'], 'idle-sad', 23.38, True),
    (['18', 'posh', 'Poshing'], 'idle-posh', 21.00, True),
    (['19', 'feelbeat', 'FeelTheBeat'], 'idle-dance-headbobbing', 25.37, True),
    (['20', 'irritated', 'Irritated'], 'idle-angry', 24.43, True),
    (['21', 'Fly', 'I Believe I Can Fly'], 'emote-wings', 12.13, True),
    (['22', 'Think','thinking'], 'emote-think', 3.00, True),
    (['23', 'theatrical', 'Theatric'], 'emote-theatrical', 8.59, True),
    (['24', 'heropose', 'hero'], 'idle-hero', 21.88, True),
    (['25', 'Superrun', 'Super Run'], 'emote-superrun', 6.27, True),
    (['26', 'punch', 'superpunch'], 'emote-superpunch', 3.75, True),
    (['27', 'Sumo', 'Sumo Fight'], 'emote-sumo', 10.87, True),
    (['28', 'thumbsuck', 'Thumb suck'], 'emote-suckthumb', 4.19, True),
    (["29", "shrink", "Shrink"], "emote-shrink", 8.00, True),
    (['30', 'tired', 'tiring'], 'idle-loop-tired', 21.96, True),
    (['31', 'shy', 'shying'], 'idle-loop-shy', 16.47, True),
    (["32", "attention", "At Attention"], "emote-salute", 3.0, True),
    (["33", "cute salute", "CuteSalute"], "emote-cutesalute", 3.0, True),
    (["34", "wop dance", "WopDance"], "dance-tiktok11", 9.20, True),
    (['35', 'splits drop','splits'], 'emote-splitsdrop', 4.47, True),
    (['36', 'snowball', 'Snowball fight'], 'emote-snowball', 5.23, True),
    (['37', 'snow angel', 'angel', 'angel'], 'emote-snowangel', 6.22, True),
    (["38", "this is for you", "gift"], "emote-gift", 5.50, True),
    (['39', 'handshake', 'Secret handshake'], 'emote-secrethandshake', 3.88, True),
    (["40", "guitar", "Guitar"], "idle-guitar", 12.229398, True),
    (['41', 'rope pull', 'rope'], 'emote-ropepull', 8.77, True),
    (['42', 'roll', 'rolling'], 'emote-roll', 3.56, True),
    (['43', 'rofl', 'roflinf'], 'emote-rofl', 6.31, True),
    (['44', 'robot', 'robotic'], 'emote-robot', 7.61, True),
    (['45', 'rainbow', 'Rainbows'], 'emote-rainbow', 2.81, True),
    (['46', 'proposing', 'proposal'], 'emote-proposing', 4.00, True),
    (['47', 'peekaboo', 'Peekaboo'], 'emote-peekaboo', 3.63, True),
    (['48', 'peace', 'Peace on'], 'emote-peace', 5.76, True),
    (['49', 'panic', 'Panicing'], 'emote-panic', 2.85, True),
    (["50", "touch", "Touching"], "dance-touch", 11.7, True),
    (['51', 'ninja run', 'ninja'], 'emote-ninjarun', 4.75, True),
    (['52', 'night fever', 'fever'], 'emote-nightfever', 5.49, True),
    (['53', 'monster fail', 'fail'], 'emote-monster_fail', 4.63, True),
    (['54', 'model', 'Modeling'], 'emote-model', 6.00, True),
    (["55", "head blowup", "HeadBlowup"], "emote-headblowup", 11.667537, True),
    (['56', 'levelup', 'Level up'], 'emote-levelup', 6.05, True),
    (['57', 'amused', 'Amused'], 'emote-laughing2', 5.06, True),
    (["58", "teleport", "teleporting"], "emote-teleporting", 11.00, True),
    (["59", "ditzy pose", "DitzyPose"], "emote-pose9", 4.583117, True),
    (['60', 'super kick','kick'], 'emote-kicking', 4.87, True),
    (["61", "tiktok7", "Tiktok7"], "idle-dance-tiktok7", 12.00, True),
    (['62', 'judo chop', 'Judo'], 'emote-judochop', 2.43, True),
    (['63', 'jetpack','jet'], 'emote-jetpack', 16.20, True),
    (['64', 'hugging', 'Hug yourself'], 'emote-hugyourself', 4.99, True),
    (['65', 'sweating', 'Sweat'], 'emote-hot', 4.35, True),
    (["66", "slap", "Slaping"], "emote-slap", 2.00, True),
    (["67", "pose 10", "Pose10"], "emote-pose10", 3.989871, True),
    (["68", "creepy cute", "Creepycute"], "emote-creepycute", 7.902453, True),
    (['69', 'harlem shake', 'Harlemshake'], 'emote-harlemshake', 13.00, True),
    (["70", "boxer", "Boxing"], "emote-boxer", 5.555702, True),
    (['71', 'handstand', 'Handstand'], 'emote-handstand', 4.02, True),
    (['72', 'greedy', 'Greedy'], 'emote-greedy', 4.64, True),
    (["73", "frustrated", "Frustrate"], "emote-frustrated", 5.584622, True),
    (['74', 'moonwalk', 'Moonwalk'], 'emote-gordonshuffle', 7.60, True),
    (['75', 'zombie', 'Zombie'], 'idle_zombie', 28.75, True),
    (['76', 'gangnam ','gangnam style'], 'emote-gangnam', 7.00, True),
    (["77", "celebration", "Celebert"], "emote-celebrationstep", 3.353703, True),
    (['78', 'faint', 'Faint'], 'emote-fainting', 18.42, True),
    (['79', 'clumsy', 'Clumsy'], 'emote-fail2', 6.48, True),
    (['80', 'fall', 'Falling'], 'emote-fail1', 5.62, True),
    (['81', 'face palm', 'palm'], 'emote-exasperatedb', 2.72, True),
    (['82', 'exasperated', 'Exasperat'], 'emote-exasperated', 2.37, True),
    (['83', 'elbow bump', 'bump'], 'emote-elbowbump', 3.80, True),
    (['84', 'disco', 'Disco'], 'emote-disco', 5.37, True),
    (["85", "blast off", 'Blast'], "emote-disappear", 6.2, True),
    (["86", "faint drop", "FaintDrop"], "emote-deathdrop", 3.76, True),
    (["87", "collapse", "Collapsing"], "emote-death2", 4.86, True),
    (["88", "revival", "Revival"], "emote-death", 6.62, True),
    (["89", "dab", "Dabing"], "emote-dab", 2.72, True),
    (["90", "curtsy", "Curtsying"], "emote-curtsy", 2.43, True),
    (["91", "confusion", "Confusions"], "emote-confused", 8.58, True),
    (["92", "cold", "Colds"], "emote-cold", 3.66, True),
    (["93", "charging", "Charge"], "emote-charging", 8.03, True),
    (["94", "bunny hop", "BunnyHop"], "emote-bunnyhop", 12.38, True),
    (["95", "bow", "Bowing"], "emote-bow", 3.34, True),
    (["96", "boo", "Booing"], "emote-boo", 4.5, True),
    (["97", "home run!", "HomeRun!"], "emote-baseball", 7.25, True),
    (["98", "falling apart", "FallingApart"], "emote-apart", 4.81, True),
    (["99", "surprise", "Surprise big"], "emote-pose6", 5.375124, True),
    (["100", "point", "Point"], "emoji-there", 2.06, True),
    (["101", "sneeze", "Sneezing"], "emoji-sneeze", 3.0, True),
    (["102", "smirk", "Smirk"], "emoji-smirking", 4.82, True),
    (["103", "sick", "Sick"], "emoji-sick", 5.07, True),
    (["104", "gasp", "Gaspinh"], "emoji-scared", 3.01, True),
    (["105", "punch", "Punching"], "emoji-punch", 1.76, True),
    (["106", "pray", "Praying"], "emoji-pray", 4.5, True),
    (["107", "stinky", "Stinken"], "emoji-poop", 4.8, True),
    (["108", "naughty", "Naught"], "emoji-naughty", 4.28, True),
    (["109", "mind blown", "MindBlown"], "emoji-mind-blown", 2.4, True),
    (["110", "lying", "Lie"], "emoji-lying", 6.31, True),
    (["111", "levitate", "Levitating"], "emoji-halo", 5.84, True),
    (["112", "fireball lunge", "FireballLunge"], "emoji-hadoken", 2.72, True),
    (["113", "give up", "GiveUp"], "emoji-give-up", 5.41, True),
    (["114", "tummy ache", "TummyAche"], "emoji-gagging", 5.5, True),
    (["115", "blush", "blushful"], "emote-shy2", 4.50, True),
    (["116", "stunned", "Stunned"], "emoji-dizzy", 4.05, True),
    (["117", "kawaii", "Kawai"], "dance-kawai", 9.50, True),
    (["118", "cry", "crying"], "emoji-crying", 3.4, True),
    (["119", "ice skating", "IceSkating"], "emote-iceskating", 7.299156, True),
    (["120", "scritchy", "Scritchy"], "idle-wild", 26.422824, True),
    (["121", "arrogance", "arrogan"], "emoji-arrogance", 6.87, True),
    (["122", "anime dance", "AnimeDance"], "dance-anime", 8.46671, True),
    (["123", "vogue hands", "VogueHands"], "dance-voguehands", 9.15, True),
    (["124", "savage dance", "tiktok8"], "dance-tiktok8", 10.00, True),
    (["125", "tiktok2", "Don't Start Now"], "dance-tiktok2", 10.00, True),
    (["126", "tiktok4", "TikTok 4"], "idle-dance-tiktok4", 15.00, True),
    (["127", "smoothwalk", "Smooth walk"], "dance-smoothwalk", 5.00, True),
    (["128", "ring on it", "Ring on It"], "dance-singleladies", 20.31, True),
    (["129", "shopping", "Let's Go Shopping"], "dance-shoppingcart", 4.00, True),
    (["130", "russian", "Russian dance"], "dance-russian", 9.00, True),
    (["131", "uwu", "UwU"], "idle-uwu", 24.00, True),
    (["132", "pennys dance", "Penny"], "dance-pennywise", 1.21, True),
    (["133", "orange juice dance", "Orange Juice"], "dance-orangejustice", 5.80, True),
    (["134", "rock out", "RockOut"], "dance-metal", 15.08, True),
    (["135", "wrong dance", "WrongDance"], "dance-wrong", 12.422389, True),
    (["136", "ice cream", "IceCream"], "dance-icecream", 14.769573, True),
    (["137", "hands in the air", "in the Air"], "dance-handsup", 22.28, True),
    (["138", "gravity", "Grav"], "emote-gravity", 8.955966, True),
    (["139", "duck walk", "DuckWalk"], "dance-duckwalk", 11.00, True),
    (["140", "fashionista", "Fashion"], "emote-fashionista", 5.00, True),
    (["141", "k-pop dance", "K-Pop"], "dance-blackpink", 6.60, True),
    (["142", "push ups", "PushUps"], "dance-aerobics", 8.60, True),
    (["143", "hyped", "Hype"], "emote-hyped", 7.49, True),
    (["144", "jinglebell", "Jingle bell"], "dance-jinglebell",10.20, True),
    (["145", "nervous", "Nervousess"], "idle-nervous", 21.71, True),
    (["146", "toilet", "wc"], "idle-toilet", 32.17, True),
    (["147", "attention", "Attentions"], "emote-attention", 4.4, True),
    (["148", "astronaut", "Astro"], "emote-astronaut", 13.79, True),
    (["149", "dance zombie", "Zombie dance"], "dance-zombie", 12.92, True),
    (["150", "ghosted", "boho"], "emoji-ghost", 3.20, True),
    (["151", "heart eyes", "HeartEyes"], "emote-hearteyes", 4.03, True),
    (["152", "sword fight", "Swordfight"], "emote-swordfight", 5.91, True),
    (["153", "time jump", "TimeJump"], "emote-timejump", 4.01, True),
    (["154", "snake", "Snakey"], "emote-snake", 5.26, True),
    (["155", "heart fingers", "HeartFingers"], "emote-heartfingers", 4.0, True),
    (["156", "heart shape", "HeartShape"], "emote-heartshape", 6.23, True),
    (["157", "hug", "Hug"], "emote-hug", 3.5, True),
    (["158", "zombie run", "run Zombie"], "emote-zombierun", 9.182984, True),
    (["159", "eyeroll", "Eye roll"], "emoji-eyeroll", 3.02, True),
    (["160", "embarrassed", "Embarrassing"], "emote-embarrassed", 7.414283, True),
    (["161", "float", "Floater"], "emote-float", 8.995302, True),
    (["162", "telekinesis", "Telekinesis"], "emote-telekinesis", 10.492032, True),
    (["163", "sexy dance", "SexyDance"], "dance-sexy", 11.80, True),
    (["164", "puppet", "Puppet"], "emote-puppet", 16.325823, True),
    (["165", "fighter", "Fight"], "idle-fighter", 17.19123, True),
    (["166", "penguin", "Penguins"], "dance-pinguin", 11.58291, True),
    (["167", "creepy puppet", "CreepyPuppet"], "dance-creepypuppet", 6.416121, True),
    (["168", "sleigh", "Sleigh"], "emote-sleigh", 11.333165, True),
    (["169", "maniac", "Maniac"], "emote-maniac", 4.906886, True),
    (["170", "energy ball", "EnergyBall"], "emote-energyball", 7.575354, True),
    (["171", "singing", "Sing"], "idle_singing", 9.50, True),
    (["172", "frog", "Frogs"], "emote-frog", 14.55257, True), 
    (["173", "punk guitar", "Guitar punk"], "emote-punkguitar", 9.365807, True),
    (["174", "cute", "Cute"], "emote-cute", 6.170464, True),
    (["175", "tiktok9", "TikTok Dance 9"], "dance-tiktok9", 11.00, True),
    (["176", "weird dance", "Weird Dance"], "dance-weird", 21.556237, True),
    (["177", "tiktok10", "TikTok Dance 10"], "dance-tiktok10", 8.00, True), 
    (["178", "pose 8", "Pose 8"], "emote-pose8", 4.00, True),
    (["179", "casual dance", "CasualDance"], "idle-dance-casual", 9.079756, True), 
    (['180', 'bummed', 'Bummed'], 'idle-loop-sad', 5.80, True),
    (["181", "smooch", "sweet Smooch"], "emote-kissing", 5.0, True),
    (['182', 'trampoline', 'tramp'], 'emote-trampoline', 4.60, True),
    (['183', 'fruity', 'fruitydance', 'Fruity Dance'], 'dance-fruity', 16.40, True),
    (['184', 'fairytwirl', 'Fairy Twirl', 'twirl'], 'emote-looping', 8.00, True),
    (['185', 'fairyfloat', 'Fairy Float', 'float'], 'idle-floating', 25.50, True),
    (['186', 'cheer', 'cheerleader'], 'dance-cheerleader', 15.60, True),
    (['187', 'karma', 'karmadance', 'Karma Dance'], 'dance-wild', 14.00, True),
    (['188', 'stargazing', 'star', 'stargazer'], 'emote-stargazer', 6.00, True),
    (['199', 'electrified', 'Electrified'], 'emote-electrified', 4.50, False),
    (["200", "stargazing", "Star Gazing"], "emote-stargaze", 1.127464, False),
    (["201", "kawaii gogo", "KawaiiGoGo"], "emote-kawaiigogo", 10.0, False),
    (['202', 'Ignition', 'ignition boost'], 'hcc-jetpack', 26.00, False),
    (['203', 'handwalk', 'hand'], 'handwalk', 7.77, False),
    (["204", "robo","robotic"], "dance-robotic", 15.50, False),
    (["205", "superpose", "Super pose"], "emote-superpose", 4.530791, False),
    (['206', 'REST', 'Rest'], 'sit-idle-cute', 16.50, False),
    (['207', 'fairyfloat', 'fairy'], 'floating', 26.60, False),
    (['208', 'hero entrance', 'Hero entrance'], 'emote-hero', 5.00, False),
    (['209', 'flirtt', 'flirt'], 'emote-lust', 4.66, False),
    (['210', 'graceful', 'Graceful'], 'emote-graceful', 3.75, False),
    (['211', 'headball', 'ball'], 'emote-headball', 10.07, False),
    (['212', 'frolic', 'Frolic'], 'emote-frollicking', 3.70, False),
    (["213", "cursing", "Cursing Emote"], "emoji-cursing", 2.38, False),
    (["214", "yoga flow", "Yoga Flow"], "dance-spiritual", 15.7, False),
    (["215", "flex", "Flexing"], "emoji-flex", 2.1, False),
    (["216", "robotic", "Robotic"], "dance-robotic", 17.81, False),
    (["217", "karate", "Karates"], "dance-martial-artist", 13.00, False),
    (["218", "floss", "Flosss"], "dance-floss", 21.00, False),
    (["219", "break dance", "Breakdance"], "dance-breakdance", 17.00, False),
]
user_last_positions = {}

def is_ws_connected(bot) -> bool:
    return hasattr(bot, "highrise") and bot.highrise.ws and not bot.highrise.ws.closed

async def check_and_start_emote_loop(self: BaseBot, user: User, message: str):
    try:
        cleaned_msg = message.strip().lower()

        if cleaned_msg in ("stop", "/stop", "!stop", "-stop"):
            if user.id in self.user_loops:
                self.user_loops[user.id]["task"].cancel()
                del self.user_loops[user.id]
                await self.highrise.send_whisper(user.id, "Emote loop stopped. (Type any emote name or number to start again)")
            else:
                await self.highrise.send_whisper(user.id, "You don't have an active emote loop.")
            return

        selected = next((e for e in emote_list if cleaned_msg in [a.lower() for a in e[0]]), None)
        if selected:
            aliases, emote_id, duration, user_allowed = selected
            if not user_allowed:
                return

            if user.id in self.user_loops:
                self.user_loops[user.id]["task"].cancel()

            async def emote_loop():
                try:
                    while True:
                        if not self.user_loops[user.id]["paused"] and is_ws_connected(self):
                            room_users = await self.highrise.get_room_users()
                            user_ids = [u.id for u, _ in room_users.content]
                            if user.id not in user_ids:
                                self.user_loops[user.id]["task"].cancel()
                                del self.user_loops[user.id]
                                return
                            try:
                                await self.highrise.send_emote(emote_id, user.id)
                            except ResponseError as re:
                                if "Target user not in room" in str(re):
                                    self.user_loops[user.id]["task"].cancel()
                                    del self.user_loops[user.id]
                                    return
                                else:
                                    raise
                        await asyncio.sleep(duration)
                except asyncio.CancelledError:
                    pass
                except Exception:
                    traceback.print_exc()

            task = asyncio.create_task(emote_loop())
            self.user_loops[user.id] = {
                "paused": False,
                "emote_id": emote_id,
                "duration": duration,
                "task": task,
            }

            visible_name = aliases[1] if len(aliases) > 1 else aliases[0]
            await self.highrise.send_whisper(
                user.id, f"You are now in a loop for emote: {visible_name}. (To stop, type 'stop')"
            )
    except Exception:
        traceback.print_exc()

async def handle_user_movement(self: BaseBot, user: User, pos) -> None:
    try:
        if user.id not in self.user_loops:
            return

        if isinstance(pos, Position):
            old_pos = user_last_positions.get(user.id)
            user_last_positions[user.id] = (pos.x, pos.y, pos.z)

            if old_pos is None:
                return

            if old_pos != (pos.x, pos.y, pos.z):
                self.user_loops[user.id]["paused"] = True
                await asyncio.sleep(2)
                new_pos = user_last_positions.get(user.id)
                if new_pos == (pos.x, pos.y, pos.z):
                    self.user_loops[user.id]["paused"] = False
        elif isinstance(pos, AnchorPosition):
            user_last_positions[user.id] = None
    except Exception:
        traceback.print_exc()

loop_file_path = "functions/bot_emote_loop.json"
bot_loop_data = { "emotes": [], "mode": "order" }
bot_loop_task = None

def save_bot_loop():
    with open(loop_file_path, "w") as f:
        json.dump(bot_loop_data, f)

def load_bot_loop():
    global bot_loop_data
    if os.path.exists(loop_file_path):
        try:
            with open(loop_file_path, "r") as f:
                bot_loop_data = json.load(f)
        except Exception:
            pass

async def handle_bot_emote_loop(self: BaseBot, user: User, message: str):
    global bot_loop_task
    msg = message.strip()
    lower = msg.lower()

    if lower in ("rest loop", "reset loop", "stop loop", "stop bot loop"):
        await stop_bot_emote_loop(self, user)
        return

    if lower == "loop list":
        if not bot_loop_data["emotes"]:
            await self.highrise.send_whisper(user.id, "Bot has no emotes saved.")
            return
        txt = "🤖 Bot Emote Loop:\n"
        for idx, emote in enumerate(bot_loop_data["emotes"], 1):
            txt += f"{idx}. {emote['emote_id']} - {emote['duration']:.1f}s\n"
        await self.highrise.send_whisper(user.id, txt)
        return

    if lower.startswith("loopr "):
        target = lower.replace("loopr", "").strip()
        bot_loop_data["emotes"] = [e for e in bot_loop_data["emotes"] if e["emote_id"] != target]
        save_bot_loop()
        await self.highrise.send_whisper(user.id, f"✅ Removed emote: {target}")
        return

    if lower.startswith("loop mode "):
        mode = lower.replace("loop mode", "").strip()
        if mode in ("random", "order"):
            bot_loop_data["mode"] = mode
            save_bot_loop()
            await self.highrise.send_whisper(user.id, f"✅ Bot loop mode set to {mode}.")
        else:
            await self.highrise.send_whisper(user.id, "❌ Mode must be 'order' or 'random'.")
        return

    if lower.startswith("loop "):
        emote_name = lower.replace("loop", "").strip()
        selected = next((e for e in emote_list if emote_name in [a.lower() for a in e[0]]), None)
        if selected:
            _, emote_id, duration, _ = selected
            bot_loop_data["emotes"].append({"emote_id": emote_id, "duration": duration})
            save_bot_loop()
            await self.highrise.send_whisper(user.id, f"✅ Bot will now loop: {emote_id}")
            if not bot_loop_task or bot_loop_task.done():
                bot_loop_task = asyncio.create_task(start_bot_loop(self))
        else:
            await self.highrise.send_whisper(user.id, f"❌ Emote not recognized: {emote_name}")

async def start_bot_loop(self: BaseBot):
    global bot_loop_task
    try:
        while True:
            if not is_ws_connected(self):
                await asyncio.sleep(1)
                continue

            if not bot_loop_data["emotes"]:
                await asyncio.sleep(5)
                continue

            emotes = bot_loop_data["emotes"]
            loop = random.sample(emotes, len(emotes)) if bot_loop_data["mode"] == "random" else emotes

            for emote in loop:
                if not is_ws_connected(self):
                    break
                try:
                    await self.highrise.send_emote(emote["emote_id"])
                except ResponseError:
                    pass
                await asyncio.sleep(emote["duration"])
    except asyncio.CancelledError:
        pass
    except Exception:
        traceback.print_exc()

async def stop_bot_emote_loop(self: BaseBot, user: User):
    global bot_loop_task
    if bot_loop_task and not bot_loop_task.done():
        bot_loop_task.cancel()
        bot_loop_task = None
        bot_loop_data["emotes"].clear()
        save_bot_loop()
        await self.highrise.send_whisper(user.id, "🛑 Bot emote loop stopped.")
    else:
        await self.highrise.send_whisper(user.id, "❌ No active bot loop to stop.")