# LIBRARIES ------------------------------------------------------------------------------------------------------------------------------------|
import os
import re
import sys
import yaml
import logging
from pathlib import Path
from colorama import Fore, Style
from logging.handlers import RotatingFileHandler

# PATHS ----------------------------------------------------------------------------------------------------------------------------------------|
LOGGER_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = LOGGER_DIR / "config" / "logger.yaml"

# MAIN -----------------------------------------------------------------------------------------------------------------------------------------|
# (1) Custom formatter for console output.
class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt: str, datefmt: str, colors: dict, show_traceback: bool):
        super().__init__(fmt = fmt, datefmt = datefmt)
        self.colors = colors
        self.show_traceback = show_traceback

    def format(self, record):
        # --- Create a deep copy to avoid modifying the original record ---
        record_copy = logging.makeLogRecord(record.__dict__.copy())
        
        # --- Apply color only to the copy ---
        color = self.colors.get(record_copy.levelname.lower(), "")
        record_copy.levelname = f"{color}{record_copy.levelname}{Style.RESET_ALL}"

        log_msg = super().format(record_copy)

        if record_copy.exc_info and self.show_traceback:
            log_msg += f"\n{self.formatException(record_copy.exc_info)}"

        return log_msg

# (2) Custom formatter for file output (NO COLORS).
class FileFormatter(logging.Formatter):
    # --- Regex pattern to strip ANSI escape codes ---
    ANSI_ESCAPE_PATTERN = re.compile(r'\x1b\[[0-9;]*m')
    
    def __init__(self, fmt: str, datefmt: str, show_traceback: bool):
        super().__init__(fmt = fmt, datefmt = datefmt)
        self.show_traceback = show_traceback

    def format(self, record):
        # --- Create a copy to avoid modifying the original record ---
        record_copy = logging.makeLogRecord(record.__dict__.copy())
        
        # --- Strip any ANSI codes from the message itself ---
        if hasattr(record_copy, 'msg') and isinstance(record_copy.msg, str):
            record_copy.msg = self._strip_ansi_codes(record_copy.msg)
        
        # --- Ensure levelname has no color codes ---
        if hasattr(record_copy, 'levelname'):
            record_copy.levelname = self._strip_ansi_codes(str(record_copy.levelname))
        
        # --- Format the log message ---
        log_msg = super().format(record_copy)
        
        # --- Strip any remaining ANSI codes from the final output ---
        log_msg = self._strip_ansi_codes(log_msg)

        if record_copy.exc_info and self.show_traceback:
            exception_text = self.formatException(record_copy.exc_info)
            exception_text = self._strip_ansi_codes(exception_text)
            log_msg += f"\n{exception_text}"

        return log_msg
    
    def _strip_ansi_codes(self, text: str) -> str:
        """Remove all ANSI escape codes from text."""
        return self.ANSI_ESCAPE_PATTERN.sub('', text)

# (3) Main logger class.
class BotLogger:
    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config = self._load_config(config_path)
        self.logger = None
        self._setup_logger()

    # --- Load logger configuration from YAML file ---
    def _load_config(self, config_path: Path) -> dict:
        try:
            with config_path.open("r", encoding = "utf-8") as f:
                return yaml.safe_load(f)
            
        except FileNotFoundError:
            raise RuntimeError(f"Logger config not found: {config_path}")

    # --- Setup the logger with handlers ---
    def _setup_logger(self):
        cfg = self.config

        self.logger = logging.getLogger(cfg["logger"]["name"])
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        self.logger.propagate = cfg["advanced"]["propagate"]

        if cfg["console"]["enabled"]:
            self._setup_console_handler()

        if cfg["file"]["enabled"]:
            self._setup_file_handler()

    # --- Setup console handler ---
    def _setup_console_handler(self):
        cfg = self.config

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, cfg["console"]["level"]))

        formatter = ColoredFormatter(
            fmt = cfg["format"]["console"],
            datefmt = cfg["format"]["date_format"],
            colors = self._resolve_colors(cfg["console"]["colors"]),
            show_traceback = cfg["error_handling"]["show_traceback_console"],
        )

        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    # --- Setup rotating file handler ---
    def _setup_file_handler(self):
        cfg = self.config

        os.makedirs(cfg["logger"]["log_dir"], exist_ok=True)

        file_handler = RotatingFileHandler(
            filename = os.path.join(cfg["logger"]["log_dir"], "bot.log"),
            maxBytes = cfg["file"]["rotation"]["max_bytes"],
            backupCount = cfg["file"]["rotation"]["backup_count"],
            encoding = cfg["advanced"]["encoding"],
        )

        file_handler.setLevel(getattr(logging, cfg["file"]["level"]))

        # --- Use FileFormatter (no colors) for file output ---
        formatter = FileFormatter(
            fmt = cfg["format"]["file"],
            datefmt = cfg["format"]["date_format"],
            show_traceback = cfg["error_handling"]["show_traceback_file"],
        )

        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    # --- Resolve color names from YAML to colorama ---
    def _resolve_colors(self, colors: dict) -> dict:
        color_map = {
            "black": Fore.BLACK,
            "red": Fore.RED,
            "green": Fore.GREEN,
            "yellow": Fore.YELLOW,
            "blue": Fore.BLUE,
            "magenta": Fore.MAGENTA,
            "cyan": Fore.CYAN,
            "white": Fore.WHITE,
        }
        return {
            level: color_map.get(color_name.split(",")[0], "")
            for level, color_name in colors.items()
        }

# GLOBAL INSTANCE --------------------------------------------------------------------------------------------------------------------------------|
_logger_instance = None

def get_logger() -> logging.Logger:
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = BotLogger().logger

    return _logger_instance
