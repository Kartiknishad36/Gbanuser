"""
.sha  and  .love  — a single command each, three modes:

  .sha                (no reply, no args)  -> one-shot shayari, tags the whole group
  .sha  (reply to X)                       -> one-shot shayari, tags just that person
  .sha <minutes>                           -> starts a recurring group broadcast
  .sha stop                                -> stops the recurring broadcast

Same three modes for `.love`. Recurring mode has a minimum interval so it
can't be used to spam even in your own group.
"""
import asyncio
import random
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import RPCError, FloodWait

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]
MIN_INTERVAL_MINUTES = 10
TAG_BATCH_SIZE = 5

# Original content pools
SHAYARI_LINES = [
    "Dil ki baat labon tak aane nahi paayi,\nAur aankhon ne sab keh diya...",
    "Tumhare bina yeh raatein adhoori si lagti hain,\nJaise chaand bin sitaron ka aasmaan.",
    "Mohabbat mein gham bhi mithe lagte hain,\nJab saath ho koi apna...",
    "Aankhon mein base ho tum, dil mein samaaye ho,\nHar saans mein bas tumhari hi khushboo aaye ho.",
    "Zindagi ek kitaab si hai,\nTum uske sabse khoobsurat panne ho.",
    "Dil toota hai to kya hua,\nPhir se jod lenge hum, tumhare saath.",
    "Tumse milke aisa laga,\nJaise barson se kisi intezaar ka ant ho gaya.",
    "Chandni raaton mein tumhara khayal aata hai,\nAur neend door chali jaati hai.",
    "Ishq mein doobna maza deti hai,\nJab saahil bhi tumhi ho.",
    "Tumhari muskaan mein chhupi hai meri duniya,\nUske bina main adhura hoon.",
]

LOVE_LINES = [
    "Tum meri pehli aur aakhri mohabbat ho.",
    "Har dil ki dhadkan mein tumhara naam likha hai.",
    "Tumse pyaar karna meri aadat ban gayi hai.",
    "Tumhare bina zindagi adhoori si lagti hai.",
    "Main tumhe har roz naya pyaar karta hoon.",
    "Tum meri duniya ke sabse khoobsurat hissa ho.",
    "Tumhare saath bitaye har pal anmol hain.",
    "Dil se dil tak ka safar tumhi se shuru hota hai.",
    "Tum meri subah aur meri raat dono ho.",
    "Pyaar sirf ek lafz nahi, tum ho.",
]

_running_tasks: dict[str, asyncio.Task] = {}


async def _send_shayari(client, chat_id, lines, tag_user=None):
    line = random.choice(lines)
    if tag_user:
        text = f"{tag_user.mention}\n\n{line}"
    else:
        text = line
    try:
        await client.send_message(chat_id, text)
    except Exception:
        pass


@app.on_message(filters.command(["sha", "shayari"], prefixes=PREFIXES))
@sudo_only
async def sha_cmd(client, message: Message):
    await _handle_romantic_cmd(client, message, SHAYARI_LINES, "sha")


@app.on_message(filters.command(["love"], prefixes=PREFIXES))
@sudo_only
async def love_cmd(client, message: Message):
    await _handle_romantic_cmd(client, message, LOVE_LINES, "love")


async def _handle_romantic_cmd(client, message: Message, lines, key):
    chat_id = message.chat.id
    task_key = f"{key}:{chat_id}"

    if len(message.command) > 1 and message.command[1].lower() == "stop":
        task = _running_tasks.pop(task_key, None)
        if task:
            task.cancel()
            await message.reply_text("⏹ Stopped.")
        else:
            await message.reply_text("Nothing running.")
        return

    if len(message.command) > 1:
        try:
            minutes = int(message.command[1])
            if minutes < MIN_INTERVAL_MINUTES:
                return await message.reply_text(f"Minimum interval is {MIN_INTERVAL_MINUTES} minutes.")
        except ValueError:
            return await message.reply_text("Usage: `.sha <minutes>` or `.sha stop`")

        if task_key in _running_tasks:
            return await message.reply_text("Already running. Use stop first.")

        async def loop():
            while True:
                await _send_shayari(client, chat_id, lines)
                await asyncio.sleep(minutes * 60)

        _running_tasks[task_key] = asyncio.create_task(loop())
        await message.reply_text(f"✅ Started every {minutes} min. Use `.sha stop` to stop.")
        return

    # One-shot
    tag_user = message.reply_to_message.from_user if message.reply_to_message else None
    await _send_shayari(client, chat_id, lines, tag_user)
