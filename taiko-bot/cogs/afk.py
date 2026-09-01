import discord
from discord.ext import commands
from utils.helpers import create_embed, success_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR

class AFKCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._afk_users: dict[int, dict] = {}

    @commands.hybrid_command(name="afk", description="Set yourself as AFK")
    async def afk(self, ctx: commands.Context, *, reason: str | None = None):
        self._afk_users[ctx.author.id] = {
            "reason": reason or "AFK",
            "guild_id": ctx.guild.id,
            "timestamp": discord.utils.utcnow(),
        }
        await ctx.send(embed=success_embed(f"You are now AFK: {reason or 'No reason provided'}"))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        afk_data = self._afk_users.pop(message.author.id, None)
        if afk_data and afk_data["guild_id"] == message.guild.id:
            await message.channel.send(embed=success_embed(f"Welcome back, {message.author.mention}! I removed your AFK status."))
            return
        for mention in message.mentions:
            afk = self._afk_users.get(mention.id)
            if afk and afk["guild_id"] == message.guild.id:
                embed = create_embed(title=f"💤 {mention.display_name} is AFK", description=afk["reason"], color=EMBED_COLOR)
                embed.set_footer(text=f"AFK since: {discord.utils.format_dt(afk['timestamp'], style='R')}")
                await message.channel.send(embed=embed)
                break

async def setup(bot: commands.Bot):
    await bot.add_cog(AFKCog(bot))
