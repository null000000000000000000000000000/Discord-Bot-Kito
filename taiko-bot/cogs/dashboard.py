import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import create_embed, success_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR
from utils.permissions import has_permissions

class DashboardCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="dashboard", description="Open server dashboard")
    @has_permissions(administrator=True)
    async def dashboard(self, ctx: commands.Context):
        embed = create_embed(
            title="Server Dashboard",
            description="Configure your server settings below.",
            color=EMBED_COLOR
        )
        embed.add_field(name="Moderation", value="`/setlogchannel`, `/setmuterole`", inline=False)
        embed.add_field(name="Welcome", value="`/setwelcome`, `/setgoodbye`, `/setautorole`", inline=False)
        embed.add_field(name="Economy", value="`/setcurrency`, `/setdailylimit`", inline=False)
        embed.add_field(name="Leveling", value="`/setxprate`, `/setlevelchannel`", inline=False)
        embed.add_field(name="Tickets", value="`/panel`", inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="setlogchannel", description="Set the moderation log channel")
    @has_permissions(administrator=True)
    async def set_log_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        await ctx.send(embed=success_embed(f"Mod log channel set to {channel.mention}"))

    @commands.hybrid_command(name="setmuterole", description="Set the mute role")
    @has_permissions(administrator=True)
    async def set_mute_role(self, ctx: commands.Context, role: discord.Role):
        await ctx.send(embed=success_embed(f"Mute role set to {role.mention}"))

    @commands.hybrid_command(name="setcurrency", description="Set the server currency name")
    @has_permissions(administrator=True)
    async def set_currency(self, ctx: commands.Context, name: str):
        await ctx.send(embed=success_embed(f"Currency name set to **{name}**"))

    @commands.hybrid_command(name="setxprate", description="Set the XP multiplier")
    @has_permissions(administrator=True)
    async def set_xp_rate(self, ctx: commands.Context, rate: float):
        if rate < 0.1 or rate > 10:
            await ctx.send(embed=error_embed("XP rate must be between 0.1 and 10."))
            return
        await ctx.send(embed=success_embed(f"XP multiplier set to **{rate}x**"))

async def setup(bot: commands.Bot):
    await bot.add_cog(DashboardCog(bot))
