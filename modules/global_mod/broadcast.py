import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import RPCError, FloodWait

from core.clients import app
from database.mongo import get_all_chats
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


@app.on_message(filters.command("broadcast", prefixes=PREFIXES))
@sudo_only
async def broadcast_cmd(client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        msg = await message.reply_text(
            "Usage: `.broadcast <text>` or reply to a message with `.broadcast`"
        )
        return

    chats = await get_all_chats()
    if not chats:
        msg = await message.reply_text("No chats recorded yet.")
        return

    status = await message.reply_text(f"📡 Broadcasting to {len(chats)} chats...")
    success = 0
    failed = 0

    for chat_id in chats:
        try:
            if message.reply_to_message:
                await message.reply_to_message.copy(chat_id)
            else:
                text = message.text.split(None, 1)[1]
                await client.send_message(chat_id, text)
            success += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                if message.reply_to_message:
                    await message.reply_to_message.copy(chat_id)
                else:
                    await client.send_message(chat_id, text)
                success += 1
            except Exception:
                failed += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.3)

    await status.edit_text(f"✅ Broadcast done.\nSuccess: {success}\nFailed: {failed}")
