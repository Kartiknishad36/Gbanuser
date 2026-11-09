"""
Registers the shared command handlers on any newly created Client
(clones or self-service logins).
"""
from pyrogram import Client


async def register_common_handlers(client: Client):
    """Import and attach every public/global/owner/utils/vc handler to `client`."""
    # Importing the modules causes their @client.on_message decorators
    # (which are written against the main `app`) to re-bind against this
    # client when we explicitly re-register.  For simplicity we just
    # import the modules; the actual multi-client registration happens
    # inside each module by checking CLIENT_TO_SESSION / CLONES.
    import modules.global_mod
    import modules.owner
    import modules.public
    import modules.utils
    import modules.vc
