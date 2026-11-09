import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
TAG_BATCH = 5
_stop_flags: dict[int, bool] = {}


@app.on_message(filters.command("tagall", prefixes=PREFIXES) & filters.group)
@sudo_only
async def tagall_cmd(client, message: Message):
    chat_id = message.chat.id
    _stop_flags[chat_id] = False

    extra = ""
    if len(message.command) > 1:
        extra = message.text.split(None, 1)[1]

    status = await message.reply_text("📣 Tagging members...")
    members = []
    async for m in client.get_chat_members(chat_id):
        if not m.user.is_bot:
            members.append(m.user)

    if not members:
        await status.edit_text("No members found.")
        return

    tagged = 0
    for i in range(0, len(members), TAG_BATCH):
        if _stop_flags.get(chat_id):
            await status.edit_text(f"⏹ Stopped. Tagged {tagged} members.")
            return
        batch = members[i:i + TAG_BATCH]
        mentions = " ".join(u.mention for u in batch)
        text = f"{extra}\n\n{mentions}" if extra else mentions
        try:
            await client.send_message(chat_id, text)
            tagged += len(batch)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass
        await asyncio.sleep(1.5)

    await status.edit_text(f"✅ Tagged {tagged} members.")


@app.on_message(filters.command("tagallstop", prefixes=PREFIXES) & filters.group)
@sudo_only
async def tagallstop_cmd(client, message: Message):
    _stop_flags[message.chat.id] = True
    await message.reply_text("⏹ Tagall stop requested.")


@app.on_message(filters.command("tagme", prefixes=PREFIXES) & filters.group)
@sudo_only
async def tagme_cmd(client, message: Message):
    await message.reply_text(message.from_user.mention)
