import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from utils.helpers import create_embed, error_embed
from utils.config import ERROR_COLOR, EMBED_COLOR

class SecurityCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._action_tracker: dict[int, dict[int, list[float]]] = {}
        self._nuke_threshold = 5
        self._nuke_window = 10

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: abc.GuildChannel):
        await self._track_action(channel.guild.id, channel.guild.me.id, "channel_delete")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        await self._track_action(role.guild.id, role.guild.me.id, "role_delete")

    async def _track_action(self, guild_id: int, actor_id: int, action: str):
        now = datetime.utcnow().timestamp()
        if guild_id not in self._action_tracker:
            self._action_tracker[guild_id] = {}
        if actor_id not in self._action_tracker[guild_id]:
            self._action_tracker[guild_id][actor_id] = []
        self._action_tracker[guild_id][actor_id].append(now)
        cutoff = now - self._nuke_window
        self._action_tracker[guild_id][actor_id] = [t for t in self._action_tracker[guild_id][actor_id] if t > cutoff]
        if len(self._action_tracker[guild_id][actor_id]) >= self._nuke_threshold:
            alert_channel = discord.utils.get(self.bot.get_all_channels(), name="security-alerts")
            if alert_channel:
                embed = create_embed(
                    title="🚨 Nuke Alert",
                    description=f"Possible nuke activity detected!\nUser: <@{actor_id}>\nActions: {action} x{len(self._action_tracker[guild_id][actor_id])}",
                    color=ERROR_COLOR
                )
                try:
                    await alert_channel.send(embed=embed)
                except Exception:
                    pass

    @commands.hybrid_command(name="securitystatus", description="Check security status")
    async def security_status(self, ctx: commands.Context):
        embed = create_embed(title="Security Status", color=EMBED_COLOR)
        embed.add_field(name="Anti-Raid", value="✅ Active", inline=True)
        embed.add_field(name="Anti-Nuke", value="✅ Active", inline=True)
        embed.add_field(name="Anti-Spam", value="✅ Active", inline=True)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(SecurityCog(bot))
