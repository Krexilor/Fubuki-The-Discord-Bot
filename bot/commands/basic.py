# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
import json
import nextcord
from pathlib import Path
from datetime import datetime
from nextcord.ext import commands
from nextcord import slash_command, Interaction, SlashOption, Embed, Color

# LOCAL IMPORTS ------------------------------------------------------------------------------------------------------------------------------------|
from core import get_logger

# DECORATORS ---------------------------------------------------------------------------------------------------------------------------------------|
divider = f"=" * 70
sub_divider = f"-" * 70

# PATHS --------------------------------------------------------------------------------------------------------------------------------------------|
# # (1) Profile Assets Path
PROFILE_DIR = Path(__file__).resolve().parent.parent.parent
PROFILE_PATH = PROFILE_DIR / "assets" / "profile"

# (2) Help Config Path
HELP_CMD_DIR = Path(__file__).resolve().parent.parent.parent
HELP_CMD_PATH = HELP_CMD_DIR / "config" / "commands" / "help.json"

# MAIN ---------------------------------------------------------------------------------------------------------------------------------------------|
class BasicCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger()
        self.logger.info("Basic Commands initialized")

    # (1) Ping Command
    @slash_command(
        name = "ping",
        description = "Check the bot's latency"
    )
    async def ping(
        self,
        interaction: Interaction
    ):
        try:
            # --- Calculating latency ---
            latency = round(self.bot.latency * 1000)
        
            # --- Building embed ---
            embed = nextcord.Embed(
                title = "🏓 Pong!",
                description = f"Bot latency: **{latency}ms**",
                color = Color.dark_purple()
            )
        
            # --- Sending message ---
            await interaction.response.send_message(embed = embed)
            self.logger.info(sub_divider)

        except Exception as e:
            # --- Error Handling ---
            embed = Embed(
                title = "Error",
                description = "An error occrurred while processing the command. Please try again later.",
                color = Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)
            self.logger.error(sub_divider)
            self.logger.error(f"Error in ping command: {e}")
            self.logger.error(sub_divider)

    # (2) BotInfo Command
    @slash_command(
        name = "botinfo",
        description = "Get information about the bot"
    )
    async def botinfo(
        self,
        interaction: Interaction
    ):
        try:
            # --- Bot information ---
            bot_name = self.bot.user.name
            guild_count = len(self.bot.guilds)
            member_count = sum(guild.member_count for guild in self.bot.guilds)
            latency = round(self.bot.latency * 1000)

            # --- Calculate Uptime ---
            uptime_delta = datetime.now() - self.bot.start_time
            days = uptime_delta.days
            hours, remainder = divmod(uptime_delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            if days > 0:
                uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

            elif hours > 0:
                uptime_str = f"{hours}h {minutes}m {seconds}s"

            elif minutes > 0:
                uptime_str = f"{minutes}m {seconds}s"

            else:
                uptime_str = f"{seconds}s"

            # --- Building embed ---
            embed = Embed(
                description = f'''
                Hello! I'm **{bot_name}**, a powerful multipurpose Discord bot built to help server owners manage, engage, and grow their communitites effortlessly.
                
                I combine **moderation**, **utility**, and **fun** features into one seamless experience.
                
                📊 **Statistics**
                 • Servers: {guild_count}
                 • Members: {member_count}
                 • Uptime: {uptime_str}
                 • Latency: {latency} ms

                🛠️ **Main Features**
                 • Moderation tools
                 • Utility & automation
                 • Fun & interactive commands
                 • Server management helpers
                 • Constant updates & improvements

                👨‍💻 **Developer Info**
                 • Developed by: Krexilor
                 • Contact: [GitHub](https://github.com/Krexilor) | [Discord](https://discord.com/users/1369319022918631525)
                ''',
                color = Color.dark_purple()
            )
            embed.set_footer(text = "Thank you for using this bot • Built with nextcord")

            banner_path = PROFILE_PATH / "banner.png"
            if banner_path.exists():
                embed.set_image(url = "attachment://banner.png")
                file = nextcord.File(banner_path, filename = "banner.png")
                await interaction.response.send_message(embed = embed, file = file)

            else:
                await interaction.response.send_message(embed = embed)

        except Exception as e:
            # --- Error Handling ---
            embed = Embed(
                title = "Error",
                description = "An error occrurred while processing the command. Please try again later.",
                color = Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)
            self.logger.error(sub_divider)
            self.logger.error(f"Error in botinfo command: {e}")
            self.logger.error(sub_divider)

    # (3) ServerInfo Command
    @slash_command(
        name = "serverinfo",
        description = "Get information about the server"
    )
    async def serverinfo(
        self,
        interaction: Interaction
    ):
        try:
            guild = interaction.guild

            # --- Gathering server information ---
            server_name = guild.name
            member_count = guild.member_count
            owner = await guild.fetch_member(guild.owner_id)
            creation_date = guild.created_at.strftime("%Y-%m-%d %H:%M:%S")
            region = guild.region
            verification_level = str(guild.verification_level).replace("_", " ").title()
            roles_count = len(guild.roles)
            channels_count = len(guild.channels)
            emojis_count = len(guild.emojis)
            stickers_count = len(guild.stickers)
            boost_level = guild.premium_tier
            boost_count = guild.premium_subscription_count
            boost_info = f"Level {boost_level} with {boost_count} boosts" if boost_count > 0 else "No boosts"

            # --- Building embed ---
            embed = Embed(
                title = "Server Information",
                description = f'''
                Here is some information about the server:

                • **Server Name**: {server_name}
                • **Owner**: {owner}
                • **Members**: {member_count}
                • **Created On**: {creation_date} UTC
                • **Region**: {region}
                • **Verification Level**: {verification_level}
                • **Roles**: {roles_count}
                • **Channels**: {channels_count}
                • **Emojis**: {emojis_count}
                • **Stickers**: {stickers_count}
                • **Boosts**: {boost_info}
                ''',
                color = Color.dark_purple()
            )
            embed.set_image(url = guild.icon.url) if guild.icon else None
            await interaction.response.send_message(embed = embed)

        except Exception as e:
            # --- Error Handling ---
            embed = Embed(
                title = "Error",
                description = "An error occrurred while processing the command. Please try again later.",
                color = Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)
            self.logger.error(sub_divider)
            self.logger.error(f"Error in serverinfo command: {e}")
            self.logger.error(sub_divider)

    # (4) UserInfo Command
    @slash_command(
        name = "userinfo",
        description = "Get information about a user"
    )
    async def userinfo(
        self,
        interaction: Interaction,
        user: nextcord.Member = SlashOption(
            name = "user",
            description = "The user to get information about",
            required = True
        )
    ):
        try:
            # --- Gathering user information ---
            username = str(user)
            account_creation = user.created_at.strftime("%Y-%m-%d %H:%M:%S")
            join_date = user.joined_at.strftime("%Y-%m-%d %H:%M:%S") if user.joined_at else "N/A"
            roles = [role.mention for role in user.roles if role.name != "@everyone"]
            roles_display = ", ".join(roles) if roles else "No roles"
            status = str(user.status).title()
            top_role = user.top_role.mention if user.top_role else "N/A"

            # --- Building embed ---
            embed = Embed(
                title = "User Information",
                description = f'''
                Here is some information about **{username}**:

                • **Account Created On**: {account_creation} UTC
                • **Joined Server On**: {join_date} UTC
                • **Status**: {status}
                • **Top Role**: {top_role}
                • **Roles**: {roles_display}
                ''',
                color = Color.dark_purple()
            )
            embed.set_thumbnail(url = user.avatar.url) if user.avatar else None
            await interaction.response.send_message(embed = embed)

        except Exception as e:
            # --- Error Handling ---
            embed = Embed(
                title = "Error",
                description = "An error occrurred while processing the command. Please try again later.",
                color = Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)
            self.logger.error(sub_divider)
            self.logger.error(f"Error in userinfo command: {e}")
            self.logger.error(sub_divider)

    # (5) Invite Command
    @slash_command(
        name = "invite",
        description = "Get the bot's invite link"
    )
    async def invite(
        self,
        interaction: Interaction
    ):
        try:
            # --- Bot client ID ---
            client_id = self.bot.user.id

            # --- Building embed ---
            embed = Embed(
                title = "Invite Me to Your Server!",
                description = f"Click the link below to invite the bot to your server:\n\n[Invite Link](https://discord.com/oauth2/authorize?client_id={client_id})",
                color = Color.dark_purple()
            )
            await interaction.response.send_message(embed = embed)

        except Exception as e:
            # --- Error Handling ---
            embed = Embed(
                title = "Error",
                description = "An error occrurred while processing the command. Please try again later.",
                color = Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)
            self.logger.error(sub_divider)
            self.logger.error(f"Error in invite command: {e}")
            self.logger.error(sub_divider)

    # (6) Help Command
    @slash_command(
        name = "help",
        description = "Get help with various bot commands"
    )
    async def help(
        self,
        interaction: Interaction,
        name: str = SlashOption(
            name = "name",
            description = "The command you need help with",
            required = True,
            choices = {
                "Avatar Command": "Avatar",
                "BotInfo Command": "BotInfo",
                "CoinFlip Command": "CoinFlip",
                "Choose Command": "Choose",
                "Compliment Command": "Compliment",
                "Emojify Command": "Emojify",
                "Insult Command": "Insult",
                "Invite Command": "Invite",
                "Mock Command": "Mock",
                "Ping Command": "Ping",
                "Purge Command": "Purge",
                "Rate Command": "Rate",
                "Reverse Command": "Reverse",
                "ServerInfo Command": "ServerInfo",
                "Ship Command": "Ship",
                "UserInfo Command": "UserInfo"
            }
        )
    ):
        try:
            # --- Load help configuration ---
            with open(HELP_CMD_PATH, "r", encoding = "utf-8") as f:
                help_data = json.load(f)

            # --- Fetch command help data ---
            command_data = help_data.get(name)

            if not command_data:
                embed = Embed(
                    title = "Error",
                    description = "No information available for this command.",
                    color = Color.red()
                )
                await interaction.response.send_message(embed = embed, ephemeral = True)
                return
            
            # --- Help command info ---
            description_text = command_data['description']
            usage_text = " ".join(f"  • `{u}`" for u in command_data["usage"])
            restriction_text = command_data['restriction']
            example_text = " ".join(f"  • {e}" for e in command_data["example"])
            
            # --- Building embed ---
            embed = Embed(
                title = f"Help • /{command_data['name']}",
                description = f'''
                • **Description:** {description_text}

                • **Usage:** {usage_text}

                • **Restrictions:** {restriction_text}
                
                • **Example:** {example_text}
                ''',
                color = Color.dark_purple()
            )
            embed.set_footer(text = "Use /help to explore other commands")
            await interaction.response.send_message(embed = embed)

        except Exception as e:
            # --- Error Handling ---
            embed = Embed(
                title = "Error",
                description = "An error occrurred while processing the command. Please try again later.",
                color = Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)
            self.logger.error(sub_divider)
            self.logger.error(f"Error in help command: {e}")
            self.logger.error(sub_divider)

# SETUP FUNCTION -----------------------------------------------------------------------------------------------------------------------------------|
def setup(bot: commands.Bot):
    bot.add_cog(BasicCommands(bot))
