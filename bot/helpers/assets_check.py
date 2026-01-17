# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
from pathlib import Path

# LOCAL IMPORTS ------------------------------------------------------------------------------------------------------------------------------------|
from core import get_logger

# DECORATORS ---------------------------------------------------------------------------------------------------------------------------------------|
divider = f"=" * 70
sub_divider = f"-" * 70

# PATHS --------------------------------------------------------------------------------------------------------------------------------------------|
ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"

# (1) CoinFlip assets
COINFLIP_ASSETS_PATH = ASSETS_DIR / "commands" / "coinflip"

# (2) Profile assets
PROFILE_ASSETS_PATH = ASSETS_DIR / "profile"

# MAIN ---------------------------------------------------------------------------------------------------------------------------------------------|
class AssetsCheck:
    def __init__(self):
        self.logger = get_logger()
        self.errors = []
        self.warnings = []
        
    # --- Check all asset files ---
    def check_all(self) -> bool:
        self.logger.info(divider)
        self.logger.info("Starting assets validation...")
        self.logger.info(sub_divider)
        
        # --- Check asset directories ---
        self._check_coinflip_assets()
        self._check_profile_assets()
        
        # --- Report results ---
        if self.errors:
            self.logger.error(sub_divider)
            self.logger.error("Assets validation FAILED!")
            self.logger.error(sub_divider)
            
            for error in self.errors:
                self.logger.error(f"  • {error}")
            
            self.logger.error(divider)
            return False
        
        else:
            self.logger.info("\nAll asset files validated successfully!")
            return True
    
    # --- Check if directory exists ---
    def _check_directory_exists(self, path: Path, dir_name: str) -> bool:
        if not path.exists():
            self.errors.append(f"Directory '{dir_name}' not found at {path}")
            return False
        
        if not path.is_dir():
            self.errors.append(f"'{dir_name}' at {path} is not a directory")
            return False
        
        return True
    
    # --- Check if required image exists with allowed extensions ---
    def _check_image_exists(self, directory: Path, image_name: str, dir_name: str) -> bool:
        allowed_extensions = ['.png', '.jpg', '.jpeg']
        
        found_files = []
        for ext in allowed_extensions:
            image_path = directory / f"{image_name}{ext}"
            if image_path.exists():
                found_files.append(image_path)
        
        if len(found_files) == 0:
            self.errors.append(
                f"{dir_name}: Missing required image '{image_name}' "
                f"(allowed extensions: {', '.join(allowed_extensions)})"
            )
            return False
        
        elif len(found_files) > 1:
            self.warnings.append(
                f"{dir_name}: Multiple versions of '{image_name}' found: "
                f"{[f.name for f in found_files]}. Only one should exist."
            )
            self.logger.warning(
                f"{dir_name}: Multiple versions of '{image_name}' found: "
                f"{[f.name for f in found_files]}"
            )
        
        return True
    
    # --- Check for invalid files in directory ---
    def _check_invalid_files(self, directory: Path, required_names: list, dir_name: str):
        allowed_extensions = {'.png', '.jpg', '.jpeg'}
        
        for file in directory.iterdir():
            if file.is_file():
                # --- Get file name without extension ---
                file_stem = file.stem
                file_ext = file.suffix.lower()
                
                # --- Check if file has invalid extension ---
                if file_ext not in allowed_extensions:
                    self.errors.append(
                        f"{dir_name}: Invalid file '{file.name}'. "
                        f"Only {', '.join(allowed_extensions)} extensions are allowed"
                    )
                
                # --- Check if file name is not in required names ---
                elif file_stem not in required_names:
                    self.errors.append(
                        f"{dir_name}: Unexpected file '{file.name}'. "
                        f"Only allowed file names: {', '.join(required_names)}"
                    )
    
    # --- Validate coinflip assets ---
    def _check_coinflip_assets(self):
        if not self._check_directory_exists(COINFLIP_ASSETS_PATH, "coinflip"):
            return
        
        required_images = ['head', 'tail']
        
        # --- Check for required images ---
        for image_name in required_images:
            self._check_image_exists(COINFLIP_ASSETS_PATH, image_name, "coinflip")
        
        # --- Check for invalid files ---
        self._check_invalid_files(COINFLIP_ASSETS_PATH, required_images, "coinflip")
        
        if not self.errors or not any("coinflip" in e for e in self.errors):
            self.logger.info("coinflip assets are valid")
    
    # --- Validate profile assets ---
    def _check_profile_assets(self):
        if not self._check_directory_exists(PROFILE_ASSETS_PATH, "profile"):
            return
        
        required_images = ['banner']
        
        # --- Check for required images ---
        for image_name in required_images:
            self._check_image_exists(PROFILE_ASSETS_PATH, image_name, "profile")
        
        # --- Check for invalid files ---
        self._check_invalid_files(PROFILE_ASSETS_PATH, required_images, "profile")
        
        if not self.errors or not any("profile" in e for e in self.errors):
            self.logger.info("profile assets are valid")

# HELPER FUNCTION TO RUN VALIDATION ----------------------------------------------------------------------------------------------------------------|
def validate_assets() -> bool:
    checker = AssetsCheck()
    return checker.check_all()
