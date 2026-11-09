from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import RPCError

from core.clients import app
from database.mongo import add_gban, remove_gban, get_gban_list, is_gbanned
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


def cmd(name):
    return filters.command(name, prefixes=PREFIXES)


@app.on_message(cmd(["gban"]))
@sudo_only
async def gban_cmd(client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Reply to a user or give user ID / username.")

    if message.reply_to_message:
        user = message.reply_to_message.from_user
        user_id = user.id
        mention = user.mention
    else:
        try:
            user = await client.get_users(message.command[1])
            user_id = user.id
            mention = user.mention
        except Exception:
            return await message.reply_text("Could not find that user.")

    reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason"
    await add_gban(user_id, reason)

    # Try to ban in current chat too
    try:
        await client.ban_chat_member(message.chat.id, user_id)
    except Exception:
        pass

    await message.reply_text(f"🚫 <b>Globally banned</b> {mention}\nReason: {reason}")


@app.on_message(cmd(["ungban"]))
@sudo_only
async def ungban_cmd(client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Reply to a user or give user ID.")

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        mention = message.reply_to_message.from_user.mention
    else:
        try:
            user = await client.get_users(message.command[1])
            user_id = user.id
            mention = user.mention
        except Exception:
            return await message.reply_text("Could not find that user.")

    await remove_gban(user_id)
    await message.reply_text(f"✅ <b>Ungbanned</b> {mention}")


@app.on_message(cmd(["gbanlist"]))
@sudo_only
async def gbanlist_cmd(client, message: Message):
    gban_list = await get_gban_list()
    if not gban_list:
        return await message.reply_text("No globally banned users.")
    text = "**Global Ban List**\n\n"
    for entry in gban_list[:50]:
        text += f"• `{entry.get('user_id')}` — {entry.get('reason', 'No reason')}\n"
    await message.reply_text(text)
