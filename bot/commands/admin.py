# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
import yaml
from pathlib import Path
from typing import Optional
from datetime import datetime
from nextcord.ext import commands
from nextcord import slash_command, Interaction, SlashOption, Embed, Color

# LOCAL IMPORTS ------------------------------------------------------------------------------------------------------------------------------------|
from core import get_logger

# DECORATORS ---------------------------------------------------------------------------------------------------------------------------------------|
divider = f"=" * 70
sub_divider = f"-" * 70

# PATHS --------------------------------------------------------------------------------------------------------------------------------------------|
# (1) Premissions Config Path
PERMISSIONS_DIR = Path(__file__).resolve().parent.parent.parent
PERMISSIONS_PATH = PERMISSIONS_DIR / "config" / "permissions.yaml"

# PERMISSION UTILITIES -----------------------------------------------------------------------------------------------------------------------------|
# (1) Load permissions from YAML file
def load_permissions() -> dict:
    with open(PERMISSIONS_PATH, "r", encoding = "utf-8") as f:
        return yaml.safe_load(f)

# (2) Check if use has admin role
def has_admin_role(interaction: Interaction) -> bool:
    permissions = load_permissions()
    admin_roles = permissions.get('Roles', {}).get('Admin', [])
    user_role_ids = [role.id for role in interaction.user.roles]
    return any(role_id in admin_roles for role_id in user_role_ids)

# (3) Check if user has moderator role
def has_mod_role(interaction: Interaction) -> bool:
    permissions = load_permissions()
    mod_roles = permissions.get('Roles', {}).get('Mods', [])
    user_role_ids = [role.id for role in interaction.user.roles]
    return any(role_id in mod_roles for role_id in user_role_ids)

# (4) Check if user has admin or moderator role
def has_permissions(interaction: Interaction) -> bool:
    return has_admin_role(interaction) or has_mod_role(interaction)

# (5) Get mod logs channel ID
def get_mod_logs_channel() -> Optional[int]:
    permissions = load_permissions()
    mod_logs = permissions.get('mod_logs')
    
    # --- Return None if mod_logs is disabled ---
    if mod_logs in (None, False, 0):
        return None
    return mod_logs

# MAIN ---------------------------------------------------------------------------------------------------------------------------------------------|
class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger()
        self.logger.info("Admin Commands initialized")

    # --- Helper function to log command usage ---
    async def log_command_usage(
        self,
        interaction: Interaction,
        command_name: str,
        details: str
    ):
        try:
            mod_logs_id = get_mod_logs_channel()
            if mod_logs_id is None:
                return
            
            channel = self.bot.get_channel(mod_logs_id)
            if channel is None:
                self.logger.error(sub_divider)
                self.logger.warning(f"Mod logs channel {mod_logs_id} not found")
                self.logger.error(sub_divider)
                return
            
            # --- Building embed ---
            embed = Embed(
                title = f"{command_name} Command used",
                description = f'''
                **User**: {interaction.user}
                **User ID:** {interaction.user.id}
                **Channel:** {interaction.channel.mention}
                **Details:** {details}
                ''',
                timestamp = datetime.utcnow(),
                color = Color.dark_orange()
            )
            embed.set_thumbnail(url = interaction.user.display_avatar.url)
            await channel.send(embed = embed)
        
        except Exception as e:
            # --- Error Handling ---
            self.logger.error(sub_divider)
            self.logger.error(f"Failed to log command usage: {e}")
            self.logger.error(sub_divider)

    # (1) Purge Command
    @slash_command(
        name = "purge",
        description = "Delete a specifide number of messages from the channel"
    )
    async def purge(
        self,
        interaction: Interaction,
        amount: int = SlashOption(
            name = "amount",
            description = "Number of messages to delete (1-100)",
            required = True,
            min_value = 1,
            max_value = 100
        )
    ):
        try:
            # --- Permission check ---
            if not has_permissions(interaction):
                embed = Embed(
                    title = "Permission Denied",
                    description = "You don't have permission to use this command. `Admin` or `Mod` role required.",
                    color = Color.red()
                )
                await interaction.response.send_message(embed = embed, ephemeral = True)
                return
            
            # --- Defer response ---
            await interaction.response.defer(ephemeral = True)

            # --- Check bot permissions ---
            if not interaction.channel.permissions_for(interaction.guild.me).manage_messages:
                embed = Embed(
                    title = "Bot Permission Error",
                    description = "I don't have permission to manage messages.",
                    color = Color.red()
                )
                await interaction.followup.send(embed = embed, ephemeral = True)
                return
            
            # --- Purge messages ---
            deleted = await interaction.channel.purge(limit = amount)

            # --- Building embed ---
            embed = Embed(
                title = "Messages Purged",
                description = f"Successfully deleted **{len(deleted)}** message(s)",
                color = Color.dark_orange()
            )
            await interaction.followup.send(embed = embed, ephemeral = True)

            # --- Log to mod_logs channel ---
            await self.log_command_usage(
                interaction,
                "Purge",
                f"Deleted **{len(deleted)}** messages \nRequested amount: **{amount}**"
            )

        except Exception as e:
            # --- Error Handling ---
            embed = Embed(
                title = "Error",
                description = "An error occrurred while processing the command. Please try again later.",
                color = Color.red()
            )
            await interaction.followup.send(embed = embed, ephemeral = True)
            self.logger.error(sub_divider)
            self.logger.error(f"Error in purge command: {e}")
            self.logger.error(sub_divider)

# SETUP FUNCTION -----------------------------------------------------------------------------------------------------------------------------------|
def setup(bot: commands.Bot):
    bot.add_cog(AdminCommands(bot))
