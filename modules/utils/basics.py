import time
from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import BOT_NAME
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


def cmd(name):
    return filters.command(name, prefixes=PREFIXES)


@app.on_message(cmd("ping"))
@sudo_only
async def ping_cmd(client, message: Message):
    start = time.time()
    msg = await message.reply_text("Pinging...")
    end = time.time()
    await msg.edit_text(f"🏓 Pong! `{round((end - start) * 1000, 2)} ms`")


@app.on_message(cmd(["id", "ids"]))
@sudo_only
async def id_cmd(client, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        text = (
            f"👤 <b>Replied User</b>\n"
            f"ID: <code>{user.id}</code>\n"
            f"Name: {user.first_name}\n"
        )
        if message.reply_to_message.chat:
            text += f"Chat ID: <code>{message.chat.id}</code>"
    else:
        text = (
            f"👤 <b>Your ID:</b> <code>{message.from_user.id}</code>\n"
            f"💬 <b>Chat ID:</b> <code>{message.chat.id}</code>"
        )
    await message.reply_text(text)


@app.on_message(cmd(["info", "whois"]))
@sudo_only
async def whois_cmd(client, message: Message):
    # Redirect style - actual info is in utils/info.py
    from modules.utils.info import info_cmd
    await info_cmd(client, message)


@app.on_message(cmd(["echo", "say"]))
@sudo_only
async def echo_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `.echo <text>`")
    text = message.text.split(None, 1)[1]
    await message.reply_text(text)
    try:
        await message.delete()
    except Exception:
        pass


@app.on_message(cmd(["del", "delete"]))
@sudo_only
async def delete_cmd(client, message: Message):
    if message.reply_to_message:
        try:
            await message.reply_to_message.delete()
            await message.delete()
        except Exception:
            pass


@app.on_message(cmd(["purge"]))
@sudo_only
async def purge_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to purge from.")
    start_id = message.reply_to_message.id
    end_id = message.id
    ids = list(range(start_id, end_id + 1))
    deleted = 0
    for i in range(0, len(ids), 100):
        chunk = ids[i:i+100]
        try:
            await client.delete_messages(message.chat.id, chunk)
            deleted += len(chunk)
        except Exception:
            continue
    status = await client.send_message(message.chat.id, f"🧹 Purged {deleted} messages.")


@app.on_message(cmd(["help", "cmds", "commands"]))
@sudo_only
async def help_cmd(client, message: Message):
    text = f"""
<b>{BOT_NAME} Commands</b>

<b>Basic</b>
• .ping — latency check
• .id — get user/chat id
• .info — user info
• .echo <text>
• .help

<b>Music / VC</b>
• .play / .vply <query>
• .skip / .stop / .pause / .resume
• .queue

<b>Moderation</b>
• .ban / .unban / .kick / .mute / .unmute
• .gban / .ungban / .gmute / .gunmute
• .warn / .unwarn / .warns
• .tagall / .tagallstop
• .broadcast <text>

<b>Fun</b>
• .sha / .love
• .joke / .quote / .dice / .coin
• .bro (auto-reply)

<b>Owner</b>
• .addsudo / .delsudo / .sudolist
• .clone / .unclone
• .approve / .unapprove
• .login (via bot)
"""
    await message.reply_text(text)
