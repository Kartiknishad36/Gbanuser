"""
.bro — Global Auto-Reply system.

Usage:
  Reply to someone + .bro        → Enable global auto-reply for that user
  .bro off  (or .unbro)          → Disable auto-reply (reply to user or give ID)
  .brolist                       → Show all users with auto-reply enabled

Once enabled, whenever that user sends a message (in any group or DM),
the userbot will automatically reply with a random line + mention.
"""
import random
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from database.mongo import add_bro_target, remove_bro_target, get_bro_targets, is_bro_target
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]

BRO_LINES = [
    "kya haal hai bhai?",
    "sunao kya chal raha hai",
    "bhai kahan busy ho",
    "yaad aa raha tha tera",
    "kya scene hai aajkal",
    "bhai full on mood mein ho kya",
    "chal milte hain kabhi",
    "kya baat hai bhai",
    "sab theek?",
    "bhai tension mat le",
    "kya haal chaal",
    "sunna tha kuch naya",
    "bhai kya scene hai",
    "kahan gum ho",
    "yaad kiya tujhe",
]


@app.on_message(filters.command(["bro"], prefixes=PREFIXES))
@sudo_only
async def bro_cmd(client, message: Message):
    if len(message.command) > 1 and message.command[1].lower() in ("off", "stop", "disable"):
        # Disable
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        elif len(message.command) > 2:
            try:
                user_id = int(message.command[2])
            except ValueError:
                return await message.reply_text("Invalid user ID.")
        else:
            return await message.reply_text("Reply to user or give ID to disable.")
        await remove_bro_target(user_id)
        return await message.reply_text(f"✅ Auto-reply disabled for `{user_id}`")

    if not message.reply_to_message:
        return await message.reply_text("Reply to a user with `.bro` to enable auto-reply.")

    user = message.reply_to_message.from_user
    await add_bro_target(user.id)
    await message.reply_text(f"✅ Global auto-reply enabled for {user.mention}")


@app.on_message(filters.command(["unbro"], prefixes=PREFIXES))
@sudo_only
async def unbro_cmd(client, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            user_id = int(message.command[1])
        except ValueError:
            return await message.reply_text("Invalid user ID.")
    else:
        return await message.reply_text("Reply to user or give ID.")
    await remove_bro_target(user_id)
    await message.reply_text(f"✅ Auto-reply disabled for `{user_id}`")


@app.on_message(filters.command(["brolist"], prefixes=PREFIXES))
@sudo_only
async def brolist_cmd(client, message: Message):
    targets = await get_bro_targets()
    if not targets:
        return await message.reply_text("No users have auto-reply enabled.")
    text = "**Bro Auto-Reply List**\n\n" + "\n".join(f"• `{uid}`" for uid in targets)
    await message.reply_text(text)


@app.on_message(filters.incoming & ~filters.bot & ~filters.service & ~filters.me)
async def bro_auto_reply(client, message: Message):
    if not message.from_user:
        return
    user_id = message.from_user.id
    if not await is_bro_target(user_id):
        return

    # Don't reply to commands
    if message.text and message.text.startswith((".", "!", "/")):
        return

    line = random.choice(BRO_LINES)
    user = message.from_user
    mention = user.mention if user.first_name else f"<a href='tg://user?id={user.id}'>{user.first_name or 'User'}</a>"
    text = f"{mention}, {line}"

    try:
        await message.reply_text(text)
    except Exception:
        pass
