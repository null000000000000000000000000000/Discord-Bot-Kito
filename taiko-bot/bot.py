import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from utils.config import TOKEN, OWNER_IDS, PREFIX, MAINTENANCE_MODE, MAINTENANCE_MESSAGE, EMBED_COLOR, ERROR_COLOR
from utils.logger import logger
from utils.errors import MaintenanceError, PermissionError
from database.manager import init_db

class TaikoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.voice_states = True
        super().__init__(
            command_prefix=commands.when_mentioned_or(PREFIX),
            intents=intents,
            owner_ids=set(OWNER_IDS),
            activity=discord.Activity(type=discord.ActivityType.watching, name="over the server"),
            status=discord.Status.online,
        )

    async def setup_hook(self):
        await init_db()
        logger.info("Database initialized")
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("_"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    logger.info(f"Loaded cog: {filename}")
                except Exception as e:
                    logger.error(f"Failed to load cog {filename}: {e}")
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    async def on_ready(self):
        if not hasattr(self, "start_time"):
            self.start_time = discord.utils.utcnow()
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        if MAINTENANCE_MODE:
            logger.warning("Bot is running in MAINTENANCE mode")

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, MaintenanceError):
            await ctx.send(f"⚠️ {MAINTENANCE_MESSAGE}")
            return
        logger.error(f"Prefix command error: {error}")
        await ctx.send("An error occurred while executing that command.")

    async def on_app_command_error(self, interaction: discord.Interaction, error: Exception):
        from utils.errors import handle_error
        if isinstance(error, MaintenanceError):
            await interaction.response.send_message(f"⚠️ {MAINTENANCE_MESSAGE}", ephemeral=True)
            return
        await handle_error(interaction, error)

bot = TaikoBot()
