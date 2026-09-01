import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy.future import select
from database.manager import get_session
from database.models import Leveling
from utils.helpers import create_embed, success_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR
from datetime import datetime, timedelta

class LevelingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._cooldowns: dict[str, datetime] = {}

    async def _get_leveling(self, user_id: int, guild_id: int) -> Leveling:
        async with get_session() as session:
            result = await session.execute(select(Leveling).where(Leveling.user_id == user_id, Leveling.guild_id == guild_id))
            leveling = result.scalar_one_or_none()
            if not leveling:
                leveling = Leveling(user_id=user_id, guild_id=guild_id)
                session.add(leveling)
                await session.commit()
                await session.refresh(leveling)
            return leveling

    async def _add_xp(self, member: discord.Member, amount: int):
        if member.bot:
            return
        guild_id = member.guild.id
        user_id = member.id
        key = f"{guild_id}:{user_id}"
        now = datetime.utcnow()
        if key in self._cooldowns and (now - self._cooldowns[key]).total_seconds() < 60:
            return
        self._cooldowns[key] = now
        leveling = await self._get_leveling(user_id, guild_id)
        old_level = leveling.level
        leveling.xp += int(amount * leveling.xp_multiplier)
        leveling.level = leveling.xp // 100 + 1
        leveling.last_xp_time = now
        async with get_session() as session:
            session.add(leveling)
            await session.commit()
            await session.refresh(leveling)
        if leveling.level > old_level:
            channel = member.guild.system_channel or discord.utils.get(member.guild.text_channels, name="general")
            if channel:
                embed = create_embed(
                    title="Level Up!",
                    description=f"Congratulations {member.mention}, you reached **Level {leveling.level}!**",
                    color=EMBED_COLOR
                )
                try:
                    await channel.send(embed=embed)
                except Exception:
                    pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        import random
        xp = random.randint(5, 15)
        await self._add_xp(message.author, xp)

    @commands.hybrid_command(name="rank", description="Check your rank")
    async def rank(self, ctx: commands.Context, member: discord.Member | None = None):
        target = member or ctx.author
        leveling = await self._get_leveling(target.id, ctx.guild.id)
        current_xp = leveling.xp
        level = leveling.level
        xp_for_next = level * 100
        xp_prev = (level - 1) * 100
        progress = current_xp - xp_prev
        needed = xp_for_next - xp_prev
        percent = min(100, int((progress / needed) * 100)) if needed > 0 else 100
        bar = "█" * (percent // 10) + "░" * (10 - (percent // 10))
        embed = create_embed(
            title=f"{target.display_name}'s Rank",
            color=EMBED_COLOR
        )
        embed.add_field(name="Level", value=str(level), inline=True)
        embed.add_field(name="XP", value=f"{current_xp:,} / {xp_for_next:,}", inline=True)
        embed.add_field(name="Progress", value=f"`{bar}` {percent}%", inline=False)
        embed.set_thumbnail(url=target.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="leaderboard", description="View the level leaderboard")
    async def leaderboard(self, ctx: commands.Context):
        async with get_session() as session:
            result = await session.execute(
                select(Leveling).where(Leveling.guild_id == ctx.guild.id).order_by(Leveling.xp.desc()).limit(10)
            )
            entries = result.scalars().all()
        if not entries:
            await ctx.send(embed=create_embed(description="No leveling data yet."))
            return
        embed = create_embed(title="Leaderboard", color=EMBED_COLOR)
        for i, entry in enumerate(entries, 1):
            user = self.bot.get_user(entry.user_id) or await self.bot.fetch_user(entry.user_id)
            embed.add_field(name=f"#{i} {user}", value=f"Level {entry.level} | {entry.xp:,} XP", inline=False)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(LevelingCog(bot))
