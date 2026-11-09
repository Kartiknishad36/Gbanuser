from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import RPCError

from core.clients import app
from database.mongo import add_gmute, remove_gmute, is_gmuted, get_gmute_list
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


def cmd(name):
    return filters.command(name, prefixes=PREFIXES)


@app.on_message(cmd(["gmute"]))
@sudo_only
async def gmute_cmd(client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Reply to a user or give user ID.")

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
    await add_gmute(user_id, reason)

    try:
        await client.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions(can_send_messages=False),
        )
    except Exception:
        pass

    await message.reply_text(f"🔇 <b>Globally muted</b> {mention}\nReason: {reason}")


@app.on_message(cmd(["gunmute"]))
@sudo_only
async def gunmute_cmd(client, message: Message):
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

    await remove_gmute(user_id)
    try:
        await client.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions(can_send_messages=True),
        )
    except Exception:
        pass

    await message.reply_text(f"🔊 <b>Globally unmuted</b> {mention}")
