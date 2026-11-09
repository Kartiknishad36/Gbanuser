from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from database.mongo import (
    set_welcome_enabled, get_welcome_enabled,
    set_welcome_text, get_welcome_text,
)
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


@app.on_message(filters.command("welcome", prefixes=PREFIXES) & filters.group)
@sudo_only
async def welcome_cmd(client, message: Message):
    if len(message.command) < 2:
        enabled = await get_welcome_enabled(message.chat.id)
        return await message.reply_text(
            f"Welcome is currently **{'ON' if enabled else 'OFF'}**.\n"
            "Usage: `.welcome on` / `.welcome off`"
        )
    arg = message.command[1].lower()
    if arg in ("on", "yes", "true", "1"):
        await set_welcome_enabled(message.chat.id, True)
        await message.reply_text("✅ Welcome messages enabled.")
    elif arg in ("off", "no", "false", "0"):
        await set_welcome_enabled(message.chat.id, False)
        await message.reply_text("✅ Welcome messages disabled.")
    else:
        await message.reply_text("Usage: `.welcome on` / `.welcome off`")


@app.on_message(filters.command("setwelcome", prefixes=PREFIXES) & filters.group)
@sudo_only
async def setwelcome_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Usage: `.setwelcome <text>`\n"
            "Placeholders: `{mention}`, `{chat}`, `{id}`"
        )
    text = message.text.split(None, 1)[1]
    await set_welcome_text(message.chat.id, text)
    await message.reply_text("✅ Welcome message updated.")


@app.on_message(filters.new_chat_members & filters.group)
async def welcome_new_member(client, message: Message):
    if not await get_welcome_enabled(message.chat.id):
        return
    text_template = await get_welcome_text(message.chat.id)
    for user in message.new_chat_members:
        if user.is_bot:
            continue
        text = text_template.format(
            mention=user.mention,
            chat=message.chat.title or "this chat",
            id=user.id,
        )
        try:
            await message.reply_text(text)
        except Exception:
            pass
