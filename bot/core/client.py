# LIBRARIES -----------------------------------------------------------------------------------------------------------------------------------------|
import sys
import yaml
import nextcord
import traceback
from pathlib import Path
from datetime import datetime
from nextcord.ext import commands

# LOCAL IMPORTS -------------------------------------------------------------------------------------------------------------------------------------|
from .logger import get_logger
from events import OnReadyEvent, OnMemberJoinEvent

# PATHS -------------------------------------------------------------------------------------------------------------------------------------------|
# (1) Config Files Path
CONFIG_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = CONFIG_DIR / "config" / "bot.yaml"

# (2) Command Files Path
COMMANDS_DIR = Path(__file__).resolve().parent.parent
COMMANDS_PATH = COMMANDS_DIR / "commands"

# MAIN ----------------------------------------------------------------------------------------------------------------------------------------------|
class BotClient(commands.Bot):
    def __init__(self):
        self.logger = get_logger()
        self.config = self._load_config()
        self.start_time = datetime.now()

        intents = self._build_intents()

        super().__init__(
            command_prefix = "/",
            intents = intents,
            owner_ids = set(map(int, self.config["bot"]["owner_ids"]))
        )
        self.add_listener(OnReadyEvent(self).handle, "on_ready")
        self.add_listener(OnMemberJoinEvent(self).handle, "on_member_join")
        self._load_cogs()

    # --- Load Bot Config ---
    def _load_config(self) -> dict:
        try:
            with CONFIG_PATH.open("r", encoding = "utf-8") as f:
                return yaml.safe_load(f)
            
        except FileNotFoundError:
            self.logger.critical(f"Bot config not found: {CONFIG_PATH}")
            raise RuntimeError("Missing bot.yaml")

    # --- Discord Intents ---
    def _build_intents(self) -> nextcord.Intents:
        cfg = self.config["intents"]
        intents = nextcord.Intents.none()

        for name, enabled in cfg.items():
            if hasattr(intents, name):
                setattr(intents, name, enabled)

        return intents
    
    # --- Load all cogs from commands directory ---
    def _load_cogs(self):
        if not COMMANDS_PATH.exists():
            self.logger.warning(f"Commands directory not found: {COMMANDS_PATH}")
            return

        # --- Add project root to sys.path if not already there ---
        project_root = str(CONFIG_DIR)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        cog_count = 0
        for file_path in COMMANDS_PATH.rglob("*.py"):
            if file_path.name.startswith("_"):
                continue

            try:
                # --- Get relative path from project root (CONFIG_DIR) ---
                relative_path = file_path.relative_to(CONFIG_DIR)
                parts = relative_path.with_suffix("").parts
                module_path = ".".join(parts)

                self.load_extension(module_path)
                cog_count += 1

            except Exception as e:
                self.logger.error(f"Failed to load cog from {file_path.name}: {e}")
                self.logger.error(traceback.format_exc())

        self.logger.info(f"Successfully loaded {cog_count} cog(s)")
    
    # --- Bot Activity ---
    def build_activity(self):
        bot_cfg = self.config["bot"]

        activity_type = bot_cfg["activity_type"].lower()
        name = bot_cfg["activity_name"]

        if activity_type == "playing":
            return nextcord.Game(name=name)

        if activity_type == "listening":
            return nextcord.Activity(
                type = nextcord.ActivityType.listening,
                name = name
            )

        if activity_type == "watching":
            return nextcord.Activity(
                type = nextcord.ActivityType.watching,
                name = name
            )

        if activity_type == "competing":
            return nextcord.Activity(
                type = nextcord.ActivityType.competing,
                name = name
            )

        if activity_type == "streaming":
            return nextcord.Streaming(
                name = name,
                url = bot_cfg["streaming_url"]
            )

        return None
    
    # --- Bot Status ---
    def build_status(self):
        status = self.config["bot"]["status"].lower()
        return getattr(nextcord.Status, status, nextcord.Status.online)
