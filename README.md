![Banner](https://github.com/Krexilor/Fubuki-The-Discord-Bot/blob/main/assets/profile/banner.png)

# 🤖 Fubuki Discord Bot

A powerful, feature-rich Discord bot built with Python and nextcord, designed for server management, moderation, and entertainment.

## ✨ Features

### 🛡️ Moderation Commands
- **Purge** - Bulk delete messages from channels (Admin/Mod only)

### 📊 Information Commands
- **Ping** - Check bot latency
- **BotInfo** - Display detailed bot statistics and information
- **ServerInfo** - View comprehensive server details
- **UserInfo** - Get information about any server member
- **Invite** - Generate bot invite link

### 🎮 Fun & Entertainment
- **Mock** - Convert text to aLtErNaTiNg CaSe
- **Reverse** - Reverse any text string
- **Emojify** - Convert text to regional indicator emojis
- **Rate** - Rate anything on a scale of 1-10
- **Choose** - Let the bot choose between 2-5 options
- **Ship** - Calculate compatibility between two users
- **Compliment** - Send a random compliment to someone
- **Insult** - Light-heartedly roast someone
- **CoinFlip** - Flip a coin (Heads or Tails)
- **Avatar** - Display user avatars with optional filters (20+ effects including blur, grayscale, sepia, pro enhance, and more)

### 🎉 Welcome System
- Automated welcome messages for new members
- Random welcome image selection
- Auto-assign roles to new members
- Customizable welcome channel

### 📝 Advanced Features
- **Custom Logger System** - Comprehensive logging with console and file output
- **Pre-flight Validation** - Validates all configs and assets before bot startup
- **Mod Logs** - Automatic logging of moderation actions
- **Help Command** - Detailed help for all commands with usage examples

---

## 📁 Project Structure

```
Fubuki/
├── assets/
│   ├── commands/
│   │   └── coinflip/
│   │       ├── head.png
│   │       └── tail.png
│   ├── profile/
│   │   └── banner.png
│   └── welcome/
│       ├── welcome1.png
│       ├── welcome2.png
│       ├── welcome3.png
│       ├── welcome4.png
│       └── welcome5.png
├── bot/
│   ├── commands/
│   │   ├── admin.py
│   │   ├── basic.py
│   │   └── fun.py
│   ├── core/
│   │   ├── client.py
│   │   └── logger.py
│   ├── events/
│   │   ├── on_member_join.py
│   │   └── on_ready.py
│   └── helpers/
│       ├── assets_check.py
│       └── config_check.py
├── config/
│   ├── commands/
│   │   ├── fun.json
│   │   └── help.json
│   ├── bot.yaml
│   ├── logger.yaml
│   └── permissions.yaml
├── logs/
├── main.py
├── .env
└── requirements.txt
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Discord Bot Token ([Create one here](https://discord.com/developers/applications))

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/fubuki-bot.git
cd fubuki-bot
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Open the `.env` file and add your Discord bot token:
```env
TOKEN=YOUR_BOT_TOKEN_HERE
```
> ⚠️ **Important:** Replace `YOUR_BOT_TOKEN_HERE` with your actual Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications).

### Step 4: Configure Bot Settings

#### **bot.yaml** ⚠️ REQUIRED CONFIGURATION
The repository includes a template. You **must** fill in the following fields:

```yaml
bot:
  status: "online"                    # online, idle, dnd, invisible
  activity_type: "playing"            # playing, watching, listening, streaming, competing
  activity_name: "with slash commands"
  owner_ids: [                        # ⚠️ FILL THIS - Your Discord User ID(s)
    "YOUR_DISCORD_USER_ID"
  ]
  client_id: "YOUR_BOT_CLIENT_ID"    # ⚠️ FILL THIS - Bot's Client ID

features:
  welcome_messages: true              # Enable/disable welcome system

intents:
  guilds: true
  members: true
  messages: true
  message_content: true
```

#### **permissions.yaml** ⚠️ REQUIRED CONFIGURATION
The repository includes a template. You **must** replace all placeholder values with your actual Discord IDs:

```yaml
Roles:
  Admin: [                            # ⚠️ FILL THIS - Admin role ID(s)
    ADMIN_ROLE_ID_HERE
  ]
  Mods: [                             # ⚠️ FILL THIS - Moderator role ID(s)
    MOD_ROLE_ID_HERE
  ]
  New_Member: [                       # ⚠️ FILL THIS - New member role ID(s)
    NEW_MEMBER_ROLE_ID_HERE
  ]

mod_logs: MOD_LOGS_CHANNEL_ID        # ⚠️ FILL THIS - Mod logs channel ID
welcome: WELCOME_CHANNEL_ID          # ⚠️ FILL THIS - Welcome channel ID
```

> 💡 **Tip:** All role and channel IDs must be valid Discord IDs or the bot will fail to start.

#### **logger.yaml** (Optional Customization)
The logger configuration is pre-configured but can be customized:
```yaml
logger:
  name: "bot"
  log_dir: "logs"

console:
  enabled: true
  level: "INFO"                      # DEBUG, INFO, WARNING, ERROR, CRITICAL

file:
  enabled: true
  level: "DEBUG"
  rotation:
    max_bytes: 10485760              # 10MB
    backup_count: 5
```

---

## 🖼️ Asset Requirements

### ⚠️ Important: Asset Naming Rules

All asset files **must** use the exact names specified below. The bot performs strict validation on startup.

### Required Assets

#### **Coinflip Command** (`assets/commands/coinflip/`)
- `head.png` or `head.jpg` or `head.jpeg` - Coin heads image
- `tail.png` or `tail.jpg` or `tail.jpeg` - Coin tails image

**Rules:**
- Only ONE version of each image (don't have both `head.png` and `head.jpg`)
- Supported formats: PNG, JPG, JPEG

#### **Bot Profile** (`assets/profile/`)
- `banner.png` or `banner.jpg` or `banner.jpeg` - Bot info banner

#### **Welcome System** (`assets/welcome/`)
- `welcome1.png` through `welcomeN.png` (minimum 1 image)
- You can add as many welcome images as you want
- The bot randomly selects one when greeting new members

**Example:**
```
assets/welcome/
├── welcome1.png
├── welcome2.png
├── welcome3.png
├── welcome4.png
└── welcome5.png
```

---

## ▶️ Running the Bot

### Start the Bot
```bash
python main.py
```

### Successful Startup
If configured correctly, you should see:
```
======================================================================
Starting configuration validation...
----------------------------------------------------------------------
bot.yaml is valid
logger.yaml is valid
permissions.yaml is valid
fun.json is valid
help.json is valid

All configuration files validated successfully!
======================================================================
Starting assets validation...
----------------------------------------------------------------------
coinflip assets are valid
profile assets are valid

All asset files validated successfully!
======================================================================
Bot token successfully retrieved.
Starting bot...
----------------------------------------------------------------------
Admin Commands initialized
Basic Commands initialized
Fun Commands initialized
Successfully loaded 3 cog(s)
======================================================================
BOT INFO
----------------------------------------------------------------------
Bot Name        : Fubuki#1234
Bot ID          : 2384782365802734806
Latency         : 45 ms
Guilds Connected: 1
Activity        : Playing | with slash commands
Status          : Online
======================================================================
```

---

## 🛠️ Configuration Guide

### Discord IDs
To get Discord IDs, enable Developer Mode:
1. User Settings → Advanced → Developer Mode (ON)
2. Right-click any user/role/channel → Copy ID

### Role Configuration
- **Admin Roles** - Full access to all moderation commands
- **Mod Roles** - Access to moderation commands (purge, etc.)
- **New Member Roles** - Automatically assigned when users join

### Channel Configuration
- **mod_logs** - Logs all moderation actions (required if using admin commands)
- **welcome** - Sends welcome messages (required if `welcome_messages: true`)

---

## ❗ Troubleshooting

### Bot Won't Start

**Configuration Errors:**
```
Configuration validation FAILED!
  • bot.yaml: Missing required field 'bot.owner_ids'
  • permissions.yaml: Role 'Admin' cannot be empty
```
→ Fill in all required fields in YAML files with valid Discord IDs

**Asset Errors:**
```
Assets validation FAILED!
  • coinflip: Missing required image 'head'
  • profile: Multiple versions of 'banner' found
```
→ Ensure correct asset names and remove duplicates

**Missing Token:**
```
Bot token not found! Please set the TOKEN environment variable.
```
→ Create `.env` file with valid bot token

### Commands Not Working
- Ensure bot has proper permissions in your server
- Check that slash commands are synced (may take up to 1 hour)
- Verify role IDs in `permissions.yaml` match your server roles

### Welcome Messages Not Sending
- Set `welcome_messages: true` in `bot.yaml`
- Configure valid channel ID in `permissions.yaml`
- Ensure bot has permission to send messages in the welcome channel

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

---

## 💬 Support

For issues or questions:
- Open an issue on GitHub
- Contact: [Discord](https://discord.com/users/1369319022918631525)

---

## 🙏 Acknowledgments

Built with:
- [nextcord](https://github.com/nextcord/nextcord) - Discord API wrapper
- [Pillow](https://python-pillow.org/) - Image processing
- [PyYAML](https://pyyaml.org/) - YAML configuration
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment management

---

**Made with ❤️ by Krexilor**
