from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from core.call_manager import (
    get_queue, get_current, skip_track, stop_all, ensure_started
)
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]


def cmd(name):
    return filters.command(name, prefixes=PREFIXES) & filters.group


@app.on_message(cmd(["pause", "resume", "skip", "stop", "queue"]))
@sudo_only
async def controls_cmd(client, message: Message):
    chat_id = message.chat.id
    command = message.command[0].lower()

    if command == "queue":
        queue = get_queue(client, chat_id)
        current = get_current(client).get(chat_id)
        if not current and not queue:
            return await message.reply_text("Queue is empty.")
        text = "🎵 <b>Current Queue</b>\n\n"
        if current:
            text += f"▶ <b>Now:</b> {current.get('title', 'Unknown')}\n\n"
        for i, track in enumerate(queue, 1):
            text += f"{i}. {track.get('title', 'Unknown')}\n"
        return await message.reply_text(text)

    if command == "skip":
        next_track = await skip_track(client, chat_id)
        if next_track:
            await message.reply_text(f"⏭️ Skipped. Now playing: <b>{next_track.get('title')}</b>")
        else:
            await message.reply_text("⏭️ Skipped. Queue empty, left VC.")
        return

    if command == "stop":
        await stop_all(client, chat_id)
        await message.reply_text("⏹️ Stopped and cleared queue.")
        return

    await message.reply_text(f"Command `{command}` received.")
