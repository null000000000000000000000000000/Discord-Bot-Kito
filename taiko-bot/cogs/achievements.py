import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from sqlalchemy.future import select
from database.manager import get_session
from database.models import Achievement
from utils.helpers import create_embed, success_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR

ACHIEVEMENTS = {
    "first_message": {"name": "First Message", "description": "Send your first message", "condition": lambda user, guild: True},
    "first_command": {"name": "First Command", "description": "Use your first command", "condition": lambda user, guild: True},
    "level_5": {"name": "Rising Star", "description": "Reach Level 5", "condition": lambda user, guild: False},
    "level_10": {"name": "Veteran", "description": "Reach Level 10", "condition": lambda user, guild: False},
}

class AchievementsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _grant_achievement(self, user_id: int, guild_id: int, key: str):
        async with get_session() as session:
            existing = await session.execute(select(Achievement).where(Achievement.user_id == user_id, Achievement.guild_id == guild_id, Achievement.name == key))
            if existing.scalar_one_or_none():
                return False
            ach = Achievement(user_id=user_id, guild_id=guild_id, name=key, description=ACHIEVEMENTS[key]["description"])
            session.add(ach)
            await session.commit()
        return True

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        if await self._grant_achievement(message.author.id, message.guild.id, "first_message"):
            try:
                await message.channel.send(f"🏆 {message.author.mention} unlocked achievement: **First Message**!")
            except Exception:
                pass

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction, command: app_commands.Command):
        if await self._grant_achievement(interaction.user.id, interaction.guild.id, "first_command"):
            try:
                await interaction.followup.send(f"🏆 {interaction.user.mention} unlocked achievement: **First Command**!", ephemeral=True)
            except Exception:
                pass

    @commands.hybrid_command(name="achievements", description="View your achievements")
    async def achievements(self, ctx: commands.Context, member: discord.Member | None = None):
        target = member or ctx.author
        async with get_session() as session:
            result = await session.execute(select(Achievement).where(Achievement.user_id == target.id, Achievement.guild_id == ctx.guild.id))
            user_achievements = result.scalars().all()
        embed = create_embed(title=f"{target.display_name}'s Achievements", color=EMBED_COLOR)
        if not user_achievements:
            embed.description = "No achievements yet."
        else:
            for ach in user_achievements:
                embed.add_field(name=ach.name, value=ach.description, inline=False)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(AchievementsCog(bot))
