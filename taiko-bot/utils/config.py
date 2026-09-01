import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_IDS = [int(i) for i in os.getenv("OWNER_IDS", "").split(",") if i]
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///data/taiko.db")
PREFIX = os.getenv("PREFIX", "!")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
EMBED_COLOR = int(os.getenv("EMBED_COLOR", "0x5865F2"), 16)
ERROR_COLOR = int(os.getenv("ERROR_COLOR", "0xED4245"), 16)
SUCCESS_COLOR = int(os.getenv("SUCCESS_COLOR", "0x57F287"), 16)

MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"
MAINTENANCE_MESSAGE = os.getenv("MAINTENANCE_MESSAGE", "Bot is under maintenance.")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set in environment variables.")
