import random
import os
import importlib.util
from highrise import*
from highrise import BaseBot,Position
from highrise.models import SessionMetadata
from highrise import Highrise, GetMessagesRequest
from functions.loop_emote import check_and_start_emote_loop
from functions.vip_manager import is_vip, handle_vip_command, get_vip_list
from functions.commands import is_teleport_command, handle_teleport_command
from functions.vip_data import load_vip_list, save_vip_list

vip_list = load_vip_list()

class Bot(BaseBot):
    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("working")
        await self.highrise.walk_to(Position(17.5 , 0.0 , 12.5, "FrontRight"))
             
    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        # Only the bot prints the message in the console
        print(f"{user.username} (ID: {user.id})")

        # Announce the user has joined the room publicly
        await self.highrise.chat(f"{user.username} joined!")

        # Send welcome whispers to the user
        await self.highrise.send_whisper(user.id, f"❤️Welcome [{user.username}]! Use: [!emote list] or [1-97] for dances & emotes.")
        await self.highrise.send_whisper(user.id, f"❤️Use: [/help] for more information.")
        await self.highrise.send_whisper(user.id, f"❤Type F3 F2 and F1 to teleport between the floor 🤍.")

        # Send emotes
        await self.highrise.send_emote("dance-hipshake")
        await self.highrise.send_emote("emote-lust", user.id)

       # React with a heart emoji
        await self.highrise.react("heart", user.id)
        
    async def on_chat(self, user: User, message: str) -> None:
        print(f"{user.username}: {message}")    
        username = user.username.lower()
        is_owner = username == "raybm"

        # Handle VIP command
        if message.lower().startswith("vip@") or message.lower().startswith("unvip@"):
            if is_owner:
                response = await handle_vip_command(user, message, vip_list)
            else:
                response = f"Sorry {user.username}, only the bot owner can manage VIPs."
            await self.highrise.chat(response)
            return

        # Handle VIP-only commands
        if (
            is_teleport_command(message)
            or message.lower().startswith("tele ")
            or message.lower().startswith("tele@")
            or message.lower().startswith("summon ")
            or message.lower().startswith("summon@")
            or message.strip() == "-4"
        ):
            if is_owner or is_vip(username, vip_list):
                await handle_teleport_command(user, message, self.highrise.send_whisper)
            else:
                await self.highrise.chat(f"Sorry {user.username}, this command is for VIPs only.")
            return

        # Handle VIP list command
        normalized_msg = message.lower().lstrip("!/ -").strip()
        if normalized_msg == "viplist":
            vip_message = get_vip_list(vip_list)
            await self.highrise.send_whisper(user.id, vip_message)
            return
            
        await check_and_start_emote_loop(self, user, message)
        # Check for direct emote names

        if message.startswith("/carp"):
           await self.highrise.react("clap",user.id)
           await self.highrise.send_whisper(user.id,"🟡You Caught 1x Golden Carp🟡 YOU WON THE MEDAL: (MEGA FISHERMAN) ")
          
        if message.startswith("/shrimp "):
           await self.highrise.react("clap",user.id)
           await self.highrise.send_whisper(user.id,"💎You Caught 1x Diamond Shrimp💎YOU WON THE MEDAL: (DIAMANTE MASTER FISHERMAN  )")                                
        if message.startswith("/curative"):
           await self.highrise.react("heart",user.id)

        if message.startswith("/shield"):
           await self.highrise.react("heart",user.id)
           await self.highrise.send_whisper(user.id,f"@{user.username} 🛡 You Used The Shield 🛡")

        if message.startswith("whiskey") or      message.startswith("whisky") or      message.startswith("Whiskey") or             message.startswith("drink") or             message.startswith("Drink") or message.startswith("!whiskey"):
           await self.highrise.react("heart",user.id)
           await self.highrise.send_whisper(user.id,f"@{user.username}  Whiskey: because adulting is hard and sometimes you need a little liquid encouragement! 🥃")

        if message.startswith("beer") or  message.startswith("Beer") or  message.startswith("alcohol") or message.startswith("Alcohol") or  message.startswith("!beer") or message.startswith("!Drunk"):
           await self.highrise.react("heart",user.id)
           await self.highrise.send_whisper(user.id,f"@{user.username}  on the house drive safe 🍺")

        if message.startswith("wine") or  message.startswith("redwine") or  message.startswith("red wine") or message.startswith("plonk") or  message.startswith("Plonk") or message.startswith("vino"):
           await self.highrise.react("heart",user.id)
           await self.highrise.send_whisper(user.id,f"@{user.username}  Ah, red wine—fancy!🍷 Trying to look sophisticated, or just hoping for purple teeth?🍷")
        
        if message.startswith("champagne") or  message.startswith("vodka") or  message.startswith("Vodka") or message.startswith("Champagne") or  message.startswith("celebration") or message.startswith("celebrate"):
           await self.highrise.react("heart",user.id)
           await self.highrise.send_whisper(user.id,f"@{user.username}  Ah, “Let’s raise a glass to celebrate the good times and the friends who make them unforgettable.”🍸🎉")
      
       
        if message.startswith("cocktail") or  message.startswith("mixed") or  message.startswith("mojito") or message.startswith("Potion") or  message.startswith("tonic") or message.startswith("julep"):
           await self.highrise.react("heart",user.id)
           await self.highrise.send_whisper(user.id,f"@{user.username}  “Cheers to the moments that turn into memories, one drink at a time.🥂")
                                          
         
        if message.startswith("Water") or message.startswith("water") or message.startswith("thirsty") or message.startswith("Thirsty") or  message.startswith("dry") or message.startswith("Dry"):
           await self.highrise.react("heart",user.id)
           await self.highrise.send_whisper(user.id,f"@{user.username}  You could say, “Ah, water—because staying hydrated is the real adventure!”🚰💧")
                      
            
        if        message.startswith("/tele") or              message.startswith("/tp") or              message.startswith("/fly") or     message.startswith("!tele") or      message.startswith("!tp") or     message.startswith("!fly"):
          if user.username == "iced_yu" or user.username == "FallonXOXO" or user.username == "RayMG":            await self.teleporter(message)

        if        message.startswith("-floor1") or message.startswith("!floor1") or message.startswith("-floor 1") or message.startswith("Floor 1") or message.startswith("Floor1") or message.startswith("/floor1") or    message.startswith("floor1") or message.startswith("-1") or    message.startswith("floor1") or message.startswith("f1") or message.startswith("f 1") or message.startswith("floor1") or message.startswith("F1")  or   message.startswith("floor 1") or message.startswith("!floor 1"):
          await self.highrise.teleport(user.id, Position(9.5 , 0.0 , 16.5))
                 
        if        message.startswith("-floor3") or message.startswith("!floor3") or message.startswith("-floor 3") or message.startswith("Floor 3") or message.startswith("Floor3") or message.startswith("/floor3") or    message.startswith("floor3") or message.startswith("-3") or    message.startswith("floor3") or message.startswith("f3") or message.startswith("f 3") or message.startswith("floor3") or message.startswith("F3")  or   message.startswith("floor 3") or message.startswith("!floor 3"):
          await self.highrise.teleport(user.id, Position(12.5 , 19.25 , 6.5))

        if        message.startswith("-floor4") or message.startswith("!floor4") or message.startswith("-floor 4") or message.startswith("Floor 4") or message.startswith("Floor4") or message.startswith("/floor4") or    message.startswith("floor4") or message.startswith("-4") or    message.startswith("floor4") or message.startswith("f4") or message.startswith("f 4") or message.startswith("floor4") or message.startswith("F4")  or   message.startswith("floor 4") or message.startswith("!floor 4"):
          await self.highrise.teleport(user.id, Position(14.5 , 20.0 , 1.5))
            
        if        message.startswith("-floor2") or message.startswith("!floor2") or message.startswith("-floor 2") or message.startswith("Floor 2") or message.startswith("Floor2") or message.startswith("/floor2") or    message.startswith("floor2") or message.startswith("-2") or    message.startswith("floor2") or message.startswith("f2") or message.startswith("f 2") or message.startswith("floor2") or message.startswith("F2")  or   message.startswith("floor 2") or message.startswith("!floor 2"):
          await self.highrise.teleport(user.id, Position(14.5 , 9.0 , 6.0))
          
        if        message.startswith("!lista") or    message.startswith("!emote list") or                                 message.startswith("!emote list") or message.startswith("!list"):
            await self.highrise.send_whisper(user.id,"!angry ,!thumbsup , !cursing , !flex , !gagging , !celebrate , !blackpink , !tiktok2 , !tiktok9 , !pennywise , !russian , !shop , !enthused , !singing ,!wrong , !guitar , !pinguin , !astronaut , !saunter , !flirt , !creepy , !watch , !revelation")
          
        if        message.startswith("!lista") or    message.startswith("!emote list") or                                 message.startswith("!emote list") or message.startswith("!list"):
            await self.highrise.send_whisper(user.id,"!tiktok10 ,!tiktok8 , !cutey , !pose3 , !pose5 , !pose1 , !pose8 , !pose7  !pose9 , !cute , !superpose , !frog , !snake , !energyball , !maniac , !teleport , !float , !telekinesi , !fight , !wei , !fashion , !boxer , !bashful , !arabesque , !party")
          
        if        message.startswith("!lista") or    message.startswith("!emote list") or                                 message.startswith("!emote list") or message.startswith("!list"):
            await self.highrise.send_whisper(user.id,"!confused , !charging , !snowangel , !hot , !snowball , !curtsy , !bow ,!model , !greedy , !tired , !shy , !wave , !hello , !lau ,!yes , !sad , !no , !kiss , !casual , !ren , !sit , !punk , !zombie , !gravity , !icecream ,!uwu , !sayso , !star")

        if        message.startswith("!lista") or    message.startswith("!emote list") or                                 message.startswith("!emote list") or message.startswith("!list"):
          await self.highrise.send_whisper(user.id,"!skating , !bitnervous , !scritchy , !timejump , !gottago , !jingle , !hyped , !sleigh , !surprise , !repose , !kawaii , !touch , !gift , !pushit , !tiktok , !salute , !attention , !smooch , !launch")
          
        if        message.startswith("/lista") or    message.startswith("/emote list") or                                 message.startswith("/emote list") or message.startswith("/list"):
            await self.highrise.send_whisper(user.id,"/angry ,/thumbsup , /cursing , /flex , /gagging , /celebrate , /blackpink , /tiktok2 , /tiktok9 , /pennywise , /russian , /shop , /enthused , /singing , /wrong , /guitar , /pinguin , /astronaut , /saunter , /flirt , /creepy , /watch , /revelation")
          
        if        message.startswith("/lista") or    message.startswith("/emote list") or                                 message.startswith("/emote list") or message.startswith("/list"):
            await self.highrise.send_whisper(user.id,"/tiktok10 , /tiktok8 , /cutey , /pose3 , /pose5 , /pose1 , /pose8 , /pose7  /pose9 , /cute , /superpose , /frog , /snake , /energyball , /maniac , /teleport , /float , /telekinesi , /fight , /wei , /fashion , /boxer , /bashful , /arabesque , /party")
          
        if        message.startswith("/lista") or    message.startswith("/emote list") or                                 message.startswith("/emote list") or message.startswith("/list"):
            await self.highrise.send_whisper(user.id,"/confused , /charging , /snowangel , /hot , /snowball , /curtsy , /bow ,/model , /greedy , /lust , /tired , /shy , /wave , /hello , /lau , /yes , /sad , /no , /kiss , /casual , /ren ,   /sit , /punk , /zombie , /gravity , /icecream ,/uwu , /sayso , /star")

        if        message.startswith("/lista") or    message.startswith("/emote list") or                                 message.startswith("/emote list") or message.startswith("/list"):
          await self.highrise.send_whisper(user.id,"/skating , /bitnervous , /scritchy , /timejump , /gottago , /jingle , /hyped , /sleigh , /surprise , /repose , /kawaii /touch , /pushit , /gift , /tiktok , /salute , /attention , /smooch , /launch")
        
        if        message.startswith("/lista") or         message.startswith("/emote list") or message.startswith("!emoteall") or message.startswith("!emote list") or message.startswith("!lista"):
            await self.highrise.send_emote("dance-floss")
                     
        if             message.startswith("!emotes") or message.startswith("/emotes"):
            await self.highrise.send_emote("emote-robot")
            await self.highrise.send_whisper(user.id,f"emotes available from number 1 to 97")

        if        message.startswith("-Help") or      message.startswith("/help") or      message.startswith("!help") or message.startswith("-help"):
            await self.highrise.chat(f"/lista | /pessoas | /emotes | | /marry me? | /play /fish /userinfo @ | !emoteall | !tele @ | !summon @ | !kick @ | !tele z,y,x | !tele @ z,y,x | ")
            await self.highrise.chat(f"[Emote] All | !emote all [Emote]")        
            await self.highrise.chat(f"{user.username} all activation codes must be used >> ! or/")
            await self.highrise.send_emote("dance-floss")
          
        if        message.startswith("😡") or      message.startswith("🤬") or      message.startswith("😤") or             message.startswith("🤨") or             message.startswith("😒") or message.startswith("🙄"):
            await self.highrise.send_emote("emote-boxer",user.id)
   
        if        message.startswith("🤔") or      message.startswith("🧐") or      message.startswith("🥸") or             message.startswith("🫤") or message.startswith("😕"):
            await self.highrise.send_emote("emote-confused",user.id)

        if        message.startswith("🤣") or      message.startswith("😂") or             message.startswith("ja") or             message.startswith("Ha") or         message.startswith("Ka") or           message.startswith("Ja") or           message.startswith("ha") or          message.startswith("ks") or             message.startswith("kk") or             message.startswith("Kk") or message.startswith("😁") or message.startswith("😀"):
            await self.highrise.send_emote("emote-laughing",user.id)

        if        message.startswith("😗") or      message.startswith("😘") or      message.startswith("😙") or             message.startswith("💋") or             message.startswith("😚"):
            await self.highrise.send_emote("emote-kiss",user.id)
            await self.highrise.send_emote("emote-blowkisses")

        if        message.startswith("😊") or      message.startswith("🥰") or      message.startswith("😳") or message.startswith("🤗"):
            await self.highrise.send_emote("idle-uwu",user.id)
            await self.highrise.send_emote("emote-blowkisses")

        if        message.startswith("🤢") or      message.startswith("🤮") or      message.startswith("🤧") or             message.startswith("😵‍💫") or message.startswith("🤒"):
            await self.highrise.send_emote("emoji-gagging",user.id)

        if        message.startswith("😱") or      message.startswith("😬") or      message.startswith("😰") or             message.startswith("😫") or message.startswith("😨"):
            await self.highrise.send_emote("idle-nervous",user.id)

        if message.startswith("🤯"):
            await self.highrise.send_emote("emote-headblowup",user.id)

        if        message.startswith("☺️") or      message.startswith("🫣") or       message.startswith("😍") or      message.startswith("🥺") or message.startswith("🥹"):
            await self.highrise.send_emote("emote-shy2",user.id)

        if        message.startswith("😏") or     message.startswith("🙃") or     message.startswith("🤤") or     message.startswith("😋") or     message.startswith("😏") or message.startswith("😈"):
            await self.highrise.send_emote("emote-lust",user.id)           

        if        message.startswith("🥵") or message.startswith("🫠"):
            await self.highrise.send_emote("emote-hot",user.id)
                                   
            
        if        message.startswith("/tp") or      message.startswith("!tp") or      message.startswith("tele") or          message.startswith("Tp") or          message.startswith("Tele") or  message.startswith("!tele"):
          target_username =         message.split("@")[-1].strip()
          await                     self.teleport_to_user(user, target_username)

        if                            message.startswith("Summon") or         message.startswith("Summom") or         message.startswith("!summom") or        message.startswith("/summom") or        message.startswith("/summon") or  message.startswith("!summon"):
          if user.username == "FallonXOXO" or user.username == "Its.Melly.Moo.XoXo" or user.username == "Shaun_Knox" or user.username == "sh1n1gam1699" or user.username == "Dreamy._.KY" or user.username == "hidinurbasement" or user.username == "@emping" or user.username == "_irii_" or user.username == "RayBM":
           target_username = message.split("@")[-1].strip()
           await self.teleport_user_next_to(target_username, user)
              
        if message.startswith("!kick"):
          if user.username == "FallonXOXO" or user.username == "RayBM":
              pass
          else:
              await self.highrise.chat("🤍.")
              return
          #separete message into parts
          parts = message.split()
          #check if message is valid "kick @username"
          if len(parts) != 2:
              await self.highrise.chat("🤍.")
              return
          #checks if there's a @ in the message
          if "@" not in parts[1]:
              username = parts[1]
          else:
              username = parts[1][1:]
          #check if user is in room
          room_users = (await self.highrise.get_room_users()).content
          for room_user, pos in room_users:
              if room_user.username.lower() == username.lower():
                  user_id = room_user.id
                  break
          if "user_id" not in locals():
              await self.highrise.chat("user not found, please fix the code coordinate ")
              return
          #kick user
          try:
              await self.highrise.moderate_room(user_id, "kick")
          except Exception as e:
              await self.highrise.chat(f"{e}")
              return
          #send message to chat
          await self.highrise.chat(f"{username} He was banned from the room!!")

    async def teleport(self, user: User, position: Position):
        try:
            await self.highrise.teleport(user.id, position)
        except Exception as e:
            print(f"Caught Teleport Error: {e}")

    async def teleport_to_user(self, user: User, target_username: str) -> None:
        try:
            room_users = await self.highrise.get_room_users()
            for target, position in room_users.content:
                if target.username.lower() == target_username.lower():
                    z = position.z
                    new_z = z - 1
                    await self.teleport(user, Position(position.x, position.y, new_z, position.facing))
                    break
        except Exception as e:
            print(f"An error occurred while teleporting to {target_username}: {e}")

    async def teleport_user_next_to(self, target_username: str, requester_user: User) -> None:
        try:
            # Get the position of the requester_user
            room_users = await self.highrise.get_room_users()
            requester_position = None
            for user, position in room_users.content:
                if user.id == requester_user.id:
                    requester_position = position
                    break

            # Find the target user and their position
            for user, position in room_users.content:
                if user.username.lower() == target_username.lower():
                    z = requester_position.z
                    new_z = z + 1  # Example: Move +1 on the z-axis (upwards)
                    await self.teleport(user, Position(requester_position.x, requester_position.y, new_z, requester_position.facing))
                    break
        except Exception as e:
            print(f"An error occurred while teleporting {target_username} next to {requester_user.username}: {e}")
          
    async def teleporter(self, message: str)-> None:
        """
            Teleports the user to the specified user or coordinate
            Usage: /teleport <username> <x,y,z>
                                                                """
        #separates the message into parts
        #part 1 is the command "/teleport"
        #part 2 is the name of the user to teleport to (if it exists)
        #part 3 is the coordinates to teleport to (if it exists)
        try:
            command, username, coordinate = message.split(" ")
        except:
            
            return
        
        #checks if the user is in the room
        room_users = (await self.highrise.get_room_users()).content
        for user in room_users:
            if user[0].username.lower() == username.lower():
                user_id = user[0].id
                break
        #if the user_id isn't defined, the user isn't in the room
        if "user_id" not in locals():
            
            return
            
        #checks if the coordinate is in the correct format (x,y,z)
        try:
            x, y, z = coordinate.split(",")
        except:
          
            return
        
        #teleports the user to the specified coordinate
        await self.highrise.teleport(user_id = user_id, dest = Position(float(x), float(y), float(z)))


    async def command_handler(self, user: User, message: str):
        parts = message.strip().split(" ")
        command = parts[0].lower()

        if command.startswith("-"):
            command = command[1:]

    # التعامل مع أوامر loop و stop مباشرة
        if command == "loop":
            await loop(self, user, message)
            return

        if command == "stop":
            await stop_loop(self, user, message)
            return

    # محاولة تنفيذ أوامر من ملفات في مجلد functions
        functions_folder = "functions"
        for file_name in os.listdir(functions_folder):
            if file_name.endswith(".py"):
                module_name = file_name[:-3]
                module_path = os.path.join(functions_folder, file_name)

                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, command) and callable(getattr(module, command)):
                    function = getattr(module, command)
                    await function(self, user, message)
                    return

    # إذا لم يكن هناك أمر معروف، فربما كتب اسم إيموجي مباشرة
        await check_and_start_emote_loop(self, user, message)
         
    async def on_whisper(self, user: User, message: str) -> None:
        print(f"{user.username} whispered: {message}")

        # Handle private messages for RayBM and botmes
        if user.username.lower() == "raybm" or user.username.lower() == "botmes":
            await self.highrise.chat(message)
            print(f"Broadcasted private message to the room: {message}")

        # ... (Your existing logic for other commands)

        if        message.startswith("tele") or              message.startswith("/tp") or              message.startswith("/fly") or     message.startswith("!tele") or      message.startswith("!tp") or     message.startswith("!fly"):
          if user.username == "FallonXOXO" or user.username == "Its.Melly.Moo.XoXo" or user.username == "sh1n1gam1699" or user.username == "Abbie_38" or user.username == "hidinurbasement" or user.username == "@emping" or user.username == "BabygirlFae"  or user.username == "RayBM":
            await self.teleporter(message)

        if        message.startswith("/") or              message.startswith("-") or              message.startswith(".") or          message.startswith("!"):
            await self.command_handler(user, message)

        if                            message.startswith("Summon") or         message.startswith("Summom") or         message.startswith("!summom") or        message.startswith("/summom") or        message.startswith("/summon") or  message.startswith("!summon"):
          if user.username == "FallonXOXO" or user.username == "Shaun_Knox" or user.username == "@Its.Melly.Moo.XoXo" or user.username == "@RayBM" or user.username == "Dreamy._.KY":
           target_username = message.split("@")[-1].strip()
           await self.teleport_user_next_to(target_username, user)

        if              message.startswith("Carteira") or  message.startswith("Wallet") or    message.startswith("wallet") or       message.startswith("carteira"):
          if user.username == "FallonXOXO" or user.username == "sh1n1gam1699" or user.username == "RayBM":
            wallet = (await self.highrise.get_wallet()).content
            await self.highrise.send_whisper(user.id,f"AMOUNT : {wallet[0].amount} {wallet[0].type}")
            await self.highrise.send_emote("emote-blowkisses")

    async def on_user_move(self, user: User, pos: Position) -> None:
        print (f"{user.username} moved to {pos}")

    async def on_emote(self, user: User, emote_id: str, receiver: User | None) -> None:
        print(f"{user.username} emoted: {emote_id}")
