import traceback

# Gold bar denominations mapping to Highrise tip IDs
BARS_DICTIONARY = {
    10000: "gold_bar_10k",
    5000: "gold_bar_5000",
    1000: "gold_bar_1k",
    500: "gold_bar_500",
    100: "gold_bar_100",
    50: "gold_bar_50",
    10: "gold_bar_10",
    5: "gold_bar_5",
    1: "gold_bar_1"
}

# Fees or additional cost mapping if needed (not used here, placeholder)
FEES_DICTIONARY = {
    10000: 1000,
    5000: 500,
    1000: 100,
    500: 50,
    100: 10,
    50: 5,
    10: 1,
    5: 1,
    1: 1
}

async def handle_tip_commands(bot, user, message: str):
    """
    Handle tipping related commands:
    - !tip <amount> : tips the user themselves
    - !tipall <amount> : tips all users in the room
    - !wallet : shows the bot's gold balance
    Returns True if a command was handled, False otherwise.
    """
    try:
        low_msg = message.lower().strip()
        if low_msg == "!wallet":
            # Show wallet balance
            try:
                wallet = await bot.highrise.get_wallet()
                if wallet and wallet.content:
                    total_gold = sum(item.amount for item in wallet.content)
                    await bot.highrise.chat(f"💰 Bot wallet contains {total_gold} gold bars.")
                else:
                    await bot.highrise.chat("Unable to fetch wallet info.")
            except Exception:
                traceback.print_exc()
                await bot.highrise.chat("Error fetching wallet info.")
            return True

        if low_msg.startswith("!tip "):
            parts = low_msg.split(" ")
            if len(parts) != 2:
                await bot.highrise.chat("Usage: !tip <amount>")
                return True
            try:
                amount = int(parts[1])
                if amount <= 0:
                    await bot.highrise.chat("Tip amount must be greater than zero.")
                    return True
            except ValueError:
                await bot.highrise.chat("Invalid amount. Please enter a number.")
                return True

            # Check bot wallet amount
            try:
                wallet = await bot.highrise.get_wallet()
                bot_amount = sum(item.amount for item in wallet.content) if wallet and wallet.content else 0
            except Exception:
                traceback.print_exc()
                await bot.highrise.chat("Error fetching wallet info.")
                return True

            if bot_amount < amount:
                await bot.highrise.chat("Not enough funds in the bot's wallet.")
                return True

            # Prepare tip bars
            tip_bars = []
            remaining = amount
            for bar_value in sorted(BARS_DICTIONARY.keys(), reverse=True):
                count = remaining // bar_value
                if count > 0:
                    tip_bars.extend([BARS_DICTIONARY[bar_value]] * count)
                    remaining %= bar_value

            # Tip the user
            try:
                for bar in tip_bars:
                    await bot.highrise.tip_user(user.id, bar)
                await bot.highrise.chat(f"@{user.username} has been tipped {amount} gold bars!")
            except Exception:
                traceback.print_exc()
                await bot.highrise.chat("Failed to send tip.")
            return True

        if low_msg.startswith("!tipall "):
            parts = low_msg.split(" ")
            if len(parts) != 2:
                await bot.highrise.chat("Usage: !tipall <amount>")
                return True
            try:
                amount = int(parts[1])
                if amount <= 0:
                    await bot.highrise.chat("Tip amount must be greater than zero.")
                    return True
            except ValueError:
                await bot.highrise.chat("Invalid amount. Please enter a number.")
                return True

            # Get room users
            try:
                room_users = await bot.highrise.get_users_in_room()
            except Exception:
                traceback.print_exc()
                await bot.highrise.chat("Failed to get users in room.")
                return True

            if not room_users:
                await bot.highrise.chat("No users found in the room to tip.")
                return True

            total_amount = amount * len(room_users)

            # Check bot wallet amount
            try:
                wallet = await bot.highrise.get_wallet()
                bot_amount = sum(item.amount for item in wallet.content) if wallet and wallet.content else 0
            except Exception:
                traceback.print_exc()
                await bot.highrise.chat("Error fetching wallet info.")
                return True

            if bot_amount < total_amount:
                await bot.highrise.chat("Not enough funds in the bot's wallet to tip everyone.")
                return True

            # Prepare tip bars for each tip amount
            tip_bars = []
            remaining = amount
            for bar_value in sorted(BARS_DICTIONARY.keys(), reverse=True):
                count = remaining // bar_value
                if count > 0:
                    tip_bars.extend([BARS_DICTIONARY[bar_value]] * count)
                    remaining %= bar_value

            # Tip each user in the room
            failed_users = []
            for target_user in room_users:
                try:
                    for bar in tip_bars:
                        await bot.highrise.tip_user(target_user.id, bar)
                    # Slow down to avoid rate limits
                    await asyncio.sleep(0.25)
                except Exception:
                    traceback.print_exc()
                    failed_users.append(target_user.username)

            msg = f"Tipped {amount} gold bars to {len(room_users) - len(failed_users)} users."
            if failed_users:
                msg += f" Failed to tip: {', '.join(failed_users)}."
            await bot.highrise.chat(msg)
            return True

        return False  # command not handled

    except Exception:
        traceback.print_exc()
        return False