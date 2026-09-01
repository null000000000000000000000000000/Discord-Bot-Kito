import discord
from discord.ext import commands
from utils.errors import PermissionError
from utils.config import OWNER_IDS

def is_owner():
    async def predicate(ctx: commands.Context):
        if ctx.author.id not in OWNER_IDS:
            raise PermissionError("This command can only be used by the bot owner.")
        return True
    return commands.check(predicate)

def has_permissions(**perms):
    async def predicate(ctx: commands.Context):
        if isinstance(ctx.channel, discord.DMChannel):
            return True
        missing = [p for p, v in perms.items() if not getattr(ctx.author.guild_permissions, p, False)]
        if missing:
            raise PermissionError(f"Missing permissions: {', '.join(missing)}")
        return True
    return commands.check(predicate)

def bot_has_permissions(**perms):
    async def predicate(ctx: commands.Context):
        if isinstance(ctx.channel, discord.DMChannel):
            return True
        missing = [p for p, v in perms.items() if not getattr(ctx.guild.me.guild_permissions, p, False)]
        if missing:
            raise PermissionError(f"Bot is missing permissions: {', '.join(missing)}")
        return True
    return commands.check(predicate)
