import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy.future import select
from database.manager import get_session
from database.models import Guild
from utils.helpers import create_embed, success_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR
from utils.permissions import has_permissions

PREMIUM_PLANS = {
    "basic": {"price": "$5", "features": ["Custom commands", "Basic analytics"]},
    "pro": {"price": "$10", "features": ["Custom commands", "Advanced analytics", "Priority support", "Custom branding"]},
    "ultimate": {"price": "$20", "features": ["Everything in Pro", "AI chatbot", "Custom dashboard", "Dedicated support"]},
}

class PremiumCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._premium_guilds: set[int] = set()
        self._premium_users: set[int] = set()

    @commands.hybrid_command(name="premium", description="View premium information")
    async def premium_info(self, ctx: commands.Context):
        embed = create_embed(title="✨ TAIKO Premium", color=EMBED_COLOR)
        for plan, data in PREMIUM_PLANS.items():
            embed.add_field(name=f"{plan.title()} - {data['price']}", value="\n".join(data["features"]), inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="upgrade", description="Upgrade to premium")
    @has_permissions(administrator=True)
    async def upgrade(self, ctx: commands.Context, plan: str):
        plan = plan.lower()
        if plan not in PREMIUM_PLANS:
            await ctx.send(embed=error_embed("Invalid plan. Choose: basic, pro, ultimate"))
            return
        async with get_session() as session:
            result = await session.execute(select(Guild).where(Guild.id == ctx.guild.id))
            guild = result.scalar_one_or_none()
            if not guild:
                guild = Guild(id=ctx.guild.id, name=ctx.guild.name)
                session.add(guild)
            guild.maintenance_mode = True
            await session.commit()
        self._premium_guilds.add(ctx.guild.id)
        await ctx.send(embed=success_embed(f"Server upgraded to **{plan.title()}** premium!"))

    @commands.hybrid_command(name="premiumstatus", description="Check premium status")
    async def premium_status(self, ctx: commands.Context):
        is_premium = ctx.guild.id in self._premium_guilds
        embed = create_embed(
            title="Premium Status",
            description=f"This server is {'**PREMIUM**' if is_premium else '**FREE**'}",
            color=EMBED_COLOR
        )
        await ctx.send(embed=embed)

    def is_premium_guild(self, guild_id: int) -> bool:
        return guild_id in self._premium_guilds

async def setup(bot: commands.Bot):
    await bot.add_cog(PremiumCog(bot))
