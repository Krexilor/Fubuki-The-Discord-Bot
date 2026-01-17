# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
import io
import json
import random
import aiohttp
import nextcord
from pathlib import Path
from nextcord.ext import commands
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw
from nextcord import slash_command, Interaction, SlashOption, Embed, Color

# LOCAL IMPORTS ------------------------------------------------------------------------------------------------------------------------------------|
from core import get_logger

# DECORATORS ---------------------------------------------------------------------------------------------------------------------------------------|
divider = f"=" * 70
sub_divider = f"-" * 70

# PATHS --------------------------------------------------------------------------------------------------------------------------------------------|
# (1) Fun Commands Input Path
FUN_DIR = Path(__file__).resolve().parent.parent.parent
FUN_PATH = FUN_DIR / "config" / "commands" / "fun.json"

# (2) CoinFlip Command Assets Path
COIN_FLIP_DIR = Path(__file__).resolve().parent.parent.parent
COIN_FLIP_PATH = COIN_FLIP_DIR / "assets" / "commands" / "coinflip"

# CONSTANTS ----------------------------------------------------------------------------------------------------------------------------------------|
MAX_TEXT_LENGTH = 500        # Maximum character limit for text commands

MAX_RECENT = 20              # How many recent messages to avoid repeating

# MAIN ---------------------------------------------------------------------------------------------------------------------------------------------|
class FunCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger()
        self.logger.info("Fun Commands initialized")

        # --- Compliemnt and Insult commands ---
        with open(FUN_PATH, "r", encoding = "utf-8") as f:
            self.fun_data = json.load(f)

        self.recent_compliments = []
        self.recent_insults = []

    # --- Helper function for compliment/insult commands ---
    def _get_random_line(self, category: str, recent_list: list) -> str:
        items = list(self.fun_data[category].values())

        available = [i for i in items if i not in recent_list]

        if not available:
            recent_list.clear()
            available = items

        choice = random.choice(available)
        recent_list.append(choice)

        if len(recent_list) > MAX_RECENT:
            recent_list.pop(0)

        return choice
    
    # --- Helper function for avatar command ---
    async def _apply_filter(self, image_url: str, filter_name: str) -> io.BytesIO:
        # --- Downlaod the image ---
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    raise Exception("Failed to download image")
                
                image_data = await resp.read()

        # --- Open image with PIL ---
        img = Image.open(io.BytesIO(image_data))

        # --- Convert to RGB if necessary (for PNG with transparency) ---
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')

            background.paste(img, mask = img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # --- Apply the selected filter ---
        # (1) Applies a basic blur effect
        if filter_name == "blur":
            img = img.filter(ImageFilter.BLUR)

        # (2) Outlines edges in the image
        elif filter_name == "contour":
            img = img.filter(ImageFilter.CONTOUR)

        # (3) Enhance fine details
        elif filter_name == "detail":
            img = img.filter(ImageFilter.DETAIL)
    
        # (4) Sharpens the edges moderately
        elif filter_name == "edge_enhance":
            img = img.filter(ImageFilter.EDGE_ENHANCE)
    
        # (5) Aggresive edge sharpening
        elif filter_name == "edge_enhance_more":
            img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    
        # (6) Create a 3D raised/curved effect
        elif filter_name == "emboss":
            img = img.filter(ImageFilter.EMBOSS)
    
        # (7) Detects and highlights all edges
        elif filter_name == "find_edges":
            img = img.filter(ImageFilter.FIND_EDGES)
    
        # (8) Makes the entire image crisper
        elif filter_name == "sharpen":
            img = img.filter(ImageFilter.SHARPEN)
    
        # (9) Light smoothing effect
        elif filter_name == "smooth":
            img = img.filter(ImageFilter.SMOOTH)
    
        # (10) Stronger smoothing
        elif filter_name == "smooth_more":
            img = img.filter(ImageFilter.SMOOTH_MORE)
    
        # (11) Removes all colors
        elif filter_name == "grayscale":
            img = img.convert('L').convert('RGB')

        # (12) Vintage brown-toned effect
        elif filter_name == "sepia":
            img = img.convert('L')
            sepia_img = Image.new('RGB', img.size)
            pixels = sepia_img.load()
            original = img.load()
        
            for y in range(img.size[1]):
                for x in range(img.size[0]):
                    gray = original[x, y]
                    pixels[x, y] = (gray, int(gray * 0.95), int(gray * 0.82))
            img = sepia_img
    
        # (13) Reverses all colors
        elif filter_name == "invert":
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            img = ImageOps.invert(img)
    
        # (14) Increases overall brightness by 50%
        elif filter_name == "brighten":
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.5)
    
        # (15) Reduces brightness by 40%
        elif filter_name == "darken":
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.6)
    
        # (16) Doubles contrast
        elif filter_name == "high_contrast":
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
    
        # (17) Reduces contrast by 50%
        elif filter_name == "low_contrast":
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(0.5)
    
        # (18) Doubles Color intensity
        elif filter_name == "saturate":
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(2.0)
    
        # (19) Refuces color intensity by 70%
        elif filter_name == "desaturate":
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(0.3)

        # (20) Give the avatar an artistic touch
        elif filter_name == "pro_enhance":
            # --- Resize for consistency ---
            img = img.resize((512, 512), Image.LANCZOS)

            # --- Auto contrast with safety cutoff ---
            if img.mode != "RGB":
                img = img.convert("RGB")

            # --- Smart contrast & exposure ---
            img = ImageOps.autocontrast(img, cutoff = 1)

            # --- Macro clarity ---
            img = img.filter(ImageFilter.UnsharpMask(radius = 1.6, percent = 110, threshold = 4))

            # --- Gentle brightness & contrast ---
            img = ImageEnhance.Brightness(img).enhance(1.04)
            img = ImageEnhance.Contrast(img).enhance(1.12)

            # --- Skin-sade color boost ---
            img = ImageEnhance.Color(img).enhance(1.15)

            # --- Potrait look ---
            img = img.filter(ImageFilter.SMOOTH)

            # --- Soft cinematic vignette ---
            width, height = img.size
            vignette = Image.new("L", (width, height), 255)
            draw = ImageDraw.Draw(vignette)

            draw.ellipse((-width * 0.15, -height * 0.15, width * 1.15, height * 1.15), fill = 0)
            vignette = vignette.filter(ImageFilter.GaussianBlur(90))

            black = Image.new("RGB", img.size, (0, 0, 0))
            img = Image.composite(black, img, vignette)

        # Save to BytesIO
        output = io.BytesIO()
        img.save(output, format = 'PNG')
        output.seek(0)

        return output

    # (1) Mock Command
    @slash_command(
        name = "mock",
        description = "Converts the provided text into alternating upper/lower case letters"
    )
    async def mock(
        self,
        interaction: Interaction,
        text: str = SlashOption(
            name = "text",
            description = "Text to mock",
            required = True
        )
    ):
        try:
            # --- Check text length ---
            if len(text) > MAX_TEXT_LENGTH:
                embed = Embed(
                    title = "Text Too Long",
                    description = f"Please provide text with **{MAX_TEXT_LENGTH}** characters or less.",
                    color = Color.red()
                )
                await interaction.response.send_message(embed = embed, ephemeral = True)
                return
            
            # --- Create mocking text ---
            mocked_text = ''.join([char.upper() if i % 2 == 0 else char.lower() for i, char in enumerate(text)])

            # --- Building embed ---
            embed = Embed(
                title = "Mocked Text",
                description = mocked_text,
                color = Color.magenta()
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
            self.logger.error(f"Error in mock command: {e}")
            self.logger.error(sub_divider)

    # (2) Reverse Command
    @slash_command(
        name = "reverse",
        description = "Reverses the order of characters in the provided text"
    )
    async def reverse(
        self,
        interaction: Interaction,
        text: str = SlashOption(
            name = "reverse",
            description = "Text to reverse",
            required = True
        )
    ):
        try:
            # --- Check text lenght ---
            if len(text) > MAX_TEXT_LENGTH:
                embed = Embed(
                    title = "Text Too Long",
                    description = f"Please provide text with **{MAX_TEXT_LENGTH}** characters or less.",
                    color = Color.red()
                )
                await interaction.response.send_message(embed = embed, ephemeral = True)
                return
            
            # --- Reverse the text ---
            reversed_text = text[::-1]

            # --- Building embed ---
            embed = Embed(
                title = "Reversed Text",
                description = reversed_text,
                color = Color.magenta()
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
            self.logger.error(f"Error in reverse command: {e}")
            self.logger.error(sub_divider)

    # (3) Emojify Command
    @slash_command(
        name = "emojify",
        description = "Converts each letter in the text into it's corresponding emoji representation"
    )
    async def emojify(
        self,
        interaction: Interaction,
        text: str = SlashOption(
            name = "text",
            description = "Text to emojify",
            required = True
        )
    ):
        try:
            # --- Check text lenght ---
            if len(text) > MAX_TEXT_LENGTH:
                embed = Embed(
                    title = "Text Too Long",
                    description = f"Please provide text with **{MAX_TEXT_LENGTH}** characters or less.",
                    color = Color.red()
                )
                await interaction.response.send_message(embed = embed, ephemeral = True)
                return
            
            # --- Convert to emojis ---
            letter_emojis = {
                'a': '🇦', 'b': '🇧', 'c': '🇨', 'd': '🇩', 'e': '🇪',
                'f': '🇫', 'g': '🇬', 'h': '🇭', 'i': '🇮', 'j': '🇯',
                'k': '🇰', 'l': '🇱', 'm': '🇲', 'n': '🇳', 'o': '🇴',
                'p': '🇵', 'q': '🇶', 'r': '🇷', 's': '🇸', 't': '🇹',
                'u': '🇺', 'v': '🇻', 'w': '🇼', 'x': '🇽', 'y': '🇾', 'z': '🇿'
            }
            
            digit_emojis = {
                '0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣',
                '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣'
            }
            
            emoji_text = ""
            for char in text.lower():
                if char.isalpha():
                    emoji_text += letter_emojis.get(char, char) + " "
                elif char.isdigit():
                    emoji_text += digit_emojis.get(char, char) + " "
                elif char == ' ':
                    emoji_text += "  "
                else:
                    emoji_text += char + " "

            # --- Check if result is too long ---
            if len(emoji_text) > 2000:
                embed = Embed(
                    title = "Result Too Long",
                    description = "The emojified text exceed Discord's message limit. Please user shorter text.",
                    color = Color.red()
                )
                await interaction.response.send_message(embed = embed, ephemeral = True)
                return
            
            # --- Building embed ---
            embed = Embed(
                title = "Emojified Text",
                description = emoji_text,
                color = Color.magenta()
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
            self.logger.error(f"Error in emojify command: {e}")
            self.logger.error(sub_divider)

    # (4) Rate Command
    @slash_command(
        name = "rate",
        description = "Randomly rate a provided word, phrase, or object on a scale or 1-10"
    )
    async def rate(
        self,
        interaction: Interaction,
        text: str = SlashOption(
            name = "text",
            description = "What do you to rate?",
            required = True
        )
    ):
        try:
            # --- Check text lenght ---
            if len(text) > MAX_TEXT_LENGTH:
                embed = Embed(
                    title = "Text Too Long",
                    description = f"Please provide text with **{MAX_TEXT_LENGTH}** characters or less.",
                    color = Color.red()
                )
                await interaction.response.send_message(embed = embed, ephemeral = True)
                return
            
            # --- Generate consistent rating based on hash ---
            seed = hash(text.lower())
            random.seed(seed)
            rating = random.randint(1, 10)

            # --- Create rating bar ---
            filled_stars = "⭐" * rating
            empty_stars = "☆" * (10 - rating)
            rating_bar = filled_stars + empty_stars

            # --- Determine rating message ---
            if rating <= 3:
                message = "Not great... 😕"

            elif rating <= 5:
                message = "Pretty average! 😐"

            elif rating <= 7:
                message = "Not bad! 👍"

            elif rating <= 9:
                message = "Really good! 😊"

            else:
                message = "Absolutely amazing! 🎉"

            # --- Buidling embed ---
            embed = Embed(
                title = "Rating",
                description = f'''
                I'd rate **{text}** a **{rating}/10**!

                {rating_bar}
                {message}
                ''',
                color = Color.magenta()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)

        except Exception as e:
            # --- Error Handling ---
            embed = Embed(
                title = "Error",
                description = "An error occrurred while processing the command. Please try again later.",
                color = Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)
            self.logger.error(sub_divider)
            self.logger.error(f"Error in rate command: {e}")
            self.logger.error(sub_divider)

    # (5) Choose Command
    @slash_command(
        name = "choose",
        description = "Selects one option from user-provided choices"
    )
    async def choose(
        self,
        interaction: Interaction,
        choice1: str = SlashOption(
            name = "choice1",
            description = "The first option",
            required = True
        ),
        choice2: str = SlashOption(
            name = "choice2",
            description = "The second option",
            required = True
        ),
        choice3: str = SlashOption(
            name = "choice3",
            description = "The third option",
            required = False
        ),
        choice4: str = SlashOption(
            name = "choice4",
            description = "The fourth option",
            required = False
        ),
        choice5: str = SlashOption(
            name = "choice5",
            description = "The fifth option",
            required = False
        )
    ):
        try:
            # --- Collect all choices ---
            choices = [choice1, choice2]
            if choice3:
                choices.append(choice3)
            
            if choice4:
                choices.append(choice4)

            if choice5:
                choices.append(choice5)

            # --- Randomly select one ---
            selected = random.choice(choices)

            # --- Add all choices to embed ---
            choices_text = " ".join([f", {choice}" for choice in choices])

            # --- Building embed ---
            embed = Embed(
                title = "Choice Made",
                description = f'''
                I choose: **{selected}**

                Available Choices: {choices_text}
                ''',
                color = Color.magenta()
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
            self.logger.error(f"Error in choose command: {e}")
            self.logger.error(sub_divider)

    # (6) Ship Command
    @slash_command(
        name = "ship",
        description = "Compatibility percentage between two users"
    )
    async def ship(
        self,
        interaction: Interaction,
        user1: nextcord.Member = SlashOption(
            name = "user1",
            description = "The first user",
            required = True
        ),
        user2: nextcord.Member = SlashOption(
            name = "user2",
            description = "The second user",
            required = True
        )
    ):
        try:
            # --- Check if same user ---
            if user1.id == user2.id:
                embed = Embed(
                    title = "Self Love",
                    description = f'''
                    {user1.mention} loves themselves **100%**! 💯

                    Self-love is important! 💖
                    ''',
                    color = Color.magenta()
                )
                await interaction.response.send_message(embed = embed)
                return
            
            # --- Calculate compatibility based on multiple factors ---
            # Factor 1: User ID combination (consistent for same pair)
            id_seed = min(user1.id, user2.id) + max(user1.id, user2.id)

            # Factor 2: Account age similarity (if both have joined discord around same time)
            age_diff = abs((user1.created_at - user2.created_at).days)
            age_bonus = max(0, 10 - (age_diff // 365))

            # Factor 3: Server join time similarity
            join_diff = abs((user1.joined_at - user2.joined_at).days) if user1.joined_at and user2.joined_at else 0
            join_bonus = max(0, 5 - (join_diff // 30))

            # Factor 4: Role similarity (number of shared roles)
            user1_roles = set(role.id for role in user1.roles)
            user2_roles = set(role.id for role in user2.roles)
            shared_roles = len(user1_roles.intersection(user2_roles))
            role_bonus = min(10, shared_roles * 2)

            # --- Generate base percentage from ID seed ---
            random.seed(id_seed)
            base_percentage = random.randint(1, 75)

            # --- Calculate final percentage ---
            final_percentage = min(100, base_percentage + age_bonus + join_bonus + role_bonus)

            # --- Create ship name ---
            name1 = user1.display_name[:len(user1_roles) // 2]
            name2 = user2.display_name[len(user2.display_name) // 2:]
            ship_name = name1 + name2

            # --- Create heart bar ---
            hearts_filled = final_percentage // 10
            hearts = "💖" * hearts_filled + "🤍" * (10 - hearts_filled)

            # --- Determine relationship message ---
            # --- Determine relationship message ---
            if final_percentage < 20:
                message = "Maybe just friends... 😅"

            elif final_percentage < 40:
                message = "There might be something there! 🤔"

            elif final_percentage < 60:
                message = "Pretty good compatibility! 😊"

            elif final_percentage < 80:
                message = "Great match! 💕"

            else:
                message = "Perfect match! 💞✨"

            # --- Building embed ---
            embed = Embed(
                title = f"💝 {user1.display_name} X {user2.display_name}",
                description = f'''
                • **Ship Name:** {ship_name}
                
                {hearts}

                • **Compatibility:** {final_percentage}%
                {message}

                __**Breakdown**__
                • Base Match: {base_percentage}%
                • Account Age bonus: +{age_bonus}%
                • Join Time Bonus: +{join_bonus}%
                • Shared Roles Bonus: +{role_bonus}%
                ''',
                color = Color.magenta()
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
            self.logger.error(f"Error in ship command: {e}")
            self.logger.error(sub_divider)

    # (7) Compliment Command
    @slash_command(
        name = "compliment",
        description = "Give someone a random compliment"
    )
    async def compliment(
        self,
        interaction: Interaction,
        user: nextcord.Member = SlashOption(
            name = "user",
            description = "Who deserves a compliment?",
            required = True
        )
    ):
        try:
            # --- Get random compliment ---
            compliment = self._get_random_line("compliment", self.recent_compliments)

            # --- Building embed ---
            embed = Embed(
                title = f"{interaction.user.display_name} complimented {user.display_name}",
                description = compliment,
                color = Color.magenta()
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
            self.logger.error(f"Error in compliment command: {e}")
            self.logger.error(sub_divider)

    # (8) Insult Command
    @slash_command(
        name = "insult",
        description = "Light-heartedly insult someone"
    )
    async def insult(
        self,
        interaction: Interaction,
        user: nextcord.Member = SlashOption(
            name = "user",
            description = "Who is getting roasted?",
            required = True
        )
    ):
        try:
            # --- Get random insult ---
            insult = self._get_random_line("insult", self.recent_insults)

            # --- Building embed ---
            embed = Embed(
                title = f"{interaction.user.display_name} insulted {user.display_name}",
                description = insult,
                color = Color.magenta()
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
            self.logger.error(f"Error in insult command: {e}")
            self.logger.error(sub_divider)

    # (9) CoinFlip command
    @slash_command(
        name = "coinflip",
        description = "Flips a coin"
    )
    async def coinflip(
        self,
        interaction: Interaction
    ):
        try:
            # --- Supported extensions ---
            valid_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

            # --- Find head and tail images in the directory ---
            head_files = [f for f in COIN_FLIP_PATH.iterdir() if f.stem.lower() == "head" and f.suffix.lower() in valid_extensions]
            tail_files = [f for f in COIN_FLIP_PATH.iterdir() if f.stem.lower() == "tail" and f.suffix.lower() in valid_extensions]

            # --- Check if bot images exists ---
            if not head_files or not tail_files:
                self.logger.error(f"Missing coin images in {COIN_FLIP_PATH}. Need both 'head' and 'tail' with valid extensions.")
                raise FileNotFoundError
            
            # --- Randomly select side ---
            result_side = random.choice(["Heads", "Tails"])
            chosen_file = head_files[0] if result_side == "Heads" else tail_files[0]

            # --- Create file  ---
            file = nextcord.File(chosen_file, filename = f"coin_{result_side.lower()}{chosen_file.suffix}")

            # --- Building embed ---
            embed = Embed(
                title = f"{result_side}",
                color = Color.magenta()
            )
            embed.set_image(url = f"attachment://{file.filename}")
            await interaction.response.send_message(embed = embed, file = file)

        except Exception as e:
            # --- Error Handling ---
            embed = Embed(
                title = "Error",
                description = "An error occrurred while processing the command. Please try again later.",
                color = Color.red()
            )
            await interaction.response.send_message(embed = embed, ephemeral = True)
            self.logger.error(sub_divider)
            self.logger.error(f"Error in coinflip command: {e}")
            self.logger.error(sub_divider)

    # (10) Avatar Command
    @slash_command(
        name = "avatar",
        description = "Display a user's avatar with optional filters"
    )
    async def avatar(
        self,
        interaction: Interaction,
        user: nextcord.Member = SlashOption(
            name = "user",
            description = "The user whose avatar you want to see",
            required = True
        ),
        effect: str = SlashOption(
            name = "effect",
            description = "Apply a filter to the avatar",
            required = False,
            choices = {
                "Blur": "blur",
                "Contour": "contour",
                "Detail": "detail",
                "Edge Enhance": "edge_enhance",
                "Edge Enhance More": "edge_enhance_more",
                "Emboss": "emboss",
                "Find Edges": "find_edges",
                "Sharpen": "sharpen",
                "Smooth": "smooth",
                "Smooth More": "smooth_more",
                "Grayscale": "grayscale",
                "Sepia": "sepia",
                "Invert": "invert",
                "Brighten": "brighten",
                "Darken": "darken",
                "High Contrast": "high_contrast",
                "Low Contrast": "low_contrast",
                "Saturate": "saturate",
                "Desaturate": "desaturate",
                "Pro Enhance": "pro_enhance"
            }
        )
    ):
        try:
            # --- Defer response as image processing might take time ---
            await interaction.response.defer()

            # --- Get user's avatar URL ---
            avatar_url = user.display_avatar.url

            # --- If no filter, just show the avatar ---
            if not effect:
                embed = Embed(
                    title = f"{user.display_name}'s Avatar",
                    color = Color.magenta()
                )
                embed.set_image(url = avatar_url)
                await interaction.followup.send(embed = embed)

            else:
                # --- Apply filter to the avatar ---
                filtered_image = await self._apply_filter(avatar_url, effect)

                # --- Create file from BytesIO ---
                file = nextcord.File(filtered_image, filename = f"avatar_{effect}.png")

                # --- Building embed ---
                embed = Embed(
                    title = f"{user.display_name}'s Avatar",
                    description = f"Filter: **{effect.replace('_', ' ').title()}**",
                    color = Color.magenta()
                )
                embed.set_image(url = f"attachment://avatar_{effect}.png")
                await interaction.followup.send(embed = embed, file = file)

        except Exception as e:
            # --- Error Handling ---
            embed = Embed(
                title = "Error",
                description = "An error occrurred while processing the command. Please try again later.",
                color = Color.red()
            )
            await interaction.followup.send(embed = embed, ephemeral = True)
            self.logger.error(sub_divider)
            self.logger.error(f"Error in avatar command: {e}")
            self.logger.error(sub_divider)

# SETUP FUNCTION -----------------------------------------------------------------------------------------------------------------------------------|
def setup(bot: commands.Bot):
    bot.add_cog(FunCommands(bot))
