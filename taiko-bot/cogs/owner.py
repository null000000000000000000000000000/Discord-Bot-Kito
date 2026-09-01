import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import create_embed, success_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR, OWNER_IDS, MAINTENANCE_MODE
from utils.permissions import is_owner
from utils.logger import logger
import time

class OwnerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._start_time = time.time()

    @commands.hybrid_command(name="eval", description="Evaluate code (owner only)")
    @is_owner()
    async def eval_command(self, ctx: commands.Context, *, code: str):
        try:
            result = eval(code, {"bot": self.bot, "ctx": ctx, "discord": discord})
            await ctx.send(f"```py\n{result}```")
        except Exception as e:
            await ctx.send(f"```py\n{e}```")

    @commands.hybrid_command(name="botstats", description="View bot statistics")
    @is_owner()
    async def bot_stats(self, ctx: commands.Context):
        uptime = time.time() - self._start_time
        days = int(uptime // 86400)
        hours = int((uptime % 86400) // 3600)
        minutes = int((uptime % 3600) // 60)
        embed = create_embed(title="Bot Statistics", color=EMBED_COLOR)
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Users", value=str(len(self.bot.users)), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Uptime", value=f"{days}d {hours}h {minutes}m", inline=True)
        embed.add_field(name="Maintenance", value="Yes" if MAINTENANCE_MODE else "No", inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="reload", description="Reload a cog")
    @is_owner()
    async def reload_cog(self, ctx: commands.Context, cog: str):
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await ctx.send(embed=success_embed(f"Reloaded cog: {cog}"))
        except Exception as e:
            await ctx.send(embed=error_embed(f"Failed to reload: {e}"))

    @commands.hybrid_command(name="maintenance", description="Toggle maintenance mode")
    @is_owner()
    async def toggle_maintenance(self, ctx: commands.Context, mode: bool):
        from utils.config import MAINTENANCE_MODE as CURRENT_MAINT
        # Note: in production, persist to DB/config
        await ctx.send(embed=success_embed(f"Maintenance mode set to: {mode}"))

    @commands.hybrid_command(name="announce", description="Send a global announcement")
    @is_owner()
    async def announce(self, ctx: commands.Context, *, message: str):
        embed = create_embed(title="📢 Announcement", description=message, color=EMBED_COLOR)
        count = 0
        for guild in self.bot.guilds:
            channel = guild.system_channel or guild.text_channels[0] if guild.text_channels else None
            if channel:
                try:
                    await channel.send(embed=embed)
                    count += 1
                except Exception:
                    pass
        await ctx.send(embed=success_embed(f"Announcement sent to {count} servers."))

    @commands.hybrid_command(name="emergency", description="Emergency bot shutdown")
    @is_owner()
    async def emergency_stop(self, ctx: commands.Context):
        await ctx.send(embed=success_embed("Emergency shutdown initiated."))
        logger.critical("Emergency shutdown triggered by owner")
        await self.bot.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(OwnerCog(bot))
