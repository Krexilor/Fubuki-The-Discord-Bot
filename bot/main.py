# LIBRARIES------------------------------------------------------------------------------------------------------------------------------------------|
import os
from dotenv import load_dotenv

# LOCAL IMPORTS--------------------------------------------------------------------------------------------------------------------------------------|
from core import get_logger
from core import BotClient

from helpers import validate_configs
from helpers import validate_assets

#INITIALIZATION-------------------------------------------------------------------------------------------------------------------------------------|
# (1) Load environment variables
load_dotenv()

# (2) Logger
logger = get_logger()

# DECORATORS ---------------------------------------------------------------------------------------------------------------------------------------|
divider = f"=" * 70
sub_divider = f"-" * 70

# BOT TOKEN------------------------------------------------------------------------------------------------------------------------------------------|
def bot_token():
    token = os.getenv("TOKEN")
    if token:
        logger.info("Bot token successfully retrieved.")
        logger.info("Starting bot...")
        logger.info(sub_divider)
        return token

    else:
        logger.critical("Bot token not found! Please set the TOKEN environment variable.")
        raise RuntimeError("Missing Discord bot token.")

# MAIN-----------------------------------------------------------------------------------------------------------------------------------------------|
def main():
    # Configuration validation
    if not validate_configs():
        logger.critical("Configuration validation failed. Please fix the above errors and restart the bot.")
        exit(1)

    # Assets validation
    if not validate_assets():
        logger.critical("Assets validation failed. Please fix the above errors and restart the bot.")
        exit(1)

    # Bot token
    logger.info(divider)
    TOKEN = bot_token()

    # Starting bot
    bot = BotClient()
    bot.run(TOKEN)

# RUNNING THE BOT------------------------------------------------------------------------------------------------------------------------------------|
if __name__ == "__main__":
    main()
