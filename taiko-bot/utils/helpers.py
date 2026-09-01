import discord
import random
from datetime import datetime, timedelta
from utils.config import EMBED_COLOR, ERROR_COLOR, SUCCESS_COLOR

def create_embed(title=None, description=None, color=None, **kwargs):
    return discord.Embed(
        title=title,
        description=description,
        color=color or EMBED_COLOR,
        timestamp=kwargs.get("timestamp", datetime.utcnow()),
    )

def success_embed(title="Success", description=None):
    return create_embed(title, description, SUCCESS_COLOR)

def error_embed(title="Error", description=None):
    return create_embed(title, description, ERROR_COLOR)

def get_user_badge(user: discord.Member):
    badges = []
    if user.id == 123456789012345678:
        badges.append("👑 Owner")
    if user.bot:
        badges.append("🤖 Bot")
    return " ".join(badges) if badges else None

def format_time(seconds: int) -> str:
    delta = timedelta(seconds=seconds)
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)

def random_color():
    return random.randint(0, 0xFFFFFF)
