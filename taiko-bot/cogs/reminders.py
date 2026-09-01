import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from utils.helpers import create_embed, success_embed, error_embed, format_time
from utils.config import EMBED_COLOR, ERROR_COLOR

class RemindersCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._reminders: list[dict] = []

    @commands.hybrid_command(name="remind", description="Set a reminder")
    async def remind(self, ctx: commands.Context, duration: str, *, message: str):
        seconds = self._parse_time(duration)
        if seconds is None or seconds < 10:
            await ctx.send(embed=error_embed("Invalid duration. Use e.g. 10s, 5m, 1h, 1d"))
            return
        reminder = {
            "user_id": ctx.author.id,
            "channel_id": ctx.channel.id,
            "guild_id": ctx.guild.id,
            "message": message,
            "end_time": datetime.utcnow() + timedelta(seconds=seconds),
        }
        self._reminders.append(reminder)
        await ctx.send(embed=success_embed(f"I will remind you in {format_time(seconds)}."))

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self._reminder_loop())

    async def _reminder_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            now = datetime.utcnow()
            ready = [r for r in self._reminders if r["end_time"] <= now]
            for reminder in ready:
                self._reminders.remove(reminder)
                channel = self.bot.get_channel(reminder["channel_id"])
                if channel:
                    try:
                        await channel.send(f"⏰ <@{reminder['user_id']}> Reminder: {reminder['message']}")
                    except Exception:
                        pass
            await __import__('asyncio').sleep(30)

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
    await bot.add_cog(RemindersCog(bot))
