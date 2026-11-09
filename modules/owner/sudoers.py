from functools import wraps
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import OWNER_ID, PREFIXES
from database.mongo import get_sudoers, add_sudo, remove_sudo


def sudo_only(func):
    """Decorator: only OWNER_ID and sudo users can run the command."""
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs):
        user_id = message.from_user.id if message.from_user else 0
        sudoers = await get_sudoers()
        if user_id != OWNER_ID and user_id not in sudoers:
            return
        return await func(client, message, *args, **kwargs)
    return wrapper


def cmd(name):
    return filters.command(name, prefixes=PREFIXES)


@app.on_message(cmd(["addsudo"]))
@sudo_only
async def addsudo_cmd(client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Reply to a user or give user ID.")
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        try:
            user_id = int(message.command[1])
        except ValueError:
            return await message.reply_text("Invalid user ID.")
    if user_id == OWNER_ID:
        return await message.reply_text("Owner is already sudo.")
    await add_sudo(user_id)
    await message.reply_text(f"✅ Added `{user_id}` as sudo.")


@app.on_message(cmd(["delsudo"]))
@sudo_only
async def delsudo_cmd(client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Reply to a user or give user ID.")
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        try:
            user_id = int(message.command[1])
        except ValueError:
            return await message.reply_text("Invalid user ID.")
    await remove_sudo(user_id)
    await message.reply_text(f"✅ Removed `{user_id}` from sudo.")


@app.on_message(cmd(["sudolist"]))
@sudo_only
async def sudolist_cmd(client, message: Message):
    sudoers = await get_sudoers()
    text = f"**Sudo Users**\n\nOwner: `{OWNER_ID}`\n\n"
    if sudoers:
        text += "\n".join(f"• `{uid}`" for uid in sudoers)
    else:
        text += "No additional sudo users."
    await message.reply_text(text)
