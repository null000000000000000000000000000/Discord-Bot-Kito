import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from utils.helpers import create_embed
from utils.config import EMBED_COLOR

class AnalyticsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._stats: dict[int, dict] = {}
        self._command_usage: dict[str, int] = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        guild_id = message.guild.id
        if guild_id not in self._stats:
            self._stats[guild_id] = {"messages": 0, "members_joined": 0, "members_left": 0}
        self._stats[guild_id]["messages"] += 1

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_id = member.guild.id
        if guild_id not in self._stats:
            self._stats[guild_id] = {"messages": 0, "members_joined": 0, "members_left": 0}
        self._stats[guild_id]["members_joined"] += 1

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild_id = member.guild.id
        if guild_id not in self._stats:
            self._stats[guild_id] = {"messages": 0, "members_joined": 0, "members_left": 0}
        self._stats[guild_id]["members_left"] += 1

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction, command: app_commands.Command):
        name = command.qualified_name
        self._command_usage[name] = self._command_usage.get(name, 0) + 1

    @commands.hybrid_command(name="stats", description="View server statistics")
    async def stats(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        stats = self._stats.get(guild_id, {"messages": 0, "members_joined": 0, "members_left": 0})
        embed = create_embed(title=f"{ctx.guild.name} Statistics", color=EMBED_COLOR)
        embed.add_field(name="Total Members", value=str(ctx.guild.member_count), inline=True)
        embed.add_field(name="Messages Tracked", value=f"{stats['messages']:,}", inline=True)
        embed.add_field(name="Members Joined", value=str(stats['members_joined']), inline=True)
        embed.add_field(name="Members Left", value=str(stats['members_left']), inline=True)
        embed.add_field(name="Channels", value=str(len(ctx.guild.channels)), inline=True)
        embed.add_field(name="Roles", value=str(len(ctx.guild.roles)), inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="commandstats", description="View command usage statistics")
    async def command_stats(self, ctx: commands.Context):
        if not self._command_usage:
            await ctx.send(embed=create_embed(description="No command usage data yet."))
            return
        sorted_usage = sorted(self._command_usage.items(), key=lambda x: x[1], reverse=True)[:10]
        embed = create_embed(title="Command Usage", color=EMBED_COLOR)
        for cmd, count in sorted_usage:
            embed.add_field(name=cmd, value=f"{count:,} uses", inline=False)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(AnalyticsCog(bot))
