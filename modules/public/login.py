"""
Two ways to log an account in (owner/sudo only, PM-only for safety):

  1. `.login <string_session>` — paste an existing Pyrogram string session directly.
  2. `.login` (no args) — guided phone number + OTP flow: bot asks for your phone
     number, sends you a Telegram login code, you reply with the code (+ 2FA
     password if you have one), and the bot logs you in automatically.

Either way, a separate Client is started for that session. Multiple sessions
can be added and stay active AT THE SAME TIME.
"""
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired,
    PhoneNumberInvalid, PasswordHashInvalid, FloodWait, RPCError,
)

from core.clients import bot

if bot is None:
    raise RuntimeError(
        "modules.public.login requires BOT_TOKEN to be set in .env — "
        "the self-service login/clone flow runs through the bot account."
    )

from core.clone_handlers import register_common_handlers
from core.call_manager import ensure_started
from config import API_ID, API_HASH, OWNER_ID
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]

# account_user_id -> session info
ACTIVE_SESSIONS: dict[int, dict] = {}
CLIENT_TO_SESSION: dict[int, dict] = {}
LOGIN_STATES: dict[int, dict] = {}


def _can_manage(entry: dict, requester_id: int) -> bool:
    if requester_id == OWNER_ID:
        return True
    return entry.get("added_by") == requester_id


@bot.on_message(filters.command(["login"], prefixes=PREFIXES) & filters.private)
@sudo_only
async def login_cmd(client, message: Message):
    user_id = message.from_user.id

    # Direct string session
    if len(message.command) > 1:
        session_string = message.command[1]
        status = await message.reply_text("🔄 Logging in with session string...")
        try:
            new_client = Client(
                name=f"login_{user_id}_{int(asyncio.get_event_loop().time())}",
                api_id=API_ID,
                api_hash=API_HASH,
                session_string=session_string,
                in_memory=True,
            )
            await register_common_handlers(new_client)
            await new_client.start()
            me = await new_client.get_me()
            try:
                await ensure_started(new_client)
            except Exception:
                pass

            entry = {
                "client": new_client,
                "user_id": me.id,
                "username": me.username,
                "added_by": user_id,
                "name": me.first_name,
            }
            # Replace if same account already logged
            ACTIVE_SESSIONS[me.id] = entry
            CLIENT_TO_SESSION[id(new_client)] = entry

            await status.edit_text(
                f"✅ Logged in as <b>{me.first_name}</b> (@{me.username or 'N/A'})\n"
                f"ID: <code>{me.id}</code>\n\n"
                "All commands are now available from this account."
            )
        except Exception as e:
            await status.edit_text(f"❌ Login failed: `{type(e).__name__}: {e}`")
        return

    # Guided flow
    LOGIN_STATES[user_id] = {"step": "phone"}
    await message.reply_text(
        "📱 Send your phone number with country code.\n"
        "Example: <code>+919876543210</code>\n\n"
        "Send <code>.cancellogin</code> anytime to abort."
    )


@bot.on_message(filters.command(["cancellogin"], prefixes=PREFIXES) & filters.private)
@sudo_only
async def cancellogin_cmd(client, message: Message):
    user_id = message.from_user.id
    state = LOGIN_STATES.pop(user_id, None)
    if state and state.get("temp_client"):
        try:
            await state["temp_client"].disconnect()
        except Exception:
            pass
    await message.reply_text("✅ Login cancelled.")


@bot.on_message(filters.private & filters.text & ~filters.command(["login", "cancellogin", "logout", "mylogin"], prefixes=PREFIXES))
async def login_flow_handler(client, message: Message):
    user_id = message.from_user.id
    state = LOGIN_STATES.get(user_id)
    if not state:
        return

    step = state.get("step")

    if step == "phone":
        phone = message.text.strip()
        try:
            temp = Client(
                name=f"temp_{user_id}",
                api_id=API_ID,
                api_hash=API_HASH,
                in_memory=True,
            )
            await temp.connect()
            sent = await temp.send_code(phone)
            state["temp_client"] = temp
            state["phone"] = phone
            state["phone_code_hash"] = sent.phone_code_hash
            state["step"] = "code"
            await message.reply_text(
                "✅ Code sent! Now send the login code you received.\n"
                "(Check Telegram app / SMS)"
            )
        except PhoneNumberInvalid:
            await message.reply_text("❌ Invalid phone number. Try again.")
        except FloodWait as e:
            await message.reply_text(f"⏳ FloodWait: try again after {e.value}s")
            LOGIN_STATES.pop(user_id, None)
        except Exception as e:
            await message.reply_text(f"❌ Error: `{e}`")
            LOGIN_STATES.pop(user_id, None)

    elif step == "code":
        code = message.text.strip().replace(" ", "")
        temp = state["temp_client"]
        try:
            await temp.sign_in(state["phone"], state["phone_code_hash"], code)
            # Success without 2FA
            await _finalize_login(temp, user_id, message)
        except SessionPasswordNeeded:
            state["step"] = "password"
            await message.reply_text("🔐 2FA enabled. Send your cloud password:")
        except (PhoneCodeInvalid, PhoneCodeExpired) as e:
            await message.reply_text(f"❌ Invalid/expired code. Start over with `.login`")
            LOGIN_STATES.pop(user_id, None)
            try:
                await temp.disconnect()
            except Exception:
                pass
        except Exception as e:
            await message.reply_text(f"❌ Error: `{e}`")
            LOGIN_STATES.pop(user_id, None)

    elif step == "password":
        password = message.text.strip()
        temp = state["temp_client"]
        try:
            await temp.check_password(password)
            await _finalize_login(temp, user_id, message)
        except PasswordHashInvalid:
            await message.reply_text("❌ Wrong password. Try again or `.cancellogin`")
        except Exception as e:
            await message.reply_text(f"❌ Error: `{e}`")
            LOGIN_STATES.pop(user_id, None)


async def _finalize_login(temp_client, requester_id, message):
    try:
        me = await temp_client.get_me()
        await register_common_handlers(temp_client)
        try:
            await ensure_started(temp_client)
        except Exception:
            pass

        entry = {
            "client": temp_client,
            "user_id": me.id,
            "username": me.username,
            "added_by": requester_id,
            "name": me.first_name,
        }
        ACTIVE_SESSIONS[me.id] = entry
        CLIENT_TO_SESSION[id(temp_client)] = entry
        LOGIN_STATES.pop(requester_id, None)

        await message.reply_text(
            f"✅ Logged in as <b>{me.first_name}</b> (@{me.username or 'N/A'})\n"
            f"ID: <code>{me.id}</code>\n\n"
            "All commands are now available from this account."
        )
    except Exception as e:
        await message.reply_text(f"❌ Finalize failed: `{e}`")
        LOGIN_STATES.pop(requester_id, None)


@bot.on_message(filters.command(["logout"], prefixes=PREFIXES) & filters.private)
@sudo_only
async def logout_cmd(client, message: Message):
    requester = message.from_user.id
    if len(message.command) > 1:
        try:
            target_id = int(message.command[1])
        except ValueError:
            return await message.reply_text("Invalid user ID.")
    else:
        # Logout all sessions owned by this requester (or all if owner)
        to_remove = []
        for uid, entry in list(ACTIVE_SESSIONS.items()):
            if _can_manage(entry, requester):
                to_remove.append(uid)
        if not to_remove:
            return await message.reply_text("No active sessions to logout.")
        for uid in to_remove:
            entry = ACTIVE_SESSIONS.pop(uid)
            try:
                await entry["client"].stop()
            except Exception:
                pass
            CLIENT_TO_SESSION.pop(id(entry["client"]), None)
        return await message.reply_text(f"✅ Logged out {len(to_remove)} session(s).")

    entry = ACTIVE_SESSIONS.get(target_id)
    if not entry:
        return await message.reply_text("No active session with that ID.")
    if not _can_manage(entry, requester):
        return await message.reply_text("You can only logout sessions you added.")
    ACTIVE_SESSIONS.pop(target_id)
    try:
        await entry["client"].stop()
    except Exception:
        pass
    CLIENT_TO_SESSION.pop(id(entry["client"]), None)
    await message.reply_text(f"✅ Logged out `{target_id}`")


@bot.on_message(filters.command(["mylogin", "sessions"], prefixes=PREFIXES) & filters.private)
@sudo_only
async def mylogin_cmd(client, message: Message):
    requester = message.from_user.id
    lines = []
    for uid, entry in ACTIVE_SESSIONS.items():
        if _can_manage(entry, requester):
            lines.append(
                f"• <b>{entry.get('name', '?')}</b> (@{entry.get('username') or 'N/A'}) "
                f"— <code>{uid}</code>"
            )
    if not lines:
        return await message.reply_text("No active sessions.")
    await message.reply_text("<b>Active Sessions</b>\n\n" + "\n".join(lines))
