import asyncio
import importlib
import pkgutil

from core.clients import app, bot, assistant
from core.call_manager import ensure_started


async def load_modules():
    """Dynamically import every module under modules/ so their handlers register."""
    import modules

    for finder, name, ispkg in pkgutil.walk_packages(modules.__path__, modules.__name__ + "."):
        try:
            importlib.import_module(name)
            print(f"[Loader] Loaded {name}")
        except Exception as e:
            print(f"[Loader] Failed to load {name}: {e}")


async def main():
    print("[Bot] Starting...")

    await load_modules()

    await app.start()
    print("[Bot] Main userbot client started.")

    if bot:
        await bot.start()
        print("[Bot] Bot client started.")

    if assistant:
        await assistant.start()
        print("[Bot] Assistant client started.")

    # Eagerly start the main account's VC engine (lazy per-client startup
    # for clones/logins happens automatically on their first .play).
    await ensure_started(app)
    print("[Bot] PyTgCalls started.")

    print("[Bot] Bot is ready.")

    await asyncio.Event().wait()  # run forever


if __name__ == "__main__":
    # NOTE: We intentionally use get_event_loop() + run_until_complete() here
    # instead of asyncio.run(). Pyrogram clients are created at import time
    # (module level in core/clients.py) and grab whatever event loop exists
    # at that moment via get_event_loop(). asyncio.run() always creates a
    # brand-new loop, which would then differ from the one the clients
    # already grabbed -> "attached to a different loop" RuntimeError. Using
    # get_event_loop() here reuses that same loop.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
