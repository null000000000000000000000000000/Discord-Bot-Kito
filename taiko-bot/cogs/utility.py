import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import create_embed, success_embed, error_embed, format_time
from utils.errors import MaintenanceError
from utils.config import MAINTENANCE_MODE, EMBED_COLOR, OWNER_IDS

class UtilityCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Check bot latency")
    async def ping(self, ctx: commands.Context):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency: `{latency}ms`")

    @commands.hybrid_command(name="pong", description="Check bot latency")
    async def pong(self, ctx: commands.Context):
        await self.ping(ctx)

    @app_commands.command(name="info", description="Get bot information")
    async def info(self, interaction: discord.Interaction):
        embed = create_embed(
            title="TAIKO Bot",
            description="A modular Discord bot built with discord.py",
            color=EMBED_COLOR
        )
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Users", value=str(len(self.bot.users)), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.set_footer(text="TAIKO Bot v1.0")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="uptime", description="Check bot uptime")
    async def uptime(self, interaction: discord.Interaction):
        delta = discord.utils.utcnow() - self.bot.start_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        await interaction.response.send_message(
            f"⏰ Uptime: `{days}d {hours}h {minutes}m {seconds}s`"
        )

    @commands.hybrid_command(name="help", description="Show help menu")
    async def help(self, ctx: commands.Context):
        embed = create_embed(title="Help", description="Use `/help` for slash command help")
        embed.add_field(name="Moderation", value="`/ban`, `/kick`, `/mute`, `/purge`", inline=False)
        embed.add_field(name="Utility", value="`/ping`, `/info`, `/serverinfo`", inline=False)
        embed.add_field(name="Economy", value="`/balance`, `/daily`, `/work`", inline=False)
        embed.add_field(name="Leveling", value="`/rank`, `/leaderboard`", inline=False)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(UtilityCog(bot))
