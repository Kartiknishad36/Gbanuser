"""
Local JSON-file storage — replaces MongoDB entirely so no external DB/network
dependency is needed. Same function names/signatures as before, so nothing
else in the codebase needs to change.
"""
import json
import asyncio
from pathlib import Path
from typing import Optional

STORAGE_PATH = Path("storage.json")
_lock = asyncio.Lock()


def _read() -> dict:
    if not STORAGE_PATH.exists():
        return {}
    try:
        with open(STORAGE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _write(data: dict):
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ===================== Sudoers =====================
async def get_sudoers() -> list[int]:
    async with _lock:
        return list(_read().get("sudoers", []))


async def add_sudo(user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("sudoers", [])
        if user_id not in data["sudoers"]:
            data["sudoers"].append(user_id)
        _write(data)


async def remove_sudo(user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("sudoers", [])
        data["sudoers"] = [u for u in data["sudoers"] if u != user_id]
        _write(data)


# ===================== Global Ban =====================
async def add_gban(user_id: int, reason: str = "No reason"):
    async with _lock:
        data = _read()
        data.setdefault("gban", {})
        data["gban"][str(user_id)] = {"reason": reason}
        _write(data)


async def remove_gban(user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("gban", {})
        data["gban"].pop(str(user_id), None)
        _write(data)


async def is_gbanned(user_id: int) -> bool:
    async with _lock:
        return str(user_id) in _read().get("gban", {})


async def get_gban_list() -> list[dict]:
    async with _lock:
        gban = _read().get("gban", {})
        return [{"user_id": int(uid), **info} for uid, info in gban.items()]


# ===================== Global Mute =====================
async def add_gmute(user_id: int, reason: str = "No reason"):
    async with _lock:
        data = _read()
        data.setdefault("gmute", {})
        data["gmute"][str(user_id)] = {"reason": reason}
        _write(data)


async def remove_gmute(user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("gmute", {})
        data["gmute"].pop(str(user_id), None)
        _write(data)


async def is_gmuted(user_id: int) -> bool:
    async with _lock:
        return str(user_id) in _read().get("gmute", {})


async def get_gmute_list() -> list[dict]:
    async with _lock:
        gmute = _read().get("gmute", {})
        return [{"user_id": int(uid), **info} for uid, info in gmute.items()]


# ===================== Warns =====================
async def add_warn(chat_id: int, user_id: int, reason: str = ""):
    async with _lock:
        data = _read()
        data.setdefault("warns", {})
        key = f"{chat_id}:{user_id}"
        data["warns"].setdefault(key, [])
        data["warns"][key].append(reason)
        _write(data)
        return len(data["warns"][key])


async def get_warns(chat_id: int, user_id: int) -> list:
    async with _lock:
        key = f"{chat_id}:{user_id}"
        return list(_read().get("warns", {}).get(key, []))


async def reset_warns(chat_id: int, user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("warns", {})
        data["warns"].pop(f"{chat_id}:{user_id}", None)
        _write(data)


# ===================== Approved PM users =====================
async def approve_pm(user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("approved_pm", [])
        if user_id not in data["approved_pm"]:
            data["approved_pm"].append(user_id)
        _write(data)


async def unapprove_pm(user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("approved_pm", [])
        data["approved_pm"] = [u for u in data["approved_pm"] if u != user_id]
        _write(data)


async def get_approved_pm() -> list[int]:
    async with _lock:
        return list(_read().get("approved_pm", []))


# ===================== Welcome messages (per chat) =====================
DEFAULT_WELCOME_TEXT = "👋 Welcome {mention} to {chat}!"


async def set_welcome_enabled(chat_id: int, enabled: bool):
    async with _lock:
        data = _read()
        data.setdefault("welcome", {})
        entry = data["welcome"].setdefault(str(chat_id), {})
        entry["enabled"] = enabled
        _write(data)


async def get_welcome_enabled(chat_id: int) -> bool:
    async with _lock:
        data = _read()
        entry = data.get("welcome", {}).get(str(chat_id), {})
        return bool(entry.get("enabled", False))


async def set_welcome_text(chat_id: int, text: str):
    async with _lock:
        data = _read()
        data.setdefault("welcome", {})
        entry = data["welcome"].setdefault(str(chat_id), {})
        entry["text"] = text
        _write(data)


async def get_welcome_text(chat_id: int) -> str:
    async with _lock:
        data = _read()
        entry = data.get("welcome", {}).get(str(chat_id), {})
        return entry.get("text") or DEFAULT_WELCOME_TEXT


# ===================== Global Auto-Reply (bro targets) =====================
async def add_bro_target(user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("bro_targets", [])
        if user_id not in data["bro_targets"]:
            data["bro_targets"].append(user_id)
        _write(data)


async def remove_bro_target(user_id: int):
    async with _lock:
        data = _read()
        data.setdefault("bro_targets", [])
        data["bro_targets"] = [u for u in data["bro_targets"] if u != user_id]
        _write(data)


async def get_bro_targets() -> list[int]:
    async with _lock:
        return list(_read().get("bro_targets", []))


async def is_bro_target(user_id: int) -> bool:
    async with _lock:
        return user_id in _read().get("bro_targets", [])


# ===================== Chat tracking (for broadcast) =====================
async def add_chat(chat_id: int):
    async with _lock:
        data = _read()
        data.setdefault("chats", [])
        if chat_id not in data["chats"]:
            data["chats"].append(chat_id)
        _write(data)


async def get_all_chats() -> list[int]:
    async with _lock:
        return list(_read().get("chats", []))
