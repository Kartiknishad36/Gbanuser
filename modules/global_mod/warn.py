from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from database.mongo import add_warn, get_warns, reset_warns
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
MAX_WARNS = 3


def cmd(name):
    return filters.command(name, prefixes=PREFIXES) & filters.group


@app.on_message(cmd("warn"))
@sudo_only
async def warn_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user you want to warn.")

    user = message.reply_to_message.from_user
    reason = " ".join(message.command[1:]) if len(message.command) > 1 else "No reason"
    count = await add_warn(message.chat.id, user.id, reason)

    text = f"⚠️ {user.mention} has been warned ({count}/{MAX_WARNS})\nReason: {reason}"
    if count >= MAX_WARNS:
        try:
            await client.ban_chat_member(message.chat.id, user.id)
            text += f"\n\n🚫 Auto-banned after {MAX_WARNS} warns."
            await reset_warns(message.chat.id, user.id)
        except Exception:
            text += "\n(Could not ban)"
    await message.reply_text(text)


@app.on_message(cmd("unwarn"))
@sudo_only
async def unwarn_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user.")
    user = message.reply_to_message.from_user
    await reset_warns(message.chat.id, user.id)
    await message.reply_text(f"✅ Warns reset for {user.mention}")


@app.on_message(cmd("warns"))
@sudo_only
async def warns_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user.")
    user = message.reply_to_message.from_user
    warns = await get_warns(message.chat.id, user.id)
    if not warns:
        return await message.reply_text(f"{user.mention} has no warns.")
    text = f"**Warns for {user.mention}** ({len(warns)})\n\n"
    for i, r in enumerate(warns, 1):
        text += f"{i}. {r or 'No reason'}\n"
    await message.reply_text(text)


@app.on_message(cmd("resetwarns"))
@sudo_only
async def resetwarns_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user.")
    user = message.reply_to_message.from_user
    await reset_warns(message.chat.id, user.id)
    await message.reply_text(f"✅ All warns cleared for {user.mention}")
