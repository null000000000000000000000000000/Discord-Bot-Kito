import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from asyncio import sleep
from utils.helpers import create_embed, success_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR
from utils.permissions import has_permissions

class GiveawayCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._giveaways: dict[int, dict] = {}

    @commands.hybrid_command(name="giveaway", description="Create a giveaway")
    @has_permissions(manage_guild=True)
    async def create_giveaway(self, ctx: commands.Context, duration: str, winners: int, *, prize: str):
        seconds = self._parse_time(duration)
        if seconds is None or seconds < 10:
            await ctx.send(embed=error_embed("Invalid duration. Use e.g. 10s, 5m, 1h, 1d"))
            return
        if winners < 1:
            await ctx.send(embed=error_embed("There must be at least 1 winner."))
            return
        end_time = datetime.utcnow() + timedelta(seconds=seconds)
        embed = create_embed(
            title=f"🎉 {prize}",
            description=f"React with 🎉 to enter!\nWinners: {winners}\nEnds: {discord.utils.format_dt(end_time, style='R')}",
            color=EMBED_COLOR
        )
        embed.set_footer(text=f"Giveaway by {ctx.author}")
        message = await ctx.send(embed=embed)
        await message.add_reaction("🎉")
        self._giveaways[message.id] = {
            "message_id": message.id,
            "channel_id": ctx.channel.id,
            "guild_id": ctx.guild.id,
            "prize": prize,
            "winners": winners,
            "end_time": end_time,
            "host": ctx.author.id,
        }
        await ctx.send(embed=success_embed(f"Giveaway created! It will end in {duration}."))

    @commands.hybrid_command(name="endgiveaway", description="End a giveaway early")
    @has_permissions(manage_guild=True)
    async def end_giveaway(self, ctx: commands.Context, message_id: str):
        try:
            message_id_int = int(message_id)
        except ValueError:
            await ctx.send(embed=error_embed("Invalid message ID."))
            return
        giveaway = self._giveaways.get(message_id_int)
        if not giveaway:
            await ctx.send(embed=error_embed("Giveaway not found."))
            return
        await self._end_giveaway(message_id_int)
        await ctx.send(embed=success_embed("Giveaway ended!"))

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self._giveaway_loop())

    async def _giveaway_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            now = datetime.utcnow()
            to_end = [mid for mid, g in self._giveaways.items() if g["end_time"] <= now]
            for mid in to_end:
                await self._end_giveaway(mid)
            await sleep(30)

    async def _end_giveaway(self, message_id: int):
        giveaway = self._giveaways.pop(message_id, None)
        if not giveaway:
            return
        channel = self.bot.get_channel(giveaway["channel_id"])
        if not channel:
            return
        try:
            message = await channel.fetch_message(message_id)
        except Exception:
            return
        users = []
        for reaction in message.reactions:
            if str(reaction.emoji) == "🎉":
                users = [user async for user in reaction.users() if not user.bot]
                break
        if not users:
            embed = create_embed(title="🎉 Giveaway Ended", description=f"Prize: {giveaway['prize']}\nNo winners! No valid entries.", color=EMBED_COLOR)
            await message.edit(embed=embed)
            return
        winners_count = min(giveaway["winners"], len(users))
        winners = __import__("random").sample(users, winners_count)
        winners_text = ", ".join([w.mention for w in winners])
        embed = create_embed(title="🎉 Giveaway Ended", description=f"Prize: {giveaway['prize']}\nWinners: {winners_text}", color=EMBED_COLOR)
        await message.edit(embed=embed)
        await channel.send(f"Congratulations {winners_text}, you won **{giveaway['prize']}**!")

    def _parse_time(self, duration: str) -> int | None:
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        for unit, multiplier in units.items():
            if duration.endswith(unit):
                try:
                    return int(duration[:-1]) * multiplier
                except ValueError:
                    return None
        try:
            return int(duration)
        except ValueError:
            return None

async def setup(bot: commands.Bot):
    await bot.add_cog(GiveawayCog(bot))
