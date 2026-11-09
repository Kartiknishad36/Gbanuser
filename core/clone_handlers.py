"""
Registers the shared command handlers on any newly created Client
(clones or self-service logins).
"""
from pyrogram import Client


async def register_common_handlers(client: Client):
    """Import and attach every public/global/owner/utils/vc handler to `client`."""
    import modules.global_mod
    import modules.owner
    import modules.public
    import modules.utils
    import modules.vc
