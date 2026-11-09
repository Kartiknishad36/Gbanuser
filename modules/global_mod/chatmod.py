from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import RPCError

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


def cmd(name):
    return filters.command(name, prefixes=PREFIXES) & filters.group


@app.on_message(cmd(["ban"]))
@sudo_only
async def ban_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user to ban.")
    user = message.reply_to_message.from_user
    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await message.reply_text(f"🚫 Banned {user.mention}")
    except Exception as e:
        await message.reply_text(f"Failed: `{e}`")


@app.on_message(cmd(["unban"]))
@sudo_only
async def unban_cmd(client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Reply to user or give ID.")
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        mention = message.reply_to_message.from_user.mention
    else:
        try:
            user = await client.get_users(message.command[1])
            user_id = user.id
            mention = user.mention
        except Exception:
            return await message.reply_text("User not found.")
    try:
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply_text(f"✅ Unbanned {mention}")
    except Exception as e:
        await message.reply_text(f"Failed: `{e}`")


@app.on_message(cmd(["kick"]))
@sudo_only
async def kick_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user to kick.")
    user = message.reply_to_message.from_user
    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await client.unban_chat_member(message.chat.id, user.id)
        await message.reply_text(f"👢 Kicked {user.mention}")
    except Exception as e:
        await message.reply_text(f"Failed: `{e}`")


@app.on_message(cmd(["mute"]))
@sudo_only
async def mute_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user to mute.")
    user = message.reply_to_message.from_user
    try:
        await client.restrict_chat_member(
            message.chat.id, user.id,
            ChatPermissions(can_send_messages=False)
        )
        await message.reply_text(f"🔇 Muted {user.mention}")
    except Exception as e:
        await message.reply_text(f"Failed: `{e}`")


@app.on_message(cmd(["unmute"]))
@sudo_only
async def unmute_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user to unmute.")
    user = message.reply_to_message.from_user
    try:
        await client.restrict_chat_member(
            message.chat.id, user.id,
            ChatPermissions(can_send_messages=True)
        )
        await message.reply_text(f"🔊 Unmuted {user.mention}")
    except Exception as e:
        await message.reply_text(f"Failed: `{e}`")
