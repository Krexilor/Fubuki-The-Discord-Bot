# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
import nextcord

# LOCAL IMPORTS -----------------------------------------------------------------------------------------------------------------------------------|
from core import get_logger

# DECORATORS ---------------------------------------------------------------------------------------------------------------------------------------|
divider = f"=" * 70
sub_divider = f"-" * 70

# MAIN --------------------------------------------------------------------------------------------------------------------------------------------|
class OnReadyEvent:
    def __init__(self, bot: nextcord.Client):
        self.bot = bot
        self.logger = get_logger()

    # --- OnReady Event Handler ---
    async def handle(self):
        # --- ENSURE websocket is fully ready ---
        await self.bot.wait_until_ready()

        # --- Set Bot Presence (NOW RELIABLE) ---
        activity = self.bot.build_activity()
        status = self.bot.build_status()

        await self.bot.change_presence(
            status = status,
            activity = activity
        )

        # --- Guild Info ---
        guild = self.bot.guilds[0] if self.bot.guilds else None

        # =========================
        # BOT INFORMATION
        # =========================
        self.logger.info(divider)
        self.logger.info("BOT INFO")
        self.logger.info(sub_divider)

        self.logger.info(f"Bot Name        : {self.bot.user}")
        self.logger.info(f"Bot ID          : {self.bot.user.id}")
        self.logger.info(f"Created On      : {self.bot.user.created_at.strftime('%d-%m-%Y %H:%M:%S')}")
        self.logger.info(f"Latency         : {round(self.bot.latency * 1000)} ms")
        self.logger.info(f"Guilds Connected: {len(self.bot.guilds)}")

        if activity:
            self.logger.info(f"Activity        : {activity.type.name.title()} | {activity.name}")

        else:
            self.logger.info("Activity        : None")

        self.logger.info(f"Status          : {status.name.title()}")
        self.logger.info(divider)

        # =========================
        # SERVER INFORMATION
        # =========================
        if guild:
            self.logger.info("SERVER INFO")
            self.logger.info(sub_divider)

            self.logger.info(f"Server Name     : {guild.name}")
            self.logger.info(f"Server ID       : {guild.id}")
            self.logger.info(f"Owner           : {guild.owner}")
            self.logger.info(f"Created On      : {guild.created_at.strftime('%d-%m-%Y %H:%M:%S')}")
            self.logger.info(f"Members         : {guild.member_count}")
            self.logger.info(f"Text Channels   : {len(guild.text_channels)}")
            self.logger.info(f"Voice Channels  : {len(guild.voice_channels)}")
            self.logger.info(f"Categories      : {len(guild.categories)}")
            self.logger.info(f"Roles           : {len(guild.roles)}")
            self.logger.info(f"Boost Level     : {guild.premium_tier}")
            self.logger.info(f"Boosts          : {guild.premium_subscription_count}")

            self.logger.info(divider)
