import discord
from bot import bot
from utils.logger import logger

if __name__ == "__main__":
    logger.info("Starting TAIKO Bot...")
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
