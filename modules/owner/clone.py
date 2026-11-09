"""
.clone <bot_token> lets someone run their own branded bot that gets the
full command set (including music/VC).
"""
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import RPCError

from core.clients import app
from core.clone_handlers import register_common_handlers
from core.call_manager import ensure_started
from config import API_ID, API_HASH, PREFIXES
from modules.owner.sudoers import sudo_only

CLONES: dict[str, Client] = {}


@app.on_message(filters.command("clone", prefixes=PREFIXES))
@sudo_only
async def clone_cmd(client, message: Message):
    if len(message.command) < 2:
        msg = await message.reply_text(
            "Usage: `.clone <bot_token>`\n\n"
            "The token is sensitive — only use this in private."
        )
        return

    bot_token = message.command[1]
    if bot_token in CLONES:
        msg = await message.reply_text("This bot token is already running as a clone.")
        return

    status = await message.reply_text("🔄 Starting clone...")

    try:
        clone_client = Client(
            name=f"clone_{bot_token.split(':')[0]}",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=bot_token,
            in_memory=True,
        )
        await register_common_handlers(clone_client)
        await clone_client.start()
        try:
            await ensure_started(clone_client)
        except Exception:
            pass
        CLONES[bot_token] = clone_client
        me = await clone_client.get_me()
        await status.edit_text(
            f"✅ Clone started: @{me.username}\n\n"
            f"It has the full command set, including music."
        )
    except RPCError as e:
        await status.edit_text(f"❌ Failed to start clone: `{e}`")
    except Exception as e:
        await status.edit_text(f"❌ Failed to start clone: `{type(e).__name__}: {e}`")


@app.on_message(filters.command("unclone", prefixes=PREFIXES))
@sudo_only
async def unclone_cmd(client, message: Message):
    if len(message.command) < 2:
        msg = await message.reply_text("Usage: `.unclone <bot_token>`")
        return
    bot_token = message.command[1]
    clone_client = CLONES.pop(bot_token, None)
    if not clone_client:
        msg = await message.reply_text("No running clone with that token.")
        return
    try:
        await clone_client.stop()
    except Exception:
        pass
    await message.reply_text("✅ Clone stopped and removed.")
