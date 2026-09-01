import time
import discord
from discord.ext import commands
from utils.errors import CooldownError

class CooldownManager:
    def __init__(self):
        self._cooldowns: dict[str, float] = {}

    def get_cooldown(self, key: str) -> float:
        return self._cooldowns.get(key, 0.0)

    def set_cooldown(self, key: str, seconds: float):
        self._cooldowns[key] = time.time() + seconds

    def is_on_cooldown(self, key: str) -> tuple[bool, float]:
        expiry = self._cooldowns.get(key, 0.0)
        remaining = max(0.0, expiry - time.time())
        return remaining > 0, remaining

    def reset_cooldown(self, key: str):
        self._cooldowns.pop(key, None)

cooldown_manager = CooldownManager()

def cooldown(seconds: float = 1.0, key_format: str = "{user_id}:{command}"):
    async def predicate(ctx: commands.Context):
        key = key_format.format(user_id=ctx.author.id, command=ctx.command.qualified_name, guild_id=ctx.guild.id if ctx.guild else 0)
        on_cd, remaining = cooldown_manager.is_on_cooldown(key)
        if on_cd:
            raise CooldownError(f"You are on cooldown. Try again in {int(remaining)}s")
        cooldown_manager.set_cooldown(key, seconds)
        return True
    return commands.check(predicate)
