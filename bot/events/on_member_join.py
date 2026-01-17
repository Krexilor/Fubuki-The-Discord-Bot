# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
import yaml
import random
import nextcord
import traceback
from pathlib import Path
from nextcord import Embed, Color

# LOCAL IMPORTS ------------------------------------------------------------------------------------------------------------------------------------|
from core import get_logger

# PATHS -------------------------------------------------------------------------------------------------------------------------------------------|
# (1) Welcome Images Path
WELCOME_IMAGE_DIR = Path(__file__).resolve().parent.parent.parent
WELCOME_IMAGE_PATH = WELCOME_IMAGE_DIR / "assets" / "welcome"

# (2) Config Files Path
CONFIG_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = CONFIG_DIR / "config" / "bot.yaml"

# (3) Premissions Config Path
PERMISSIONS_DIR = Path(__file__).resolve().parent.parent.parent
PERMISSIONS_PATH = PERMISSIONS_DIR / "config" / "permissions.yaml"

# DECORATORS ---------------------------------------------------------------------------------------------------------------------------------------|
divider = f"=" * 70
sub_divider = f"-" * 70

# MAIN ---------------------------------------------------------------------------------------------------------------------------------------------|
class OnMemberJoinEvent:
    def __init__(self, bot: nextcord.Client):
        self.bot = bot
        self.logger = get_logger()
        self.config = self._load_config()
        self.permissions = self._load_permissions()

    # --- Load Bot Config ---
    def _load_config(self) -> dict:
        try:
            with CONFIG_PATH.open("r", encoding = "utf-8") as f:
                return yaml.safe_load(f)
            
        except FileNotFoundError:
            return {}
        
    # --- Load Permissions Config ---
    def _load_permissions(self) -> dict:
        try:
            with PERMISSIONS_PATH.open("r", encoding = "utf-8") as f:
                return yaml.safe_load(f)
            
        except FileNotFoundError:
            return {}
        
    # --- Get Random Welcome Image ---
    def _get_random_welcome_image(self) -> Path:
        if not WELCOME_IMAGE_PATH.exists():
            return None
        
        # --- Get all supported image files ---
        image_extensions = [".png", ".jpg", ".jpeg"]
        images = [img for img in WELCOME_IMAGE_PATH.iterdir() if img.is_file() and img.suffix.lower() in image_extensions]

        if not images:
            self.logger.error(sub_divider)
            self.logger.warning(f"No Welcome images found at: {WELCOME_IMAGE_PATH}")
            self.logger.error(sub_divider)
            return None
        
        return random.choice(images)

    # --- OnMemberJoin Event Handler ---
    async def handle(self, member: nextcord.Member):
        try:
            # --- Check if welcome messages are enabled ---
            if not self.config.get("features", {}).get("welcome_messages", False):
                self.logger.error(sub_divider)
                self.logger.debug(f"Welcome messages disabled. Skipping for {member.name}")
                self.logger.error(sub_divider)
                return
            
            # --- Get welcome channel ID ---
            welcome_channel_id = self.permissions.get("welcome")

            if not welcome_channel_id:
                self.logger.error(sub_divider)
                self.logger.error("Welcome channel ID not found in permissions.yaml")
                self.logger.error(sub_divider)
                return
            
            # --- Get welcome channel ---
            welcome_channel = self.bot.get_channel(welcome_channel_id)

            if not welcome_channel:
                return
            
            # --- Assign new member role ---
            new_member_role_ids = self.permissions.get("Roles", {}).get("New_Member", [])

            if new_member_role_ids:
                for role_id in new_member_role_ids:
                    role = member.guild.get_role(role_id)

                    if role:
                        try:
                            await member.add_roles(role)
                            self.logger.info(f"Assigned role '{role.name}' to '{member.name}'")

                        except nextcord.Forbidden:
                            self.logger.error(sub_divider)
                            self.logger.error(f"Missing permissions to assign role '{role.name}' to '{member.name}'")
                            self.logger.error(sub_divider)

                        except Exception as e:
                            self.logger.error(sub_divider)
                            self.logger.error(f"Error assigning role to {member.name}: {e}")
                            self.logger.error(sub_divider)

                    else:
                        self.logger.error(sub_divider)
                        self.logger.warning(f"Role with ID {role_id} not found")
                        self.logger.error(sub_divider)

            # --- Building welcome embed ---
            welcome_image = self._get_random_welcome_image()

            embed = Embed(
                title = "🎉 Welcome to the Server!",
                description = f'''
                Welcome {member.mention}! We're glad to have you here.

                We have assigned you {role.name} which will let you interact with the server.

                __**GETTING STARTED**__
                • Introduce yourself to the community in `👋│introductions channel`.
                • Go through the server rule ` ` to avoid getting any penalties.
                • Get yourself some fun roles from ` ` channel.
                • Stay update with ` ` channel.
                • Type `/help` to get more information about the community.

                Hope you will enjoy your stay here.
                ''',
                color = Color.blurple()
            )
            if welcome_image:
                file = nextcord.File(welcome_image, filename = welcome_image.name)
                embed.set_image(url = f"attachment://{welcome_image.name}")
                
                await welcome_channel.send(embed = embed, file = file)

            else:
                await welcome_channel.send(embed = embed)

        except Exception as e:
            self.logger.error(sub_divider)
            self.logger.error(f"Error in OnMemberJoin event for {member.name}: {e}")
            self.logger.error(traceback.format_exc())
            self.logger.error(sub_divider)
