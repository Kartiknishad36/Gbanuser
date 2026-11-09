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
    UpdatedGroupCallParticipant,
)

from core.clients import app, assistant

_INSTANCES: dict[int, PyTgCalls] = {}
_STARTED: dict[int, bool] = {}
_QUEUES: dict[int, dict[int, list[dict]]] = {}
_CURRENT: dict[int, dict[int, dict]] = {}


def _resolve_call_client(client):
    if client is app and assistant is not None:
        return assistant
    return client


def get_pytgcalls(client) -> PyTgCalls:
    call_client = _resolve_call_client(client)
    key = id(call_client)
    if key not in _INSTANCES:
        pytg = PyTgCalls(call_client)
        _INSTANCES[key] = pytg
        _register_handlers(pytg, client)
    return _INSTANCES[key]


def get_queue(client, chat_id: int) -> list:
    key = id(_resolve_call_client(client))
    if key not in _QUEUES:
        _QUEUES[key] = {}
    return _QUEUES[key].setdefault(chat_id, [])


def get_current(client) -> dict:
    key = id(_resolve_call_client(client))
    if key not in _CURRENT:
        _CURRENT[key] = {}
    return _CURRENT[key]


async def ensure_started(client):
    pytg = get_pytgcalls(client)
    key = id(_resolve_call_client(client))
    if not _STARTED.get(key):
        try:
            await pytg.start()
            _STARTED[key] = True
        except Exception:
            pass


async def play_track(client, chat_id: int, track: dict, video: bool = False):
    pytg = get_pytgcalls(client)
    await ensure_started(client)
    stream = MediaStream(
        track["url"],
        audio_parameters=AudioQuality.HIGH,
        video_parameters=VideoQuality.HD_720p if video else None,
    )
    current = get_current(client)
    current[chat_id] = track
    await pytg.play(chat_id, stream)


async def skip_track(client, chat_id: int):
    queue = get_queue(client, chat_id)
    current = get_current(client)
    pytg = get_pytgcalls(client)
    if queue:
        next_track = queue.pop(0)
        video = next_track.get("video", False)
        await play_track(client, chat_id, next_track, video=video)
        return next_track
    else:
        current.pop(chat_id, None)
        try:
            await pytg.leave_call(chat_id)
        except Exception:
            pass
        return None


async def stop_all(client, chat_id: int):
    queue = get_queue(client, chat_id)
    queue.clear()
    current = get_current(client)
    current.pop(chat_id, None)
    pytg = get_pytgcalls(client)
    try:
        await pytg.leave_call(chat_id)
    except Exception:
        pass


def _register_handlers(pytg: PyTgCalls, client):
    @pytg.on_update(fl.stream_end)
    async def on_stream_end(_, update: StreamEnded):
        chat_id = update.chat_id
        queue = get_queue(client, chat_id)
        if queue:
            next_track = queue.pop(0)
            video = next_track.get("video", False)
            try:
                await play_track(client, chat_id, next_track, video=video)
            except Exception:
                pass
        else:
            current = get_current(client)
            current.pop(chat_id, None)
            try:
                await pytg.leave_call(chat_id)
            except Exception:
                pass
