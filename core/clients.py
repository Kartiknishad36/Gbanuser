from pyrogram import Client
from config import (
    API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, ASSISTANT_SESSION, BOT_NAME
)

# Main userbot account (STRING_SESSION required)
app = Client(
    name="main",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION,
    in_memory=True,
)

# Optional companion bot (BOT_TOKEN) — powers the public .login / .start flow
bot = None
if BOT_TOKEN:
    bot = Client(
        name="bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        in_memory=True,
    )

# Optional dedicated assistant for VC (keeps main account free)
assistant = None
if ASSISTANT_SESSION:
    assistant = Client(
        name="assistant",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=ASSISTANT_SESSION,
        in_memory=True,
    )
