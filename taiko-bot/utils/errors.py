import traceback
import discord
from utils.logger import logger
from utils.config import ERROR_COLOR, EMBED_COLOR

class TaikoError(Exception):
    pass

async def handle_error(interaction: discord.Interaction, error: Exception):
    logger.error(f"Command error: {error}\n{traceback.format_exc()}")
    embed = discord.Embed(
        title="Error",
        description=f"An unexpected error occurred: {str(error)}",
        color=ERROR_COLOR
    )
    try:
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception:
        pass

class PermissionError(TaikoError):
    pass

class CooldownError(TaikoError):
    pass

class MaintenanceError(TaikoError):
    pass
