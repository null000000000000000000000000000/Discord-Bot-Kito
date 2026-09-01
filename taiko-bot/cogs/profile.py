import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy.future import select
from database.manager import get_session
from database.models import Economy, Leveling, Achievement
from utils.helpers import create_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR

class ProfileCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _get_user_data(self, user_id: int, guild_id: int):
        async with get_session() as session:
            economy = await session.execute(select(Economy).where(Economy.user_id == user_id, Economy.guild_id == guild_id))
            economy = economy.scalar_one_or_none()
            leveling = await session.execute(select(Leveling).where(Leveling.user_id == user_id, Leveling.guild_id == guild_id))
            leveling = leveling.scalar_one_or_none()
            achievements = await session.execute(select(Achievement).where(Achievement.user_id == user_id, Achievement.guild_id == guild_id))
            achievements = achievements.scalars().all()
        return economy, leveling, achievements

    @commands.hybrid_command(name="profile", description="View a user's profile")
    async def profile(self, ctx: commands.Context, member: discord.Member | None = None):
        target = member or ctx.author
        economy, leveling, achievements = await self._get_user_data(target.id, ctx.guild.id)
        embed = create_embed(
            title=f"{target.display_name}'s Profile",
            color=EMBED_COLOR
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        if economy:
            embed.add_field(name="💰 Wallet", value=f"{economy.balance:,} coins", inline=True)
            embed.add_field(name="🏦 Bank", value=f"{economy.bank:,} coins", inline=True)
        if leveling:
            embed.add_field(name="📊 Level", value=str(leveling.level), inline=True)
            embed.add_field(name="✨ XP", value=f"{leveling.xp:,}", inline=True)
        if achievements:
            badge_list = ", ".join([a.name for a in achievements[:5]])
            embed.add_field(name="🏆 Badges", value=badge_list or "None", inline=False)
        embed.set_footer(text=f"User ID: {target.id}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="rank", description="View your rank card")
    async def rank(self, ctx: commands.Context, member: discord.Member | None = None):
        target = member or ctx.author
        _, leveling, _ = await self._get_user_data(target.id, ctx.guild.id)
        if not leveling:
            await ctx.send(embed=error_embed("No leveling data for this user."))
            return
        current_xp = leveling.xp
        level = leveling.level
        xp_for_next = level * 100
        xp_prev = (level - 1) * 100
        progress = current_xp - xp_prev
        needed = xp_for_next - xp_prev
        percent = min(100, int((progress / needed) * 100)) if needed > 0 else 100
        bar = "█" * (percent // 10) + "░" * (10 - (percent // 10))
        embed = create_embed(
            title=f"{target.display_name}'s Rank Card",
            color=EMBED_COLOR
        )
        embed.add_field(name="Level", value=str(level), inline=True)
        embed.add_field(name="XP", value=f"{current_xp:,} / {xp_for_next:,}", inline=True)
        embed.add_field(name="Progress", value=f"`{bar}` {percent}%", inline=False)
        embed.set_thumbnail(url=target.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ProfileCog(bot))
