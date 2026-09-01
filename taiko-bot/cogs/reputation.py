import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from sqlalchemy.future import select
from database.manager import get_session
from database.models import Economy
from utils.helpers import create_embed, success_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR

class ReputationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._cooldowns: dict[str, datetime] = {}

    @commands.hybrid_command(name="rep", description="Give reputation to a user")
    async def rep(self, ctx: commands.Context, member: discord.Member):
        if member.bot or member == ctx.author:
            await ctx.send(embed=error_embed("You cannot give reputation to bots or yourself."))
            return
        key = f"{ctx.guild.id}:{ctx.author.id}:{member.id}"
        now = datetime.utcnow()
        if key in self._cooldowns and (now - self._cooldowns[key]).total_seconds() < 86400:
            remaining = 86400 - (now - self._cooldowns[key]).total_seconds()
            await ctx.send(embed=error_embed(f"You can give reputation again in {int(remaining // 3600)}h {(int(remaining % 3600) // 60)}m"))
            return
        async with get_session() as session:
            economy = await session.execute(select(Economy).where(Economy.user_id == member.id, Economy.guild_id == ctx.guild.id))
            economy = economy.scalar_one_or_none()
            if not economy:
                economy = Economy(user_id=member.id, guild_id=ctx.guild.id)
                session.add(economy)
                await session.commit()
                await session.refresh(economy)
            economy.balance += 1
            session.add(economy)
            await session.commit()
        self._cooldowns[key] = now
        await ctx.send(embed=success_embed(f"You gave {member.mention} +1 reputation!"))

    @commands.hybrid_command(name="repleaderboard", description="View the reputation leaderboard")
    async def rep_leaderboard(self, ctx: commands.Context):
        async with get_session() as session:
            result = await session.execute(
                select(Economy).where(Economy.guild_id == ctx.guild.id).order_by(Economy.balance.desc()).limit(10)
            )
            entries = result.scalars().all()
        if not entries:
            await ctx.send(embed=create_embed(description="No reputation data yet."))
            return
        embed = create_embed(title="Reputation Leaderboard", color=EMBED_COLOR)
        for i, entry in enumerate(entries, 1):
            user = self.bot.get_user(entry.user_id) or await self.bot.fetch_user(entry.user_id)
            embed.add_field(name=f"#{i} {user}", value=f"{entry.balance:,} rep", inline=False)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ReputationCog(bot))
