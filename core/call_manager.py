"""
Per-client PyTgCalls management — every account has its OWN VC engine.

Features:
- Auto play next song when current ends
- Auto leave VC when queue is empty
- Notify in group when someone joins VC (full user info)
- Notify in group when someone leaves VC (full user info)
"""

from pytgcalls import PyTgCalls
from pytgcalls import filters as fl
from pytgcalls.types import (
    MediaStream,
    AudioQuality,
    VideoQuality,
    StreamEnded,
    GroupCallParticipant,
    UpdatedGroupCallParticipants,
)
from pyrogram import Client
from pyrogram.types import Message
import asyncio
from typing import Dict, List, Optional

# client_id -> PyTgCalls instance
_engines: Dict[int, PyTgCalls] = {}
# client_id -> {chat_id: queue list}
_queues: Dict[int, Dict[int, List[dict]]] = {}
# client_id -> {chat_id: current track info}
_current: Dict[int, Dict[int, dict]] = {}


def get_engine(client: Client) -> PyTgCalls:
    cid = id(client)
    if cid not in _engines:
        _engines[cid] = PyTgCalls(client)
        _queues[cid] = {}
        _current[cid] = {}
    return _engines[cid]


def get_queue(client: Client, chat_id: int) -> List[dict]:
    cid = id(client)
    if cid not in _queues:
        _queues[cid] = {}
    return _queues[cid].setdefault(chat_id, [])


def get_current(client: Client) -> Dict[int, dict]:
    cid = id(client)
    if cid not in _current:
        _current[cid] = {}
    return _current[cid]


async def ensure_started(client: Client):
    engine = get_engine(client)
    try:
        await engine.start()
    except Exception:
        pass  # already started or will lazy-start


async def play_track(client: Client, chat_id: int, track: dict, video: bool = False):
    """Play a single track. track = {title, url, duration, ...}"""
    engine = get_engine(client)
    await ensure_started(client)

    stream = MediaStream(
        track["url"],
        audio_parameters=AudioQuality.HIGH,
        video_parameters=VideoQuality.HD_720p if video else None,
    )

    current = get_current(client)
    current[chat_id] = track

    try:
        await engine.play(chat_id, stream)
    except Exception as e:
        current.pop(chat_id, None)
        raise e


async def skip_track(client: Client, chat_id: int):
    queue = get_queue(client, chat_id)
    current = get_current(client)
    engine = get_engine(client)

    if queue:
        next_track = queue.pop(0)
        video = next_track.get("video", False)
        await play_track(client, chat_id, next_track, video=video)
        return next_track
    else:
        current.pop(chat_id, None)
        try:
            await engine.leave_call(chat_id)
        except Exception:
            pass
        return None


async def stop_all(client: Client, chat_id: int):
    queue = get_queue(client, chat_id)
    queue.clear()
    current = get_current(client)
    current.pop(chat_id, None)
    engine = get_engine(client)
    try:
        await engine.leave_call(chat_id)
    except Exception:
        pass
