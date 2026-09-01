import discord
from discord.ext import commands
from datetime import datetime, timedelta
from utils.helpers import create_embed, error_embed
from utils.config import ERROR_COLOR, EMBED_COLOR

BAD_WORDS = ["badword", "scam", "phishing"]

class AutoModCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._spam_tracker: dict[int, dict[int, list[float]]] = {}
        self._raid_tracker: dict[int, list[float]] = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        await self._check_spam(message)
        await self._check_bad_words(message)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self._check_raid(member)

    async def _check_spam(self, message: discord.Message):
        guild_id = message.guild.id
        user_id = message.author.id
        now = datetime.utcnow().timestamp()
        if guild_id not in self._spam_tracker:
            self._spam_tracker[guild_id] = {}
        if user_id not in self._spam_tracker[guild_id]:
            self._spam_tracker[guild_id][user_id] = []
        self._spam_tracker[guild_id][user_id].append(now)
        cutoff = now - 5
        self._spam_tracker[guild_id][user_id] = [t for t in self._spam_tracker[guild_id][user_id] if t > cutoff]
        if len(self._spam_tracker[guild_id][user_id]) > 5:
            try:
                await message.author.timeout(discord.utils.utcnow() + timedelta(minutes=1), reason="Anti-spam")
                await message.channel.send(f"⛔ {message.author.mention} has been timed out for spamming.", delete_after=10)
            except Exception:
                pass
            self._spam_tracker[guild_id][user_id] = []

    async def _check_raid(self, member: discord.Member):
        guild_id = member.guild.id
        now = datetime.utcnow().timestamp()
        if guild_id not in self._raid_tracker:
            self._raid_tracker[guild_id] = []
        self._raid_tracker[guild_id].append(now)
        cutoff = now - 10
        self._raid_tracker[guild_id] = [t for t in self._raid_tracker[guild_id] if t > cutoff]
        if len(self._raid_tracker[guild_id]) > 10:
            channel = discord.utils.get(member.guild.text_channels, name="alerts")
            if channel:
                embed = create_embed(
                    title="Raid Alert",
                    description=f"Detected {len(self._raid_tracker[guild_id])} joins in 10 seconds!",
                    color=ERROR_COLOR
                )
                try:
                    await channel.send(embed=embed)
                except Exception:
                    pass

    async def _check_bad_words(self, message: discord.Message):
        content = message.content.lower()
        for word in BAD_WORDS:
            if word in content:
                try:
                    await message.delete()
                    await message.channel.send(f"⛔ {message.author.mention}, that word is not allowed here.", delete_after=5)
                except Exception:
                    pass
                break

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoModCog(bot))
