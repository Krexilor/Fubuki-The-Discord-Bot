#LIBRARIES------------------------------------------------------------------------------------------------------------------------------------------|
import json
import yaml
from pathlib import Path
from typing import Dict, Any

#LOCAL IMPORTS--------------------------------------------------------------------------------------------------------------------------------------|
from core import get_logger

# DECORATORS ---------------------------------------------------------------------------------------------------------------------------------------|
divider = f"=" * 70
sub_divider = f"-" * 70

# PATHS --------------------------------------------------------------------------------------------------------------------------------------------|
CONFIG_DIR = Path(__file__).resolve().parent.parent.parent

# (1) Bot Config Path
BOT_PATH = CONFIG_DIR / "config" / "bot.yaml"

# (2) Logger Config Path
LOGGER_PATH = CONFIG_DIR / "config" / "logger.yaml"

# (3) Permissions Config Path
PERMISSIONS_PATH = CONFIG_DIR / "config" / "permissions.yaml"

# (4) Responses Config Path
FUN_CONFIG_PATH = CONFIG_DIR / "config" / "commands" / "fun.json"
HELP_CONFIG_PATH = CONFIG_DIR / "config" / "commands" / "help.json"

# MAIN ---------------------------------------------------------------------------------------------------------------------------------------------|
class ConfigCheck:
    def __init__(self):
        self.logger = get_logger()
        self.errors = []
        
    # --- Check all configuration files ---
    def check_all(self) -> bool:
        self.logger.info(divider)
        self.logger.info("Starting configuration validation...")
        self.logger.info(sub_divider)
        
        # --- Check YAML files ---
        self._check_bot_config()
        self._check_logger_config()
        self._check_permissions_config()
        
        # --- Check JSON files ---
        self._check_json_file(FUN_CONFIG_PATH, "fun.json")
        self._check_json_file(HELP_CONFIG_PATH, "help.json")
        
        # --- Report results ---
        if self.errors:
            self.logger.error(sub_divider)
            self.logger.error("Configuration validation FAILED!")
            self.logger.error(sub_divider)

            for error in self.errors:
                self.logger.error(f"  • {error}")

            self.logger.error(divider)
            return False
        
        else:
            self.logger.info(" ")
            self.logger.info("All configuration files validated successfully!")
            return True
    
    # --- Check if a file exists ---
    def _check_file_exists(self, path: Path, file_name: str) -> bool:
        if not path.exists():
            self.errors.append(f"{file_name} not found at {path}")
            return False
        return True
    
    # --- Load and parse YAML file ---
    def _load_yaml(self, path: Path, file_name: str) -> Dict[str, Any] | None:
        if not self._check_file_exists(path, file_name):
            return None
        
        try:
            with open(path, 'r', encoding = 'utf-8') as f:
                data = yaml.safe_load(f)
                
            if data is None:
                self.errors.append(f"{file_name} is empty")
                return None
                
            return data
        
        except yaml.YAMLError as e:
            self.errors.append(f"{file_name} has invalid YAML syntax: {e}")
            return None
        
        except Exception as e:
            self.errors.append(f"Error reading {file_name}: {e}")
            return None
    
    # --- Validate bot.yaml configuration ---
    def _check_bot_config(self):
        data = self._load_yaml(BOT_PATH, "bot.yaml")
        if data is None:
            return
        
        # --- Check bot section ---
        if 'bot' not in data:
            self.errors.append("bot.yaml: Missing 'bot' section")
            return
        
        bot = data['bot']
        
        # --- Check required fields ---
        required_fields = ['status', 'activity_type', 'activity_name', 'owner_ids', 'client_id']
        for field in required_fields:
            if field not in bot:
                self.errors.append(f"bot.yaml: Missing required field 'bot.{field}'")
        
        # --- Validate status ---
        if 'status' in bot:
            valid_statuses = ['online', 'idle', 'dnd', 'invisible']
            if bot['status'] not in valid_statuses:
                self.errors.append(f"bot.yaml: Invalid status '{bot['status']}'. Must be one of: {valid_statuses}")
        
        # --- Validate activity_type ---
        if 'activity_type' in bot:
            valid_activities = ['playing', 'watching', 'listening', 'streaming', 'competing']
            if bot['activity_type'] not in valid_activities:
                self.errors.append(f"bot.yaml: Invalid activity_type '{bot['activity_type']}'. Must be one of: {valid_activities}")
        
        # --- Validate owner_ids ---
        if 'owner_ids' in bot:
            if not isinstance(bot['owner_ids'], list):
                self.errors.append("bot.yaml: 'owner_ids' must be a list")

            elif len(bot['owner_ids']) == 0:
                self.errors.append("bot.yaml: 'owner_ids' cannot be empty")
        
        # --- Validate client_id ---
        if 'client_id' in bot:
            if not bot['client_id']:
                self.errors.append("bot.yaml: 'client_id' cannot be empty")
        
        # --- Check features section ---
        if 'features' not in data:
            self.errors.append("bot.yaml: Missing 'features' section")
        
        # --- Check intents section ---
        if 'intents' not in data:
            self.errors.append("bot.yaml: Missing 'intents' section")

        else:
            intents = data['intents']
            if not isinstance(intents, dict) or len(intents) == 0:
                self.errors.append("bot.yaml: 'intents' section cannot be empty")
        
        if not self.errors or not any("bot.yaml" in e for e in self.errors):
            self.logger.info("bot.yaml is valid")
    
    # --- Validate logger.yaml configuration ---
    def _check_logger_config(self):
        data = self._load_yaml(LOGGER_PATH, "logger.yaml")
        if data is None:
            return
        
        # --- Check logger section ---
        if 'logger' not in data:
            self.errors.append("logger.yaml: Missing 'logger' section")
            
        else:
            logger = data['logger']
            if 'name' not in logger or 'log_dir' not in logger:
                self.errors.append("logger.yaml: Missing required fields in 'logger' section")
        
        # --- Check console section ---
        if 'console' not in data:
            self.errors.append("logger.yaml: Missing 'console' section")

        else:
            console = data['console']
            if 'enabled' not in console or 'level' not in console:
                self.errors.append("logger.yaml: Missing required fields in 'console' section")
            
            # --- Validate log level ---
            if 'level' in console:
                valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
                if console['level'] not in valid_levels:
                    self.errors.append(f"logger.yaml: Invalid console log level '{console['level']}'")
        
        # --- Check file section ---
        if 'file' not in data:
            self.errors.append("logger.yaml: Missing 'file' section")

        else:
            file = data['file']
            if 'enabled' not in file or 'level' not in file:
                self.errors.append("logger.yaml: Missing required fields in 'file' section")
            
            # --- Validate log level ---
            if 'level' in file:
                valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
                if file['level'] not in valid_levels:
                    self.errors.append(f"logger.yaml: Invalid file log level '{file['level']}'")
        
        # --- Check format section ---
        if 'format' not in data:
            self.errors.append("logger.yaml: Missing 'format' section")
        
        if not self.errors or not any("logger.yaml" in e for e in self.errors):
            self.logger.info("logger.yaml is valid")
    
    # --- Validate permissions.yaml configuration ---
    def _check_permissions_config(self):
        data = self._load_yaml(PERMISSIONS_PATH, "permissions.yaml")
        if data is None:
            return
        
        # --- Check Roles section ---
        if 'Roles' not in data:
            self.errors.append("permissions.yaml: Missing 'Roles' section")

        else:
            roles = data['Roles']
            required_roles = ['Admin', 'Mods', 'New_Member']
            
            for role in required_roles:
                if role not in roles:
                    self.errors.append(f"permissions.yaml: Missing required role '{role}'")

                elif not isinstance(roles[role], list):
                    self.errors.append(f"permissions.yaml: Role '{role}' must be a list")

                elif len(roles[role]) == 0:
                    self.errors.append(f"permissions.yaml: Role '{role}' cannot be empty")
        
        # --- Check channel IDs ---
        if 'mod_logs' not in data:
            self.errors.append("permissions.yaml: Missing 'mod_logs' channel ID")

        elif not data['mod_logs']:
            self.errors.append("permissions.yaml: 'mod_logs' channel ID cannot be empty")
        
        if 'welcome' not in data:
            self.errors.append("permissions.yaml: Missing 'welcome' channel ID")

        elif not data['welcome']:
            self.errors.append("permissions.yaml: 'welcome' channel ID cannot be empty")
        
        if not self.errors or not any("permissions.yaml" in e for e in self.errors):
            self.logger.info("permissions.yaml is valid")
    
    # --- Check if JSON file exists and is valid ---
    def _check_json_file(self, path: Path, file_name: str):
        if not self._check_file_exists(path, file_name):
            return
        
        try:
            with open(path, 'r', encoding = 'utf-8') as f:
                data = json.load(f)
                
            if data is None:
                self.errors.append(f"{file_name} is empty")
            else:
                self.logger.info(f"{file_name} is valid")
                
        except json.JSONDecodeError as e:
            self.errors.append(f"{file_name} has invalid JSON syntax: {e}")

        except Exception as e:
            self.errors.append(f"Error reading {file_name}: {e}")

# HELPER FUNCTION TO RUN VALIDATION ----------------------------------------------------------------------------------------------------------------|
def validate_configs() -> bool:
    checker = ConfigCheck()
    return checker.check_all()
