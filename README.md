# Userbot

Telegram userbot — moderation, self-service account cloning, and fun extras.
All commands are restricted to the owner and sudo users, except the
self-service `.login`/`.clone` flow, which is intentionally open to anyone
(PM-only, for safety).

## Features

- **Music/VC**: `.play`, `.vply`, `.cplay`, `.cvply` — play audio/video in a group's voice chat, with a per-chat queue. `.pause`/`.resume`/`.skip`/`.stop`, `.vmute`/`.vunmute`. Uses Pyrogram + PyTgCalls v2 and BabyAPI as the stream source. Every account (including clones/logins) gets its own independent VC engine.

- **Owner/Sudo system**: `.addsudo`, `.delsudo`, `.sudolist`

- **PM Guard**: warns and blocks strangers who spam PMs. `.approve` / `.unapprove` / `.approved`

- **Global moderation**: `.gban`, `.ungban`, `.gbanlist`, `.gmute`, `.gunmute`

- **Chat moderation**: `.ban`, `.unban`, `.kick`, `.mute`, `.unmute`, `.banall`, `.kickall`, `.muteall`, `.unmuteall`

- **Warn system**: `.warn`, `.unwarn`, `.warns`, `.resetwarns` (auto-ban after 3)

- **Broadcast**: `.broadcast <text>`

- **Tag all**: `.tagall [message]`, `.tagallstop`, `.tagme`

- **Shayari / Love**: `.sha` and `.love` (one-shot or recurring)

- **Welcome**: `.welcome on/off`, `.setwelcome <text>`

- **Self-service login**: `.login` with phone+OTP or string session

- **Clone**: `.clone <bot_token>` / `.unclone`

## Setup

1. Copy `.env.example` → `.env` and fill values
2. `pip install -r requirements.txt`
3. `python3 main.py`

**Required env:** `API_ID`, `API_HASH`, `STRING_SESSION`, `OWNER_ID`  
**Recommended:** `BOT_TOKEN`, `ASSISTANT_SESSION`, `API_KEY`

## Deployment

Supports Docker, Heroku (Procfile), and Nixpacks out of the box.

## Notes

- All sensitive commands are sudo/owner only.
- Self-service login is PM-only for safety.
- Original shayari/love lines included (no copyright issues).
