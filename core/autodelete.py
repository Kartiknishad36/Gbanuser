"""
Small helper used by several modules to auto-delete bot replies after a short delay.
"""
import asyncio
from pyrogram.types import Message
from pyrogram.errors import RPCError


async def auto_delete(message: Message, delay: int = 8):
    """Delete `message` after `delay` seconds. Silently ignore failures."""
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except (RPCError, Exception):
        pass
