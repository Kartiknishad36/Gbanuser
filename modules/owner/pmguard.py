from pyrogram import filters
from pyrogram.types import Message

from core.clients import app
from config import OWNER_ID
from modules.owner.sudoers import sudo_only
from database.mongo import approve_pm, unapprove_pm, get_approved_pm

PREFIXES = [".", "!"]

# Simple in-memory flood tracking for PM Guard
_pm_warnings: dict[int, int] = {}
MAX_PM_WARNS = 3


@app.on_message(filters.private & filters.incoming & ~filters.bot & ~filters.service)
async def pm_guard(client, message: Message):
    user_id = message.from_user.id
    if user_id == OWNER_ID:
        return
    approved = await get_approved_pm()
    if user_id in approved:
        return

    # Ignore commands from sudo (they shouldn't hit this usually)
    if message.text and message.text.startswith((".", "!")):
        return

    count = _pm_warnings.get(user_id, 0) + 1
    _pm_warnings[user_id] = count

    if count >= MAX_PM_WARNS:
        try:
            await client.block_user(user_id)
            await message.reply_text("You have been blocked for spamming.")
        except Exception:
            pass
        _pm_warnings.pop(user_id, None)
    else:
        await message.reply_text(
            f"⚠️ Please don't spam. Warning {count}/{MAX_PM_WARNS}.\n"
            "If you need something, contact the owner."
        )


@app.on_message(filters.command("approve", prefixes=PREFIXES))
@sudo_only
async def approve_cmd(client, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            user_id = int(message.command[1])
        except ValueError:
            return await message.reply_text("Invalid user ID.")
    else:
        return await message.reply_text("Reply to a user or give ID.")

    await approve_pm(user_id)
    _pm_warnings.pop(user_id, None)
    await message.reply_text(f"✅ Approved `{user_id}` for PMs.")


@app.on_message(filters.command("unapprove", prefixes=PREFIXES))
@sudo_only
async def unapprove_cmd(client, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            user_id = int(message.command[1])
        except ValueError:
            return await message.reply_text("Invalid user ID.")
    else:
        return await message.reply_text("Reply to a user or give ID.")

    await unapprove_pm(user_id)
    await message.reply_text(f"✅ Unapproved `{user_id}`.")


@app.on_message(filters.command("approved", prefixes=PREFIXES))
@sudo_only
async def approved_list_cmd(client, message: Message):
    approved = await get_approved_pm()
    if not approved:
        return await message.reply_text("No approved users.")
    text = "**Approved PM users**\n\n" + "\n".join(f"• `{uid}`" for uid in approved)
    await message.reply_text(text)
