import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from sqlalchemy.future import select
from database.manager import get_session
from database.models import Economy, User
from utils.helpers import create_embed, success_embed, error_embed, format_time
from utils.config import EMBED_COLOR, ERROR_COLOR, SUCCESS_COLOR

SHOP_ITEMS = {
    "cookie": {"price": 100, "description": "A delicious cookie"},
    "coffee": {"price": 250, "description": "A warm coffee"},
    "pizza": {"price": 500, "description": "A slice of pizza"},
}

class EconomyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _get_economy(self, user_id: int, guild_id: int) -> Economy:
        async with get_session() as session:
            result = await session.execute(select(Economy).where(Economy.user_id == user_id, Economy.guild_id == guild_id))
            economy = result.scalar_one_or_none()
            if not economy:
                economy = Economy(user_id=user_id, guild_id=guild_id)
                session.add(economy)
                await session.commit()
                await session.refresh(economy)
            return economy

    @commands.hybrid_command(name="balance", description="Check your balance")
    async def balance(self, ctx: commands.Context, member: discord.Member | None = None):
        target = member or ctx.author
        economy = await self._get_economy(target.id, ctx.guild.id)
        embed = create_embed(
            title=f"{target.display_name}'s Balance",
            color=EMBED_COLOR
        )
        embed.add_field(name="Wallet", value=f"{economy.balance:,} coins", inline=True)
        embed.add_field(name="Bank", value=f"{economy.bank:,} coins", inline=True)
        embed.set_thumbnail(url=target.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="daily", description="Claim your daily reward")
    async def daily(self, ctx: commands.Context):
        economy = await self._get_economy(ctx.author.id, ctx.guild.id)
        now = datetime.utcnow()
        if economy.daily_last and (now - economy.daily_last) < timedelta(hours=24):
            remaining = timedelta(hours=24) - (now - economy.daily_last)
            await ctx.send(embed=error_embed(f"You already claimed your daily reward. Come back in {format_time(int(remaining.total_seconds()))}"))
            return
        reward = 500
        economy.balance += reward
        economy.daily_last = now
        async with get_session() as session:
            session.add(economy)
            await session.commit()
        await ctx.send(embed=success_embed(f"You claimed your daily reward of **{reward:,}** coins!"))

    @commands.hybrid_command(name="work", description="Work to earn coins")
    async def work(self, ctx: commands.Context):
        economy = await self._get_economy(ctx.author.id, ctx.guild.id)
        now = datetime.utcnow()
        if economy.work_last and (now - economy.work_last) < timedelta(hours=1):
            remaining = timedelta(hours=1) - (now - economy.work_last)
            await ctx.send(embed=error_embed(f"You are tired. Rest for {format_time(int(remaining.total_seconds()))}"))
            return
        earnings = 100 + __import__('random').randint(0, 200)
        economy.balance += earnings
        economy.work_last = now
        async with get_session() as session:
            session.add(economy)
            await session.commit()
        jobs = ["programmer", "chef", "artist", "streamer", "gamer"]
        job = __import__('random').choice(jobs)
        await ctx.send(embed=success_embed(f"You worked as a **{job}** and earned **{earnings:,}** coins!"))

    @commands.hybrid_command(name="shop", description="View the shop")
    async def shop(self, ctx: commands.Context):
        embed = create_embed(title="Shop", color=EMBED_COLOR)
        for item, data in SHOP_ITEMS.items():
            embed.add_field(name=item.title(), value=f"{data['price']:,} coins - {data['description']}", inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="buy", description="Buy an item from the shop")
    async def buy(self, ctx: commands.Context, item: str):
        item = item.lower()
        if item not in SHOP_ITEMS:
            await ctx.send(embed=error_embed("Item not found in shop."))
            return
        economy = await self._get_economy(ctx.author.id, ctx.guild.id)
        price = SHOP_ITEMS[item]["price"]
        if economy.balance < price:
            await ctx.send(embed=error_embed(f"You need {price:,} coins to buy this item."))
            return
        economy.balance -= price
        async with get_session() as session:
            session.add(economy)
            await session.commit()
        await ctx.send(embed=success_embed(f"You bought **{item.title()}** for {price:,} coins!"))

    @commands.hybrid_command(name="give", description="Give coins to another user")
    async def give(self, ctx: commands.Context, member: discord.Member, amount: int):
        if member.bot or member == ctx.author:
            await ctx.send(embed=error_embed("Invalid target."))
            return
        if amount <= 0:
            await ctx.send(embed=error_embed("Amount must be positive."))
            return
        economy = await self._get_economy(ctx.author.id, ctx.guild.id)
        if economy.balance < amount:
            await ctx.send(embed=error_embed("You don't have enough coins."))
            return
        target_economy = await self._get_economy(member.id, ctx.guild.id)
        economy.balance -= amount
        target_economy.balance += amount
        async with get_session() as session:
            session.add(economy)
            session.add(target_economy)
            await session.commit()
        await ctx.send(embed=success_embed(f"You gave {member.mention} **{amount:,}** coins!"))

async def setup(bot: commands.Bot):
    await bot.add_cog(EconomyCog(bot))
