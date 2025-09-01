import os
import json
import time
import aiohttp
import random
import asyncio
import requests
import logging
import threading
import xml.etree.ElementTree as ET
import aiogram.types as types
from typing import Dict, Any
from http.server import BaseHTTPRequestHandler, HTTPServer

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.enums import ParseMode, ChatAction
from aiogram.types import (
    Message,
    BotCommand,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaAnimation
)
from aiogram.client.default import DefaultBotProperties

load_dotenv()

# Initialize a basic logger early (will be properly configured later)
logger = logging.getLogger("MAKIMA 🌸")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'))
logger.addHandler(console_handler)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

R34_API_KEY = os.getenv("R34_API_KEY")
R34_USER_ID = int(os.getenv("R34_USER_ID", "0"))

OWNER_ID = 5290407067
help_page_states = {}

RULE34_API_BASE = "https://api.rule34.xxx/index.php"

sent_content_ids = set()
user_offsets = {}
MAX_CONTENT_CACHE = 10000
api_request_times = []
MAX_REQUESTS_PER_MINUTE = 60

privacy_mode = "normal"

# Bot Messages Dictionary
BOT_MESSAGES = {
    "membership_reminder": """🌺 <b>Hey {user_mention}, Glad to see you!</b>

I'm <b>Makima</b>, but I only play with those who join our <b>lovely family!</b> 💖

<blockquote><i>✨ Join our <b>special places</b>. Tap below and come find me! 💕</i></blockquote>""",

    "welcome_text": """💖 <b>Hey there</b> <a href="tg://user?id={user_id}"><b>{user_name}</b></a>, <b>Welcome!</b>

<b>Makima</b> here, to brighten your day! 🌸

🎀 Enjoy <b>150+ anime commands</b> and <b>amazing content</b> from <b>22+ series.</b> All super easy to explore!

<blockquote><i>💌 Use any anime command to begin your journey!</i></blockquote>""",

    "membership_success": """🌸 <b>You're now officially part of our little world!</b> 💕

🥰 I'm really happy to have you here. You can now enjoy all the special features and content waiting for you.

<blockquote><b><i>I can't wait to share my favorite anime moments with you, sweetheart 🌺</i></b></blockquote>

✨ Type <b>/start</b> to begin your journey with me! 🎀""",

    "privacy_settings": """🔐 <b>Privacy Mode Settings</b>

<b>Current Mode:</b> {mode_emoji} <b>{mode_text}</b>

<blockquote>╭─<b> 🔓 Public Mode</b>
├─ Everyone can use the bot
├─ No membership requirements
╰─ Works in groups and private chats</blockquote>

<blockquote>╭─<b> 🔒 Normal Mode</b>
├─ Membership verification required
├─ Users must join channel & group
╰─ Default secure behavior</blockquote>

<b>👑 Owner always has full access regardless of mode</b>""",

    "search_guidance": """🔍 <b>Live Search Mode</b> 💫

<i>Searching for:</i> <b>"{search_text}"</b>

<blockquote>╭─ 🌟 <b>Search Tips:</b>
├─ Use character names: "sakura"
├─ Try anime names: "naruto", "bleach"
├─ Use underscores: "yor_forger"
╰─ Combine tags: "big_breasts"</blockquote>

<blockquote>╭─ 💡 <b>Popular searches:</b>
├─ Character names from any anime
├─ Series names with specific tags
╰─ Art styles like "anime", "manga", "3d"</blockquote>

⏳ <i>Searching live from internet...</i>""",

    "no_results": """🔍 <b>No Results Found</b> 😔

<i>Searched for:</i> <b>"{search_text}"</b>

<blockquote>╭─ 💡 <b>Try these instead:</b>
├─ Use underscores: "{search_underscore}"
├─ Try character first name only
├─ Check spelling of character names
╰─ Use /random for surprise content</blockquote>

<blockquote>╭─ 🌸 <b>Or try these popular characters:</b>
├─ hinata, sakura, tsunade (Naruto)
├─ rukia, orihime, yoruichi (Bleach)
╰─ mikasa, annie, historia (AOT)</blockquote>""",

    "media_selection": "💖 {title}\n\n✨ What would you like to see?",
    "anime_media_caption": "💖 {title} {media_emoji} ✨",
    "random_selection": "🎲 <b>Random Content</b> ✨\n\n💫 What would you like to see?",
    "random_media_caption": "🎲 <b>Random {media_type_title}</b> ✨\n\n💫 Enjoy this surprise!",
    "search_selection": "🔍 <b>Search Result</b> ✨\n\n💫 Found: <i>{search_text}</i>\n\n✨ What would you like to see?",
    "search_media_caption": "🔍 <b>Search Result</b> ✨\n\n💫 Found: <i>{search_query}</i>"
}

# Button Text Dictionary
BUTTON_TEXTS = {
    "membership_channel": "💟 Our Channel",
    "membership_group": "Our Group 💞",
    "membership_check": "💗️ Joined Both 💗",
    "updates": "💟 Updates",
    "support": "Support 💞",
    "add_to_group": "💗️ Add Me To Your Group 💗",
    "videos": "🎬 Videos",
    "images": "🖼️ Images",
    "animations": "🎨 Animations",
    "refresh": "💞 Refresh",
    "next": "💘 Next",
    "back": "💓 Back",
    "privacy_public": "🔓 Set Public Mode",
    "privacy_public_active": "🔓 Public Mode ✓",
    "privacy_normal": "🔒 Set Normal Mode",
    "privacy_normal_active": "🔒 Normal Mode ✓",
    "privacy_status": "📊 View Status"
}

# Callback Answers Dictionary
CALLBACK_ANSWERS = {
    "membership_success": "🎀 Yay! Welcome to our loving family, sweetheart! 💖",
    "membership_failed": "💘 You're not part of our cozy little family yet. Come join us, we're waiting with open arms 💅",
    "membership_required": "🥀️ You were here, part of our little family. Come back so we can continue this beautiful journey together ❤️‍🩹",
    "privacy_public": "🔓 Bot set to Public Mode - Everyone can use it now!",
    "privacy_normal": "🔒 Bot set to Normal Mode - Membership required!",
    "privacy_restricted": "⛔ This command is restricted.",
    "loading_content": "💞 Loading {media_type}...",
    "loading_random": "💞 Loading random {media_type}...",
    "loading_search": "💞 Loading {media_type} for '{search_query}'...",
    "fresh_content": "✨ Getting fresh content...",
    "more_content": "💞 Loading more content...",
    "back_to_selection": "💕 Going back to selection...",
    "back_to_menu": "💕 Returning to main menu..."
}

# Image URLs List
MAKIMA_IMAGES = [
    "https://ik.imagekit.io/asadofc/Images1.png",
    "https://ik.imagekit.io/asadofc/Images2.png",
    "https://ik.imagekit.io/asadofc/Images3.png",
    "https://ik.imagekit.io/asadofc/Images4.png",
    "https://ik.imagekit.io/asadofc/Images5.png",
    "https://ik.imagekit.io/asadofc/Images6.png",
    "https://ik.imagekit.io/asadofc/Images7.png",
    "https://ik.imagekit.io/asadofc/Images8.png",
    "https://ik.imagekit.io/asadofc/Images9.png",
    "https://ik.imagekit.io/asadofc/Images10.png",
    "https://ik.imagekit.io/asadofc/Images11.png",
    "https://ik.imagekit.io/asadofc/Images12.png",
    "https://ik.imagekit.io/asadofc/Images13.png",
    "https://ik.imagekit.io/asadofc/Images14.png",
    "https://ik.imagekit.io/asadofc/Images15.png",
    "https://ik.imagekit.io/asadofc/Images16.png",
    "https://ik.imagekit.io/asadofc/Images17.png",
    "https://ik.imagekit.io/asadofc/Images18.png",
    "https://ik.imagekit.io/asadofc/Images19.png",
    "https://ik.imagekit.io/asadofc/Images20.png",
    "https://ik.imagekit.io/asadofc/Images21.png",
    "https://ik.imagekit.io/asadofc/Images22.png",
    "https://ik.imagekit.io/asadofc/Images23.png",
    "https://ik.imagekit.io/asadofc/Images24.png",
    "https://ik.imagekit.io/asadofc/Images25.png",
    "https://ik.imagekit.io/asadofc/Images26.png",
    "https://ik.imagekit.io/asadofc/Images27.png",
    "https://ik.imagekit.io/asadofc/Images28.png",
    "https://ik.imagekit.io/asadofc/Images29.png",
    "https://ik.imagekit.io/asadofc/Images30.png",
    "https://ik.imagekit.io/asadofc/Images31.png",
    "https://ik.imagekit.io/asadofc/Images32.png",
    "https://ik.imagekit.io/asadofc/Images33.png",
    "https://ik.imagekit.io/asadofc/Images34.png",
    "https://ik.imagekit.io/asadofc/Images35.png",
    "https://ik.imagekit.io/asadofc/Images36.png",
    "https://ik.imagekit.io/asadofc/Images37.png",
    "https://ik.imagekit.io/asadofc/Images38.png",
    "https://ik.imagekit.io/asadofc/Images39.png",
    "https://ik.imagekit.io/asadofc/Images40.png"
]

# Media Type Emojis Dictionary
MEDIA_EMOJIS = {
    "image": "🖼️",
    "video": "🎬", 
    "gif": "🎨"
}

# URLs Dictionary
URLS = {
    "channel": "https://t.me/WorkGlows",
    "group": "https://t.me/SoulMeetsHQ"
}

# Environment Variable Validation
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN environment variable is required")
    raise ValueError("BOT_TOKEN environment variable is required")

if not R34_API_KEY:
    logger.error("❌ R34_API_KEY environment variable is required")
    raise ValueError("R34_API_KEY environment variable is required")

if not R34_USER_ID:
    logger.error("❌ R34_USER_ID environment variable is required")
    raise ValueError("R34_USER_ID environment variable is required")

logger.info("✅ All environment variables loaded successfully")

# LOGGING SETUP - Color classes and formatter functions
class Colors:
    BLUE = '\033[94m'      # INFO/WARNING
    GREEN = '\033[92m'     # DEBUG
    YELLOW = '\033[93m'    # INFO
    RED = '\033[91m'       # ERROR
    RESET = '\033[0m'      # Reset color
    BOLD = '\033[1m'       # Bold text

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to entire log messages"""

    COLORS = {
        'DEBUG': Colors.GREEN,
        'INFO': Colors.YELLOW,
        'WARNING': Colors.BLUE,
        'ERROR': Colors.RED,
    }

    def format(self, record):
        # Get the original formatted message
        original_format = super().format(record)

        # Get color based on log level
        color = self.COLORS.get(record.levelname, Colors.RESET)

        # Apply color to the entire message
        colored_format = f"{color}{original_format}{Colors.RESET}"

        return colored_format

def setup_colored_logging():
    """Setup colored logging configuration"""
    logger = logging.getLogger("MAKIMA 🌸")
    logger.setLevel(logging.INFO)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create colored formatter with enhanced format
    formatter = ColoredFormatter(
        fmt='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger

# Now properly configure the logger with colors
logger = setup_colored_logging()

# UTILITY FUNCTIONS
def extract_user_info(msg: Message) -> Dict[str, Any]:
    """Extract user and chat information from message"""
    logger.debug("🔍 Extracting user information from message")

    if not msg.from_user:
        return {
            "user_id": 0,
            "username": "Anonymous",
            "full_name": "Anonymous User",
            "first_name": "Anonymous",
            "last_name": "",
            "chat_id": msg.chat.id if msg.chat else 0,
            "chat_type": msg.chat.type if msg.chat else "unknown",
            "chat_title": msg.chat.title or msg.chat.first_name or "Unknown Chat",
            "chat_username": f"@{msg.chat.username}" if msg.chat and msg.chat.username else "No Username",
            "chat_link": f"https://t.me/{msg.chat.username}" if msg.chat and msg.chat.username else "No Link",
        }

    u = msg.from_user
    c = msg.chat
    info = {
        "user_id": u.id,
        "username": u.username or "No Username",
        "full_name": u.full_name,
        "first_name": u.first_name,
        "last_name": u.last_name or "",
        "chat_id": c.id,
        "chat_type": c.type,
        "chat_title": c.title or c.first_name or "",
        "chat_username": f"@{c.username}" if c.username else "No Username",
        "chat_link": f"https://t.me/{c.username}" if c.username else "No Link",
    }
    logger.info(
        f"📑 User info extracted: {info['full_name']} (@{info['username']}) "
        f"[ID: {info['user_id']}] in {info['chat_title']} [{info['chat_id']}] {info['chat_link']}"
    )
    return info

def log_with_user_info(level: str, message: str, user_info: Dict[str, Any]) -> None:
    """Log message with user information"""
    user_detail = (
        f"👤 {user_info.get('full_name', 'N/A')} (@{user_info.get('username', 'N/A')}) "
        f"[ID: {user_info.get('user_id', 'N/A')}] | "
        f"💬 {user_info.get('chat_title', 'N/A')} [{user_info.get('chat_id', 'N/A')}] "
        f"({user_info.get('chat_type', 'N/A')}) {user_info.get('chat_link', 'N/A')}"
    )
    full_message = f"{message} | {user_detail}"

    if level.upper() == "INFO":
        logger.info(full_message)
    elif level.upper() == "DEBUG":
        logger.debug(full_message)
    elif level.upper() == "WARNING":
        logger.warning(full_message)
    elif level.upper() == "ERROR":
        logger.error(full_message)
    else:
        logger.info(full_message)

bot = Bot(token=str(BOT_TOKEN), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
        logger.debug(f"🌐 HTTP GET request received from {self.client_address[0]}")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
        logger.debug(f"🌐 HTTP HEAD request received from {self.client_address[0]}")

    def log_message(self, format, *args):
        # Override default HTTP logging to use our colored logger
        logger.debug(f"🌐 HTTP {format % args}")

def check_membership(user_id):
    """Check if user is a member of required channel and group"""
    logger.info(f"🔍 Starting membership check for user ID: {user_id}")

    try:
        logger.debug(f"🌐 Preparing channel membership check for user {user_id}")
        channel_url = f"{TELEGRAM_API_URL}/getChatMember"
        channel_data = {"chat_id": "@WorkGlows", "user_id": user_id}
        logger.debug(f"📡 Channel API URL: {channel_url}")
        logger.debug(f"📋 Channel request data: {channel_data}")

        channel_response = requests.post(channel_url, json=channel_data, timeout=10)
        logger.debug(f"📨 Channel API response status: {channel_response.status_code}")

        logger.debug(f"🌐 Preparing group membership check for user {user_id}")
        group_url = f"{TELEGRAM_API_URL}/getChatMember"
        group_data = {"chat_id": "-1002186262653", "user_id": user_id}
        logger.debug(f"📡 Group API URL: {group_url}")
        logger.debug(f"📋 Group request data: {group_data}")

        group_response = requests.post(group_url, json=group_data, timeout=10)
        logger.debug(f"📨 Group API response status: {group_response.status_code}")

        if channel_response.status_code == 200 and group_response.status_code == 200:
            logger.debug(f"✅ Both API calls successful for user {user_id}")

            channel_member = channel_response.json().get("result", {})
            group_member = group_response.json().get("result", {})

            logger.debug(f"👤 Channel member data: {channel_member}")
            logger.debug(f"👥 Group member data: {group_member}")

            valid_statuses = ["member", "administrator", "creator"]
            logger.debug(f"📋 Valid membership statuses: {valid_statuses}")

            channel_status = channel_member.get("status")
            group_status = group_member.get("status")

            logger.debug(f"🔐 Channel status for user {user_id}: {channel_status}")
            logger.debug(f"🔐 Group status for user {user_id}: {group_status}")

            channel_joined = channel_status in valid_statuses
            group_joined = group_status in valid_statuses

            logger.debug(f"✓ Channel membership valid: {channel_joined}")
            logger.debug(f"✓ Group membership valid: {group_joined}")

            membership_status = channel_joined and group_joined

            if membership_status:
                logger.info(f"✅ User {user_id} has valid membership in both channel and group")
            else:
                logger.warning(f"⚠️ User {user_id} membership check failed - Channel: {channel_joined} ({channel_status}), Group: {group_joined} ({group_status})")

            return membership_status
        else:
            logger.error(f"❌ API error checking membership for user {user_id} - Channel: {channel_response.status_code}, Group: {group_response.status_code}")
            if channel_response.status_code != 200:
                logger.error(f"❌ Channel API error details: {channel_response.text}")
            if group_response.status_code != 200:
                logger.error(f"❌ Group API error details: {group_response.text}")
            return False

    except requests.RequestException as e:
        logger.error(f"❌ Network error during membership check for user {user_id}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected exception during membership check for user {user_id}: {str(e)}")
        return False

def should_check_membership(user_id):
    """Check if membership verification is required based on privacy mode"""
    global privacy_mode

    if user_id == OWNER_ID:
        logger.debug(f"👑 Owner {user_id} bypassing membership check")
        return False

    if privacy_mode == "public":
        logger.debug(f"🔓 Public mode active - user {user_id} bypassing membership check")
        return False

    logger.debug(f"🔒 Normal mode - user {user_id} requires membership verification")
    return True

async def send_membership_reminder(chat_id, user_id, user_name):
    """Send cute reminder about joining required channel and group"""
    logger.info(f"💌 Starting membership reminder process for {user_name} (ID: {user_id}) in chat {chat_id}")

    logger.debug(f"👤 Creating user mention for user: {user_name}")
    user_mention = f'<a href="tg://user?id={user_id}"><b>{user_name}</b></a>'
    logger.debug(f"🔗 User mention created: {user_mention}")

    logger.debug(f"📝 Formatting reminder message")
    reminder_message = BOT_MESSAGES["membership_reminder"].format(user_mention=user_mention)
    logger.debug(f"📄 Reminder message length: {len(reminder_message)} characters")

    logger.debug(f"⌨️ Creating inline keyboard for membership reminder")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=BUTTON_TEXTS["membership_channel"], url=URLS["channel"]),
            InlineKeyboardButton(text=BUTTON_TEXTS["membership_group"], url=URLS["group"])
        ],
        [
            InlineKeyboardButton(text=BUTTON_TEXTS["membership_check"], callback_data="check_membership")
        ]
    ])
    logger.debug(f"✅ Inline keyboard created with {len(keyboard.inline_keyboard)} rows")

    logger.debug(f"🎲 Selecting random image from {len(MAKIMA_IMAGES)} available images")
    selected_image = random.choice(MAKIMA_IMAGES)
    logger.info(f"🖼️ Selected reminder image: {selected_image}")

    try:
        logger.debug(f"📤 Sending upload photo action to chat {chat_id}")
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
        logger.debug(f"✅ Upload photo action sent successfully")

        logger.debug(f"📸 Sending membership reminder photo to chat {chat_id}")
        await bot.send_photo(
            chat_id=chat_id,
            photo=selected_image,
            caption=reminder_message,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        logger.info(f"✅ Membership reminder sent successfully to {user_name} (ID: {user_id}) in chat {chat_id}")

    except Exception as e:
        logger.error(f"❌ Failed to send membership reminder to {user_name} (ID: {user_id}) in chat {chat_id}: {str(e)}")
        logger.error(f"❌ Reminder failure details - Chat: {chat_id}, User: {user_id}, Image: {selected_image}")

def check_rate_limit():
    """Check if we're within API rate limits"""
    logger.debug(f"⏱️ Starting rate limit check")
    current_time = time.time()
    logger.debug(f"🕐 Current timestamp: {current_time}")

    global api_request_times
    original_count = len(api_request_times)
    logger.debug(f"📊 Original request count: {original_count}")

    # Filter out requests older than 60 seconds
    api_request_times = [t for t in api_request_times if current_time - t < 60]
    filtered_count = len(api_request_times)
    logger.debug(f"📊 Filtered request count (last 60s): {filtered_count}")

    if original_count != filtered_count:
        logger.debug(f"🧹 Cleaned {original_count - filtered_count} old request timestamps")

    if len(api_request_times) >= MAX_REQUESTS_PER_MINUTE:
        logger.warning(f"⚠️ Rate limit reached - {len(api_request_times)}/{MAX_REQUESTS_PER_MINUTE} requests in last minute")
        logger.warning(f"🚫 Rate limit exceeded, request blocked")
        return False

    api_request_times.append(current_time)
    logger.debug(f"➕ Added new request timestamp: {current_time}")
    logger.info(f"✅ Rate limit check passed - {len(api_request_times)}/{MAX_REQUESTS_PER_MINUTE} requests in last minute")
    return True

def manage_content_cache():
    """Manage content cache size to prevent memory issues"""
    logger.debug(f"🧹 Starting content cache management")
    global sent_content_ids
    original_size = len(sent_content_ids)
    logger.debug(f"📊 Current cache size: {original_size}/{MAX_CONTENT_CACHE}")

    if len(sent_content_ids) > MAX_CONTENT_CACHE:
        logger.warning(f"⚠️ Cache size exceeded limit: {original_size} > {MAX_CONTENT_CACHE}")
        logger.debug(f"🔄 Converting cache set to list for processing")
        cache_list = list(sent_content_ids)

        # Keep the second half (newer items)
        midpoint = len(cache_list) // 2
        logger.debug(f"✂️ Removing first {midpoint} items from cache")
        sent_content_ids = set(cache_list[midpoint:])

        new_size = len(sent_content_ids)
        logger.info(f"🧹 Content cache cleaned - reduced from {original_size} to {new_size} items ({original_size - new_size} removed)")
    else:
        logger.debug(f"✅ Cache size within limits, no cleanup needed")

def start_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 Starting dummy server on port {port}")
    logger.info("⚙️ Dummy HTTP server thread started.")
    try:
        server = HTTPServer(("0.0.0.0", port), DummyHandler)
        logger.info(f"✅ HTTP server successfully bound to 0.0.0.0:{port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"❌ Failed to start HTTP server: {str(e)}")
        raise

ANIME_COMMANDS = {
    "naruto": {
        "title": "Naruto", 
        "tags": ["hinata_hyuga", "sakura_haruno", "tsunade", "ino_yamanaka", "temari", "kushina_uzumaki"]
    },
    "kushina": {
        "title": "Kushina Uzumaki",
        "tags": ["kushina_uzumaki", "uzumaki_kushina", "kushina", "nine_tails_jinchuriki"]
    },
    "hinata": {
        "title": "Hinata Hyuga",
        "tags": ["hinata_hyuga", "hyuga_hinata", "hinata_(naruto)", "hinata", "byakugan"]
    },
    "sakura": {
        "title": "Sakura Haruno",
        "tags": ["sakura_haruno", "haruno_sakura", "sakura_(naruto)", "sakura", "medical_ninja"]
    },
    "temari": {
        "title": "Temari",
        "tags": ["temari_(naruto)", "temari", "sand_village", "wind_style", "fan_weapon"]
    },
    "konan": {
        "title": "Konan",
        "tags": ["konan", "paper_jutsu", "akatsuki_member"]
    },
    "ino": {
        "title": "Ino Yamanaka",
        "tags": ["ino_yamanaka", "yamanaka_ino", "ino"]
    },
    "shizune": {
        "title": "Makima",
        "tags": ["shizune", "medical_ninja", "tsunade_assistant", "leaf_village"]
    },
    "tsunade": {
        "title": "Tsunade",
        "tags": ["tsunade", "hokage", "blonde_hair", "medical_ninja", "legendary_sannin"]
    },
    "sarada": {
        "title": "Sarada Uchiha",
        "tags": ["sarada_uchiha"]
    },
    "rin": {
        "title": "Rin Nohara",
        "tags": ["rin_nohara"]
    },
    "tenten": {
        "title": "Tenten",
        "tags": ["tenten"]
    },
    "kurenai": {
        "title": "Kurenai Yuhi",
        "tags": ["kurenai_yuhi"]
    },
    "anko": {
        "title": "Anko Mitarashi",
        "tags": ["anko_mitarashi"]
    },
    "hanabi": {
        "title": "Hanabi Hyuga",
        "tags": ["hanabi_hyuga"]
    },
    "kaguya": {
        "title": "Kaguya Otsutsuki",
        "tags": ["kaguya_otsutsuki"]
    },
    "mei": {
        "title": "Mei Terumi",
        "tags": ["mei_terumi"]
    },
    "karin": {
        "title": "Karin Uzumaki",
        "tags": ["karin_uzumaki"]
    },
    "bleach": {
        "title": "Bleach", 
        "tags": ["orihime_inoue", "rukia_kuchiki", "yoruichi_shihouin", "rangiku_matsumoto", "nelliel_tu_odelschwanck"]
    },
    "rukia": {
        "title": "Rukia Kuchiki",
        "tags": ["rukia_kuchiki", "bleach", "kuchiki_rukia", "soul_reaper", "shinigami", "rukia"]
    },
    "orihime": {
        "title": "Orihime Inoue",
        "tags": ["orihime_inoue", "bleach", "inoue_orihime", "orihime", "human", "fullbringer"]
    },
    "yoruichi": {
        "title": "Yoruichi Shihouin",
        "tags": ["yoruichi_shihouin", "bleach", "shihouin_yoruichi", "yoruichi", "cat_form", "flash_goddess"]
    },
    "rangiku": {
        "title": "Rangiku Matsumoto",
        "tags": ["rangiku_matsumoto"]
    },
    "soifon": {
        "title": "Soi Fon",
        "tags": ["soi_fon"]
    },
    "nemu": {
        "title": "Nemu Kurotsuchi",
        "tags": ["nemu_kurotsuchi"]
    },
    "lisa": {
        "title": "Lisa Yadomaru",
        "tags": ["lisa_yadomaru"]
    },
    "hiyori": {
        "title": "Hiyori Sarugaki",
        "tags": ["hiyori_sarugaki"]
    },
    "mashiro": {
        "title": "Mashiro Kuna",
        "tags": ["mashiro_kuna"]
    },
    "retsu": {
        "title": "Retsu Unohana",
        "tags": ["retsu_unohana"]
    },
    "isane": {
        "title": "Isane Kotetsu",
        "tags": ["isane_kotetsu"]
    },
    "nanao": {
        "title": "Nanao Ise",
        "tags": ["nanao_ise"]
    },
    "yachiru": {
        "title": "Yachiru Kusajishi",
        "tags": ["yachiru_kusajishi"]
    },
    "nelliel": {
        "title": "Nelliel Tu Odelschwanck",
        "tags": ["nelliel_tu_odelschwanck"]
    },
    "katen": {
        "title": "Katen Kyōkotsu",
        "tags": ["katen_kyokotsu"]
    },
    "op": {
        "title": "One Piece", 
        "tags": ["nami_(one_piece)", "nico_robin", "nefeltari_vivi", "perona", "boa_hancock"]
    },
    "nami": {
        "title": "Nami",
        "tags": ["nami_(one_piece)"]
    },
    "hancock": {
        "title": "Boa Hancock",
        "tags": ["boa_hancock"]
    },
    "jjk": {
        "title": "Jujutsu Kaisen", 
        "tags": ["nobara_kugisaki", "maki_zenin", "mei_mei", "utahime_iori"]
    },
    "nobara": {
        "title": "Nobara Kugisaki",
        "tags": ["nobara_kugisaki", "kugisaki_nobara", "nobara", "hammer_and_nails", "blonde_hair", "brown_eyes"]
    },
    "maki": {
        "title": "Maki Zenin",
        "tags": ["maki_zenin"]
    },
    "yuki": {
        "title": "Yuki Tsukumo",
        "tags": ["yuki_tsukumo"]
    },
    "meimei": {
        "title": "Mei Mei",
        "tags": ["mei_mei"]
    },
    "utahime": {
        "title": "Utahime Iori",
        "tags": ["utahime_iori"]
    },
    "kasumi": {
        "title": "Kasumi Miwa",
        "tags": ["kasumi_miwa"]
    },
    "shoko": {
        "title": "Shoko Ieiri",
        "tags": ["shoko_ieiri"]
    },
    "rika": {
        "title": "Rika Orimoto",
        "tags": ["rika_orimoto"]
    },
    "spyfam": {
        "title": "Spy x Family", 
        "tags": ["yor_forger", "spy_x_family", "anya_forger"]
    },
    "yor": {
        "title": "Yor Forger",
        "tags": ["yor_forger"]
    },
    "anya": {
        "title": "Anya Forger",
        "tags": ["anya_forger"]
    },
    "aot": {
        "title": "Attack on Titan", 
        "tags": ["shingeki_no_kyojin", "mikasa_ackerman", "annie_leonhart", "historia_reiss", "pieck_finger"]
    },
    "mikasa": {
        "title": "Mikasa Ackerman",
        "tags": ["mikasa_ackerman"]
    },
    "annie": {
        "title": "Annie Leonhart",
        "tags": ["annie_leonhart"]
    },
    "historia": {
        "title": "Historia Reiss",
        "tags": ["historia_reiss"]
    },
    "sasha": {
        "title": "Sasha Blouse",
        "tags": ["sasha_blouse"]
    },
    "ymir": {
        "title": "Ymir",
        "tags": ["ymir"]
    },
    "hange": {
        "title": "Hange Zoë",
        "tags": ["hange_zoe"]
    },
    "pieck": {
        "title": "Pieck Finger",
        "tags": ["pieck_finger"]
    },
    "gabi": {
        "title": "Gabi Braun",
        "tags": ["gabi_braun"]
    },
    "carla": {
        "title": "Carla Yeager",
        "tags": ["carla_yeager"]
    },
    "frieda": {
        "title": "Frieda Reiss",
        "tags": ["frieda_reiss"]
    },
    "ymirfritz": {
        "title": "Ymir Fritz",
        "tags": ["ymir_fritz"]
    },
    "ds": {
        "title": "Demon Slayer", 
        "tags": ["nezuko_kamado", "shinobu_kocho", "mitsuri_kanroji", "kanao_tsuyuri"]
    },
    "nezuko": {
        "title": "Nezuko Kamado",
        "tags": ["nezuko_kamado", "demon_slayer", "kimetsu_no_yaiba", "kamado_nezuko", "nezuko", "demon_girl"]
    },
    "shinobu": {
        "title": "Shinobu Kocho",
        "tags": ["shinobu_kocho", "demon_slayer", "kimetsu_no_yaiba", "butterfly_hashira", "insect_hashira", "kocho_shinobu"]
    },
    "mitsuri": {
        "title": "Mitsuri Kanroji",
        "tags": ["mitsuri_kanroji", "demon_slayer", "kimetsu_no_yaiba", "love_hashira", "kanroji_mitsuri", "mitsuri"]
    },
    "kanao": {
        "title": "Kanao Tsuyuri",
        "tags": ["kanao_tsuyuri", "demon_slayer", "kimetsu_no_yaiba", "tsuyuri_kanao", "kanao", "flower_breathing"]
    },
    "daki": {
        "title": "Daki",
        "tags": ["daki"]
    },
    "tamayo": {
        "title": "Tamayo",
        "tags": ["tamayo"]
    },
    "aoi": {
        "title": "Aoi Kanzaki",
        "tags": ["aoi_kanzaki"]
    },
    "kanae": {
        "title": "Kanae Kocho",
        "tags": ["kanae_kocho"]
    },
    "amane": {
        "title": "Ubuyashiki Amane",
        "tags": ["ubuyashiki_amane"]
    },
    "vs": {
        "title": "Vinland Saga", 
        "tags": ["vinland_saga", "thorfinn", "askeladd"]
    },
    "helga": {
        "title": "Helga",
        "tags": ["helga"]
    },
    "ylva": {
        "title": "Ylva",
        "tags": ["ylva"]
    },
    "arnheid": {
        "title": "Arnheid",
        "tags": ["arnheid"]
    },
    "gudrid": {
        "title": "Gudrid",
        "tags": ["gudrid"]
    },
    "dand": {
        "title": "Dandadan", 
        "tags": ["dandadan", "momo_ayase", "seiko_ayase"]
    },
    "momoayase": {
        "title": "Momo Ayase",
        "tags": ["momo_ayase"]
    },
    "oka": {
        "title": "Oka Sarutobi",
        "tags": ["oka_sarutobi"]
    },
    "naomidand": {
        "title": "Naomi",
        "tags": ["naomi"]
    },
    "shakunetsu": {
        "title": "Shakunetsu Ayase",
        "tags": ["shakunetsu_ayase"]
    },
    "ikue": {
        "title": "Ikue",
        "tags": ["ikue"]
    },
    "opm": {
        "title": "One Punch Man", 
        "tags": ["fubuki_(one-punch_man)", "tatsumaki"]
    },
    "tatsumaki": {
        "title": "Tatsumaki",
        "tags": ["tatsumaki"]
    },
    "fubuki": {
        "title": "Fubuki",
        "tags": ["fubuki_(one-punch_man)"]
    },
    "cm": {
        "title": "Chainsaw Man", 
        "tags": ["power_(chainsaw_man)", "makima", "chainsaw_man", "kobeni_higashiyama"]
    },
    "power": {
        "title": "Power",
        "tags": ["power_(chainsaw_man)"]
    },
    "makima": {
        "title": "Makima",
        "tags": ["makima"]
    },
    "himeno": {
        "title": "Himeno",
        "tags": ["himeno"]
    },
    "quanxi": {
        "title": "Quanxi",
        "tags": ["quanxi"]
    },
    "reze": {
        "title": "Reze",
        "tags": ["reze"]
    },
    "angel": {
        "title": "Angel Devil",
        "tags": ["angel_devil"]
    },
    "asa": {
        "title": "Asa Mitaka",
        "tags": ["asa_mitaka"]
    },
    "sd": {
        "title": "Sakamoto Days", 
        "tags": ["sakamoto_days", "lu_xiaotang"]
    },
    "osaragi": {
        "title": "Osaragi",
        "tags": ["osaragi_(sakamoto_days)"]
    },
    "drs": {
        "title": "Dr Stone", 
        "tags": ["dr._stone", "kohaku_(dr._stone)", "ruri_(dr._stone)"]
    },
    "yuzuriha": {
        "title": "Yuzuriha Ogawa",
        "tags": ["yuzuriha_ogawa"]
    },
    "kohaku": {
        "title": "Kohaku",
        "tags": ["kohaku_(dr._stone)"]
    },
    "ruri": {
        "title": "Ruri",
        "tags": ["ruri_(dr._stone)"]
    },
    "suika": {
        "title": "Suika",
        "tags": ["suika"]
    },
    "stella": {
        "title": "Stella",
        "tags": ["stella"]
    },
    "overflow": {
        "title": "Overflow", 
        "tags": ["overflow", "kotone_shirakawa", "ayane_shirakawa"]
    },
    "kotone": {
        "title": "Kotone Shirakawa",
        "tags": ["kotone_shirakawa"]
    },
    "ayane": {
        "title": "Ayane Shirakawa",
        "tags": ["ayane_shirakawa"]
    },
    "bnha": {
        "title": "My Hero Academia", 
        "tags": ["ochako_uraraka", "momo_yaoyorozu", "tsuyu_asui", "kyoka_jiro", "mina_ashido", "boku_no_hero_academia"]
    },
    "ochako": {
        "title": "Ochako Uraraka",
        "tags": ["ochako_uraraka", "boku_no_hero_academia"]
    },
    "momo": {
        "title": "Momo Yaoyorozu",
        "tags": ["momo_yaoyorozu", "boku_no_hero_academia"]
    },
    "tsuyu": {
        "title": "Tsuyu Asui",
        "tags": ["tsuyu_asui", "boku_no_hero_academia"]
    },
    "kyoka": {
        "title": "Kyoka Jiro",
        "tags": ["kyoka_jiro", "boku_no_hero_academia"]
    },
    "mina": {
        "title": "Mina Ashido",
        "tags": ["mina_ashido", "boku_no_hero_academia"]
    },
    "toru": {
        "title": "Toru Hagakure",
        "tags": ["toru_hagakure", "boku_no_hero_academia"]
    },
    "nejire": {
        "title": "Nejire Hado",
        "tags": ["nejire_hado", "boku_no_hero_academia"]
    },
    "mt": {
        "title": "Mt. Lady",
        "tags": ["mt._lady", "boku_no_hero_academia"]
    },
    "midnight": {
        "title": "Midnight",
        "tags": ["midnight", "boku_no_hero_academia"]
    },
    "mirko": {
        "title": "Mirko",
        "tags": ["mirko", "boku_no_hero_academia"]
    },
    "bubble": {
        "title": "Bubble Girl",
        "tags": ["bubble_girl", "boku_no_hero_academia"]
    },
    "uwabami": {
        "title": "Uwabami",
        "tags": ["uwabami", "boku_no_hero_academia"]
    },
    "ryukyu": {
        "title": "Ryukyu",
        "tags": ["ryukyu", "boku_no_hero_academia"]
    },
    "pixie": {
        "title": "Pixie-Bob",
        "tags": ["pixie-bob", "boku_no_hero_academia"]
    },
    "mandalay": {
        "title": "Mandalay",
        "tags": ["mandalay", "boku_no_hero_academia"]
    },
    "ragdoll": {
        "title": "Ragdoll",
        "tags": ["ragdoll", "boku_no_hero_academia"]
    },
    "tiger": {
        "title": "Tiger",
        "tags": ["tiger", "boku_no_hero_academia"]
    },
    "thirteen": {
        "title": "Thirteen",
        "tags": ["thirteen", "boku_no_hero_academia"]
    },
    "recovery": {
        "title": "Recovery Girl",
        "tags": ["recovery_girl", "boku_no_hero_academia"]
    },
    "inko": {
        "title": "Inko Midoriya",
        "tags": ["inko_midoriya", "boku_no_hero_academia"]
    },
    "rei": {
        "title": "Rei Todoroki",
        "tags": ["rei_todoroki", "boku_no_hero_academia"]
    },
    "fuyumi": {
        "title": "Fuyumi Todoroki",
        "tags": ["fuyumi_todoroki", "boku_no_hero_academia"]
    },
    "nana": {
        "title": "Nana Shimura",
        "tags": ["nana_shimura", "boku_no_hero_academia"]
    },
    "star": {
        "title": "Star and Stripe",
        "tags": ["star_and_stripe", "boku_no_hero_academia"]
    },
    "lady": {
        "title": "Lady Nagant",
        "tags": ["lady_nagant", "boku_no_hero_academia"]
    },
    "camie": {
        "title": "Camie Utsushimi",
        "tags": ["camie_utsushimi", "boku_no_hero_academia"]
    },
    "yu": {
        "title": "Yu Takeyama",
        "tags": ["yu_takeyama", "boku_no_hero_academia"]
    },
    "nao": {
        "title": "Nao",
        "tags": ["nao", "boku_no_hero_academia"]
    },
    "kendo": {
        "title": "Itsuka Kendo",
        "tags": ["itsuka_kendo", "boku_no_hero_academia"]
    },
    "ibara": {
        "title": "Ibara Shiozaki",
        "tags": ["ibara_shiozaki", "boku_no_hero_academia"]
    },
    "setsuna": {
        "title": "Setsuna Tokage",
        "tags": ["setsuna_tokage", "boku_no_hero_academia"]
    },
    "pony": {
        "title": "Pony Tsunotori",
        "tags": ["pony_tsunotori", "boku_no_hero_academia"]
    },
    "reiko": {
        "title": "Reiko Yanagi",
        "tags": ["reiko_yanagi", "boku_no_hero_academia"]
    },
    "kinoko": {
        "title": "Kinoko Komori",
        "tags": ["kinoko_komori", "boku_no_hero_academia"]
    },
    "shihai": {
        "title": "Shihai Kuroiro",
        "tags": ["shihai_kuroiro", "boku_no_hero_academia"]
    },
    "yui": {
        "title": "Yui Kodai",
        "tags": ["yui_kodai", "boku_no_hero_academia"]
    },
    "hxh": {
        "title": "Hunter x Hunter", 
        "tags": ["hunter_x_hunter", "machi_komacine", "shizuku_murasaki"]
    },
    "biscuit": {
        "title": "Biscuit Krueger",
        "tags": ["biscuit_krueger", "hunter_x_hunter"]
    },
    "machi": {
        "title": "Machi Komacine",
        "tags": ["machi_komacine", "hunter_x_hunter"]
    },
    "neon": {
        "title": "Neon Nostrade",
        "tags": ["neon_nostrade", "hunter_x_hunter"]
    },
    "mha": {
        "title": "My Hero Academia", 
        "tags": ["ochako_uraraka", "momo_yaoyorozu", "tsuyu_asui", "nejire_hado", "boku_no_hero_academia"]
    },
    "ochaco": {
        "title": "Ochaco Uraraka",
        "tags": ["ochako_uraraka", "boku_no_hero_academia"]
    },
    "tsuyu": {
        "title": "Tsuyu Asui",
        "tags": ["tsuyu_asui", "boku_no_hero_academia"]
    },
    "momoyaoyorozu": {
        "title": "Momo Yaoyorozu",
        "tags": ["momo_yaoyorozu", "boku_no_hero_academia"]
    },
    "toga": {
        "title": "Himiko Toga",
        "tags": ["himiko_toga", "boku_no_hero_academia"]
    },
    "kyoka": {
        "title": "Kyoka Jiro",
        "tags": ["kyoka_jiro", "boku_no_hero_academia"]
    },
    "nejire": {
        "title": "Nejire Hado",
        "tags": ["nejire_hado", "boku_no_hero_academia"]
    },
    "mirko": {
        "title": "Mirko",
        "tags": ["mirko", "boku_no_hero_academia"]
    },
    "mina": {
        "title": "Mina Ashido",
        "tags": ["mina_ashido", "boku_no_hero_academia"]
    },
    "star": {
        "title": "Star and Stripe",
        "tags": ["star_and_stripe", "boku_no_hero_academia"]
    },
    "eri": {
        "title": "Eri",
        "tags": ["eri", "boku_no_hero_academia"]
    },
    "fma": {
        "title": "Fullmetal Alchemist", 
        "tags": ["fullmetal_alchemist", "winry_rockbell", "riza_hawkeye", "lust_(fma)", "izumi_curtis"]
    },
    "winry": {
        "title": "Winry Rockbell",
        "tags": ["winry_rockbell", "fullmetal_alchemist"]
    },
    "riza": {
        "title": "Riza Hawkeye",
        "tags": ["riza_hawkeye", "fullmetal_alchemist"]
    },
    "olivier": {
        "title": "Olivier Mira Armstrong",
        "tags": ["olivier_mira_armstrong", "fullmetal_alchemist"]
    },
    "izumi": {
        "title": "Izumi Curtis",
        "tags": ["izumi_curtis", "fullmetal_alchemist"]
    },
    "lanfan": {
        "title": "Lan Fan",
        "tags": ["lan_fan", "fullmetal_alchemist"]
    },
    "meichang": {
        "title": "Mei Chang",
        "tags": ["mei_chang", "fullmetal_alchemist"]
    },
    "rose": {
        "title": "Rose Thomas",
        "tags": ["rose_thomas", "fullmetal_alchemist"]
    },
    "nina": {
        "title": "Nina Tucker",
        "tags": ["nina_tucker", "fullmetal_alchemist"]
    },
    "trisha": {
        "title": "Trisha Elric",
        "tags": ["trisha_elric", "fullmetal_alchemist"]
    },
    "sheska": {
        "title": "Sheska",
        "tags": ["sheska", "fullmetal_alchemist"]
    },
    "dn": {
        "title": "Death Note", 
        "tags": ["death_note", "misa_amane", "naomi_misora"]
    },
    "misa": {
        "title": "Misa Amane",
        "tags": ["misa_amane", "death_note"]
    },
    "naomimisora": {
        "title": "Naomi Misora",
        "tags": ["naomi_misora", "death_note"]
    },
    "kiyomi": {
        "title": "Kiyomi Takada",
        "tags": ["kiyomi_takada", "death_note"]
    },
    "tg": {
        "title": "Tokyo Ghoul", 
        "tags": ["tokyo_ghoul", "touka_kirishima", "rize_kamishiro"]
    },
    "touka": {
        "title": "Touka Kirishima",
        "tags": ["touka_kirishima", "tokyo_ghoul"]
    },
    "eto": {
        "title": "Eto Yoshimura",
        "tags": ["eto_yoshimura", "tokyo_ghoul"]
    },
    "rize": {
        "title": "Rize Kamishiro",
        "tags": ["rize_kamishiro", "tokyo_ghoul"]
    },
    "akira": {
        "title": "Akira Mado",
        "tags": ["akira_mado", "tokyo_ghoul"]
    },
    "hinami": {
        "title": "Hinami Fueguchi",
        "tags": ["hinami_fueguchi", "tokyo_ghoul"]
    },
    "itori": {
        "title": "Itori",
        "tags": ["itori", "tokyo_ghoul"]
    },
    "karren": {
        "title": "Karren von Rosewald",
        "tags": ["karren_von_rosewald", "tokyo_ghoul"]
    },
    "kimi": {
        "title": "Kimi Nishino",
        "tags": ["kimi_nishino", "tokyo_ghoul"]
    },
    "yoriko": {
        "title": "Yoriko Kosaka",
        "tags": ["yoriko_kosaka", "tokyo_ghoul"]
    },
    "roma": {
        "title": "Roma Hoito",
        "tags": ["roma_hoito", "tokyo_ghoul"]
    },
    "mdd": {
        "title": "My Dress-Up Darling", 
        "tags": ["sono_bisque_doll_wa_koi_wo_suru", "marin_kitagawa"]
    },
    "marin": {
        "title": "Marin Kitagawa",
        "tags": ["marin_kitagawa"]
    },
    "sajuna": {
        "title": "Sajuna Inui",
        "tags": ["sajuna_inui"]
    },
    "shinju": {
        "title": "Shinju Inui",
        "tags": ["shinju_inui"]
    },
    "boruto": {
        "title": "Boruto", 
        "tags": ["boruto", "sarada_uchiha", "himawari_uzumaki"]
    },
    "ps": {
        "title": "Prison School", 
        "tags": ["prison_school", "hana_midorikawa", "meiko_shiraki", "mari_kurihara"]
    }
}

PRIORITY_COMMANDS = [
    "start",
    "naruto", "hinata", "sakura", "tsunade", "kushina", "temari", "ino", "konan", "shizune", "sarada", "rin", "tenten", "kurenai", "anko", "hanabi", "kaguya", "mei", "karin",
    "bleach", "rukia", "orihime", "yoruichi", "rangiku", "nelliel", "soifon", "nemu", "lisa", "hiyori",
    "op", "nami", "hancock",
    "jjk", "nobara", "maki", "yuki", "meimei", "utahime",
    "spyfam", "yor", "anya",
    "aot", "mikasa", "annie", "historia", "sasha", "ymir", "pieck",
    "ds", "nezuko", "shinobu", "mitsuri", "daki", "kanao",
    "opm", "tatsumaki", "fubuki",
    "cm", "power", "makima",
    "mha", "ochaco", "tsuyu", "toga", "momoyaoyorozu", "kyoka", "nejire", "mirko", "mina", "eri",
    "fma", "winry", "riza", "olivier", "izumi",
    "dn", "misa",
    "tg", "touka", "rize", "eto", "akira", "hinami",
    "mdd", "marin", "sajuna", "shinju",
    "vs", "dand", "sd", "drs", "overflow", "hxh", "boruto", "ps"
]

REGISTERED_COMMANDS = PRIORITY_COMMANDS[:97] + ["random"]

COMMAND_DESCRIPTIONS = {
    "start": "💖 Meet Makima",
    "random": "🎲 Surprise Me",
    "naruto": "🍃 Ninja World",
    "bleach": "⚔️ Soul Society", 
    "op": "🏴‍☠️ Grand Line",
    "jjk": "✨ Cursed Energy",
    "spyfam": "🕵️ Secret Family",
    "aot": "⚡ Titan World",
    "ds": "🗡️ Demon Hunt",
    "vs": "🛡️ Viking Saga",
    "dand": "👻 Yokai Hunt",
    "opm": "💪 Hero World",
    "cm": "⛓️ Devil Hunt",
    "sd": "🎯 Assassin Life",
    "drs": "🧪 Science World",
    "overflow": "💧 School Days",
    "hxh": "🎮 Hunter Life",
    "mha": "🦸 Hero Academy",
    "fma": "⚗️ Alchemy Art",
    "dn": "📓 Death Gods",
    "tg": "🖤 Ghoul World",
    "mdd": "👗 Cosplay Fun",
    "boruto": "🌟 New Era",
    "ps": "🏫 School Prison",
    "hinata": "💜 Shy Princess",
    "sakura": "🌸 Cherry Blossom",
    "tsunade": "👑 Legendary Sannin",
    "kushina": "❤️ Red Hot",
    "rukia": "❄️ Ice Princess", 
    "orihime": "🧡 Sweet Angel",
    "yoruichi": "⚡ Flash Goddess",
    "mikasa": "⚔️ Warrior Queen",
    "annie": "💎 Crystal Girl",
    "nezuko": "🌺 Bamboo Cutie",
    "shinobu": "🦋 Butterfly Beauty",
    "nobara": "🔨 Strong Girl",
    "maki": "💚 Weapon Master",
    "yor": "🖤 Assassin Mom",
    "anya": "💕 Mind Reader",
    "power": "🩸 Blood Fiend",
    "makima": "🐕 Control Devil",
    "nami": "🍊 Navigator",
    "hancock": "🐍 Snake Princess"
}

BOT_COMMANDS = [
    BotCommand(command=cmd, description=COMMAND_DESCRIPTIONS.get(cmd, f"💖 {cmd.title()}"))
    for cmd in REGISTERED_COMMANDS
]

async def fetch_rule34_media(anime_name: str, media_type: str = "image", user_info: Dict[str, Any] = None, max_retries: int = 5):
    """
    Fetches anime-specific NSFW content from Rule34 API using tags
    Returns high-quality content (image/video/gif) with guaranteed success through retries
    Prevents duplicate content using advanced tracking system
    """
    log_with_user_info("INFO", f"🎯 Starting Rule34 media fetch for anime: {anime_name}, media_type: {media_type}", user_info or {})

    anime_data = ANIME_COMMANDS.get(anime_name)
    if not anime_data:
        log_with_user_info("ERROR", f"❌ Anime '{anime_name}' not found in ANIME_COMMANDS", user_info or {})
        return None

    log_with_user_info("DEBUG", f"✅ Anime data found for {anime_name}: {anime_data['title']} with {len(anime_data['tags'])} tags", user_info or {})

    tags = anime_data["tags"]
    user_id = user_info.get("user_id", 0) if user_info else 0
    user_key = f"{user_id}_{anime_name}" if user_id else anime_name

    if user_key not in user_offsets:
        user_offsets[user_key] = 0
        log_with_user_info("DEBUG", f"🆕 Created new user offset for key: {user_key}", user_info or {})

    log_with_user_info("INFO", f"📍 User offset for {user_key}: {user_offsets[user_key]}", user_info or {})

    for retry in range(max_retries):
        log_with_user_info("DEBUG", f"🔄 Attempt {retry + 1}/{max_retries} for {anime_name}", user_info or {})

        try:
            character_specific_tags = []
            generic_tags = []

            character_name = anime_data["title"].lower().replace(" ", "_")
            log_with_user_info("DEBUG", f"🔤 Processing character name: {character_name}", user_info or {})

            for tag in tags:
                if any(name_part in tag.lower() for name_part in character_name.split("_")):
                    character_specific_tags.append(tag)
                else:
                    generic_tags.append(tag)

            log_with_user_info("DEBUG", f"🏷️ Character specific tags: {character_specific_tags}", user_info or {})
            log_with_user_info("DEBUG", f"🏷️ Generic tags: {generic_tags}", user_info or {})

            if retry < len(character_specific_tags):
                selected_tags = [character_specific_tags[retry]]
                log_with_user_info("DEBUG", f"🎯 Using character specific tag: {selected_tags}", user_info or {})
            elif retry < len(character_specific_tags) + len(generic_tags):
                generic_index = retry - len(character_specific_tags)
                selected_tags = [generic_tags[generic_index]]
                log_with_user_info("DEBUG", f"🎯 Using generic tag: {selected_tags}", user_info or {})
            else:
                if character_specific_tags:
                    primary_tag = random.choice(character_specific_tags)
                    if len(character_specific_tags) > 1:
                        secondary_tag = random.choice([t for t in character_specific_tags if t != primary_tag])
                        selected_tags = [primary_tag, secondary_tag]
                        log_with_user_info("DEBUG", f"🎯 Using combined character tags: {selected_tags}", user_info or {})
                    else:
                        selected_tags = [primary_tag]
                        log_with_user_info("DEBUG", f"🎯 Using single character tag: {selected_tags}", user_info or {})
                else:
                    tag_count = min(random.randint(1, 2), len(generic_tags))
                    selected_tags = random.sample(generic_tags, tag_count)
                    log_with_user_info("DEBUG", f"🎯 Using random generic tags: {selected_tags}", user_info or {})

            tag_string = "+".join(selected_tags)
            log_with_user_info("INFO", f"🔗 Final tag string: {tag_string}", user_info or {})

            page_offset = user_offsets[user_key] + retry
            log_with_user_info("DEBUG", f"📄 Page offset: {page_offset}", user_info or {})

            if not check_rate_limit():
                log_with_user_info("WARNING", f"⚠️ Rate limit exceeded, sleeping for 10 seconds", user_info or {})
                await asyncio.sleep(10)
                continue

            manage_content_cache()

            log_with_user_info("DEBUG", f"🌐 Making API request to Rule34 with tags: {tag_string}", user_info or {})
            async with aiohttp.ClientSession() as session:
                params = {
                    "page": "dapi",
                    "s": "post",
                    "q": "index",
                    "tags": tag_string,
                    "limit": 100,
                    "pid": page_offset,
                    "api_key": R34_API_KEY,
                    "user_id": R34_USER_ID
                }
                log_with_user_info("DEBUG", f"📋 API params: {params}", user_info or {})

                async with session.get(RULE34_API_BASE, params=params) as response:
                    log_with_user_info("DEBUG", f"📡 API response status: {response.status}", user_info or {})

                    if response.status == 200:
                        xml_content = await response.text()
                        log_with_user_info("DEBUG", f"📄 Received XML content length: {len(xml_content)} characters", user_info or {})

                        try:
                            root = ET.fromstring(xml_content)
                            log_with_user_info("DEBUG", f"✅ Successfully parsed XML", user_info or {})

                            posts = []
                            total_posts_found = 0

                            for post in root.findall('.//post'):
                                total_posts_found += 1
                                post_id = post.get('id')
                                file_url = post.get('file_url')

                                if post_id in sent_content_ids:
                                    log_with_user_info("DEBUG", f"⏭️ Skipping duplicate post ID: {post_id}", user_info or {})
                                    continue

                                if file_url and file_url.startswith(('http://', 'https://')):
                                    # Check image formats with PNG priority
                                    if media_type == "image" and file_url.lower().endswith(('.jpg', '.jpeg', '.webp', '.png')):
                                        # Prefer non-PNG formats for better compatibility
                                        priority = 1 if file_url.lower().endswith('.png') else 2
                                        posts.append({
                                            'url': file_url,
                                            'id': post_id,
                                            'tags': post.get('tags', ''),
                                            'score': int(post.get('score', 0)),
                                            'type': 'image',
                                            'priority': priority
                                        })
                                    elif media_type == "gif" and file_url.lower().endswith('.gif'):
                                        posts.append({
                                            'url': file_url,
                                            'id': post_id,
                                            'tags': post.get('tags', ''),
                                            'score': int(post.get('score', 0)),
                                            'type': 'gif'
                                        })
                                    elif media_type == "video" and file_url.lower().endswith(('.mp4', '.webm', '.mov')):
                                        posts.append({
                                            'url': file_url,
                                            'id': post_id,
                                            'tags': post.get('tags', ''),
                                            'score': int(post.get('score', 0)),
                                            'type': 'video'
                                        })

                            log_with_user_info("INFO", f"📊 Found {total_posts_found} total posts, {len(posts)} matching {media_type} type", user_info or {})

                            if posts:
                                # Sort by priority then score for better compatibility
                                posts.sort(key=lambda x: (x.get('priority', 1), x['score']), reverse=True)
                                top_posts = posts[:50]
                                selected = random.choice(top_posts)

                                log_with_user_info("INFO", f"✨ Selected post: ID {selected['id']}, score {selected['score']}, type {selected['type']}", user_info or {})

                                sent_content_ids.add(selected['id'])
                                log_with_user_info("DEBUG", f"💾 Added post ID {selected['id']} to sent_content_ids cache", user_info or {})

                                user_offsets[user_key] += 1
                                log_with_user_info("DEBUG", f"📈 Incremented user offset for {user_key} to {user_offsets[user_key]}", user_info or {})

                                return selected
                            else:
                                log_with_user_info("WARNING", f"⚠️ No posts found matching criteria for attempt {retry + 1}", user_info or {})

                        except ET.ParseError as e:
                            log_with_user_info("ERROR", f"❌ XML parsing error on attempt {retry + 1}: {str(e)}", user_info or {})
                            continue
                    else:
                        log_with_user_info("ERROR", f"❌ API request failed with status {response.status}", user_info or {})

        except Exception as e:
            log_with_user_info("ERROR", f"❌ Exception during attempt {retry + 1}: {str(e)}", user_info or {})
            continue

    log_with_user_info("WARNING", f"⚠️ All primary attempts failed, starting fallback search for {anime_name}", user_info or {})
    character_name = anime_data["title"].lower().replace(" ", "_")
    fallback_tags = list(tags) + [character_name]
    log_with_user_info("DEBUG", f"🔄 Fallback tags: {fallback_tags}", user_info or {})

    for tag in fallback_tags:
        log_with_user_info("DEBUG", f"🔍 Trying fallback tag: {tag}", user_info or {})
        try:
            page_offset = random.randint(0, 10)
            log_with_user_info("DEBUG", f"📄 Fallback page offset: {page_offset}", user_info or {})

            async with aiohttp.ClientSession() as session:
                params = {
                    "page": "dapi",
                    "s": "post", 
                    "q": "index",
                    "tags": tag,
                    "limit": 100,
                    "pid": page_offset,
                    "api_key": R34_API_KEY,
                    "user_id": R34_USER_ID
                }
                log_with_user_info("DEBUG", f"📋 Fallback API params: {params}", user_info or {})

                async with session.get(RULE34_API_BASE, params=params) as response:
                    log_with_user_info("DEBUG", f"📡 Fallback API response status: {response.status}", user_info or {})

                    if response.status == 200:
                        xml_content = await response.text()
                        log_with_user_info("DEBUG", f"📄 Fallback XML content length: {len(xml_content)} characters", user_info or {})

                        try:
                            root = ET.fromstring(xml_content)
                            posts = []
                            total_posts_found = 0

                            for post in root.findall('.//post'):
                                total_posts_found += 1
                                post_id = post.get('id')
                                file_url = post.get('file_url')

                                if post_id in sent_content_ids:
                                    continue

                                if file_url and file_url.startswith(('http://', 'https://')):
                                    # Check image formats with PNG handling
                                    if media_type == "image" and file_url.lower().endswith(('.jpg', '.jpeg', '.webp', '.png')):
                                        # Prefer non-PNG formats for better compatibility
                                        priority = 1 if file_url.lower().endswith('.png') else 2
                                        posts.append({
                                            'url': file_url,
                                            'id': post_id,
                                            'tags': post.get('tags', ''),
                                            'score': int(post.get('score', 0)),
                                            'type': 'image',
                                            'priority': priority
                                        })
                                    elif media_type == "gif" and file_url.lower().endswith('.gif'):
                                        posts.append({
                                            'url': file_url,
                                            'id': post_id,
                                            'tags': post.get('tags', ''),
                                            'score': int(post.get('score', 0)),
                                            'type': 'gif'
                                        })
                                    elif media_type == "video" and file_url.lower().endswith(('.mp4', '.webm', '.mov')):
                                        posts.append({
                                            'url': file_url,
                                            'id': post_id,
                                            'tags': post.get('tags', ''),
                                            'score': int(post.get('score', 0)),
                                            'type': 'video'
                                        })

                            log_with_user_info("INFO", f"📊 Fallback found {total_posts_found} total posts, {len(posts)} matching {media_type} type", user_info or {})

                            if posts:
                                # Sort by priority then score for better compatibility
                                posts.sort(key=lambda x: (x.get('priority', 1), x['score']), reverse=True)
                                selected = random.choice(posts[:30])

                                log_with_user_info("INFO", f"✨ Fallback selected post: ID {selected['id']}, score {selected['score']}, type {selected['type']}", user_info or {})

                                sent_content_ids.add(selected['id'])
                                log_with_user_info("DEBUG", f"💾 Added fallback post ID {selected['id']} to cache", user_info or {})

                                return selected
                        except ET.ParseError as e:
                            log_with_user_info("ERROR", f"❌ Fallback XML parsing error: {str(e)}", user_info or {})
                            continue
        except Exception as e:
            log_with_user_info("ERROR", f"❌ Fallback exception for tag {tag}: {str(e)}", user_info or {})
            continue

    log_with_user_info("ERROR", f"❌ Complete failure: No content found for {anime_name} with media_type {media_type}", user_info or {})
    return None

def create_media_selection_keyboard(anime_name: str):
    """Create beautiful keyboard for media type selection"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=BUTTON_TEXTS["videos"], callback_data=f"select_video_{anime_name}"),
            InlineKeyboardButton(text=BUTTON_TEXTS["images"], callback_data=f"select_image_{anime_name}")
        ],
        [
            InlineKeyboardButton(text=BUTTON_TEXTS["animations"], callback_data=f"select_gif_{anime_name}")
        ]
    ])
    return keyboard

def create_media_navigation_keyboard(anime_name: str, media_type: str, page: int = 1):
    """Create beautiful keyboard for media navigation with Update, Next, Back buttons"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=BUTTON_TEXTS["refresh"], callback_data=f"update_{anime_name}_{media_type}_{page}"),
            InlineKeyboardButton(text=BUTTON_TEXTS["next"], callback_data=f"next_{anime_name}_{media_type}_{page}")
        ],
        [
            InlineKeyboardButton(text=BUTTON_TEXTS["back"], callback_data=f"back_{anime_name}")
        ]
    ])
    return keyboard

async def send_media_selection(anime_name: str, chat_id: int, user_info: Dict[str, Any] = None):
    """Send initial image with media type selection buttons"""
    log_with_user_info("INFO", f"🎯 Starting media selection for anime: {anime_name} in chat: {chat_id}", user_info or {})

    anime_data = ANIME_COMMANDS.get(anime_name)
    if not anime_data:
        log_with_user_info("ERROR", f"❌ Anime '{anime_name}' not found in ANIME_COMMANDS", user_info or {})
        return None

    title = anime_data["title"]
    log_with_user_info("DEBUG", f"📝 Anime title: {title}", user_info or {})

    log_with_user_info("DEBUG", f"🎯 Fetching initial image for {anime_name}", user_info or {})
    post = await fetch_rule34_media(anime_name, "image", user_info)
    if not post:
        log_with_user_info("ERROR", f"❌ Failed to fetch initial image for {anime_name}", user_info or {})
        return None

    log_with_user_info("INFO", f"✅ Successfully fetched initial image: {post['id']} for {anime_name}", user_info or {})

    try:
        log_with_user_info("DEBUG", f"⌨️ Creating media selection keyboard for {anime_name}", user_info or {})
        keyboard = create_media_selection_keyboard(anime_name)
        log_with_user_info("DEBUG", f"✅ Media selection keyboard created", user_info or {})

        log_with_user_info("DEBUG", f"📝 Formatting caption for {title}", user_info or {})
        caption = BOT_MESSAGES["media_selection"].format(title=title)
        log_with_user_info("DEBUG", f"📄 Caption length: {len(caption)} characters", user_info or {})

        log_with_user_info("DEBUG", f"📤 Sending upload photo action to chat {chat_id}", user_info or {})
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
        log_with_user_info("DEBUG", f"✅ Upload photo action sent", user_info or {})

        log_with_user_info("DEBUG", f"📸 Sending media selection photo to chat {chat_id}", user_info or {})
        sent_msg = await bot.send_photo(
            chat_id=chat_id,
            photo=post['url'],
            caption=caption,
            reply_markup=keyboard,
            has_spoiler=True
        )
        log_with_user_info("INFO", f"✅ Media selection sent successfully for {anime_name} to chat {chat_id}, message ID: {sent_msg.message_id}", user_info or {})
        return sent_msg

    except Exception as e:
        log_with_user_info("ERROR", f"❌ Failed to send media selection for {anime_name} to chat {chat_id}: {str(e)}", user_info or {})
        log_with_user_info("ERROR", f"❌ Error details - URL: {post['url']}, Title: {title}", user_info or {})
        return None

async def send_random_media(chat_id: int, message_id: int | None = None, edit_mode: bool = False, media_type: str = "image", page: int = 1):
    """Send or edit random media with retry system (matching anime command style)"""
    try:
        attempts = 0
        post = None

        while attempts < 3 and not post:
            await asyncio.sleep(0.001)
            post = await fetch_random_content(media_type)
            attempts += 1

        if not post:
            post = await fetch_random_content("image")
        if not post:
            return None

        keyboard = create_random_navigation_keyboard(media_type, page)
        caption = BOT_MESSAGES["random_media_caption"].format(media_type_title=media_type.title())

        if edit_mode and message_id:
            if media_type == "video":
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaVideo(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
            elif media_type == "gif":
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaAnimation(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
            else:
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaPhoto(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
        else:
            if media_type == "video":
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_VIDEO)
            else:
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)

            if media_type == "video":
                await bot.send_video(
                    chat_id=chat_id,
                    video=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    has_spoiler=True
                )
            elif media_type == "gif":
                await bot.send_animation(
                    chat_id=chat_id,
                    animation=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    has_spoiler=True
                )
            else:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    has_spoiler=True
                )

        return True
    except Exception as e:
        logger.error(f"❌ Failed to send random media: {str(e)}")
        return None

async def send_search_media(search_query: str, chat_id: int, message_id: int | None = None, edit_mode: bool = False, media_type: str = "image", page: int = 1):
    """Send or edit search media with retry system (matching anime command style)"""
    try:
        post = await search_rule34_live(search_query, media_type)
        if not post:
            return None

        keyboard = create_search_navigation_keyboard(search_query, media_type, page)
        caption = BOT_MESSAGES["search_media_caption"].format(search_query=search_query)

        if edit_mode and message_id:
            if media_type == "video":
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaVideo(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
            elif media_type == "gif":
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaAnimation(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
            else:
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaPhoto(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
        else:
            if media_type == "video":
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_VIDEO)
            else:
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)

            if media_type == "video":
                await bot.send_video(
                    chat_id=chat_id,
                    video=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    has_spoiler=True
                )
            elif media_type == "gif":
                await bot.send_animation(
                    chat_id=chat_id,
                    animation=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    has_spoiler=True
                )
            else:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    has_spoiler=True
                )

        return True
    except Exception as e:
        logger.error(f"❌ Failed to send search media: {str(e)}")
        return None

async def send_anime_media(anime_name: str, chat_id: int, user_info: Dict[str, Any] = None, message_id: int | None = None, edit_mode: bool = False, media_type: str = "image", page: int = 1):
    """Send or edit anime media with retry system"""
    log_with_user_info("INFO", f"🎬 Starting anime media send for {anime_name}, type: {media_type}, edit_mode: {edit_mode}, page: {page}", user_info or {})

    anime_data = ANIME_COMMANDS.get(anime_name)
    if not anime_data:
        log_with_user_info("ERROR", f"❌ Anime '{anime_name}' not found in ANIME_COMMANDS", user_info or {})
        return None

    title = anime_data["title"]
    log_with_user_info("DEBUG", f"📝 Anime title: {title}", user_info or {})

    media_emoji = {"image": "🖼️", "video": "🎬", "gif": "🎨"}
    log_with_user_info("DEBUG", f"🎭 Media emoji for {media_type}: {media_emoji.get(media_type, '❓')}", user_info or {})

    post = None
    log_with_user_info("INFO", f"🔄 Starting retry loop with up to 15 attempts for {anime_name}", user_info or {})

    for attempt in range(15):
        log_with_user_info("DEBUG", f"🎯 Attempt {attempt + 1}/15 for {anime_name} {media_type}", user_info or {})
        post = await fetch_rule34_media(anime_name, media_type, user_info)
        if post:
            log_with_user_info("INFO", f"✅ Successfully fetched {media_type} on attempt {attempt + 1}: {post['id']}", user_info or {})
            break

        if attempt >= 10 and media_type in ["video", "gif"]:
            log_with_user_info("WARNING", f"⚠️ Attempt {attempt + 1}: Falling back to image for {media_type}", user_info or {})
            post = await fetch_rule34_media(anime_name, "image", user_info)
            if post:
                log_with_user_info("INFO", f"✅ Fallback to image successful on attempt {attempt + 1}: {post['id']}", user_info or {})
                break

    if not post:
        log_with_user_info("ERROR", f"❌ Complete failure: No media found for {anime_name} after 15 attempts", user_info or {})
        return None

    log_with_user_info("INFO", f"🎉 Media ready for sending: {post['type']} with ID {post['id']}, score {post['score']}", user_info or {})

    try:
        log_with_user_info("DEBUG", f"⌨️ Creating navigation keyboard for {anime_name}", user_info or {})
        keyboard = create_media_navigation_keyboard(anime_name, media_type, page)
        log_with_user_info("DEBUG", f"✅ Navigation keyboard created", user_info or {})

        log_with_user_info("DEBUG", f"📝 Formatting caption for {title}", user_info or {})
        caption = BOT_MESSAGES["anime_media_caption"].format(
            title=title, 
            media_emoji=MEDIA_EMOJIS.get(media_type, '')
        )
        log_with_user_info("DEBUG", f"📄 Caption: {caption}", user_info or {})

        if edit_mode and message_id is not None:
            log_with_user_info("INFO", f"✏️ Edit mode: Updating message {message_id} with {media_type}", user_info or {})

            if media_type == "video":
                log_with_user_info("DEBUG", f"🎬 Editing message with video", user_info or {})
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaVideo(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
                log_with_user_info("INFO", f"✅ Video message edited successfully", user_info or {})
            elif media_type == "gif":
                log_with_user_info("DEBUG", f"🎨 Editing message with GIF", user_info or {})
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaAnimation(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
                log_with_user_info("INFO", f"✅ GIF message edited successfully", user_info or {})
            else:
                log_with_user_info("DEBUG", f"🖼️ Editing message with image", user_info or {})
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaPhoto(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
                log_with_user_info("INFO", f"✅ Image message edited successfully", user_info or {})
            return None
        else:
            log_with_user_info("INFO", f"📤 Send mode: Creating new message with {media_type}", user_info or {})

            if media_type == "video":
                log_with_user_info("DEBUG", f"📤 Sending upload video action", user_info or {})
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_VIDEO)
            else:
                log_with_user_info("DEBUG", f"📤 Sending upload photo action", user_info or {})
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)

            if media_type == "video":
                log_with_user_info("DEBUG", f"🎬 Sending video message", user_info or {})
                sent_msg = await bot.send_video(
                    chat_id=chat_id,
                    video=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    supports_streaming=True,
                    has_spoiler=True
                )
                log_with_user_info("INFO", f"✅ Video sent successfully, message ID: {sent_msg.message_id}", user_info or {})
            elif media_type == "gif":
                log_with_user_info("DEBUG", f"🎨 Sending GIF message", user_info or {})
                sent_msg = await bot.send_animation(
                    chat_id=chat_id,
                    animation=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    has_spoiler=True
                )
                log_with_user_info("INFO", f"✅ GIF sent successfully, message ID: {sent_msg.message_id}", user_info or {})
            else:
                log_with_user_info("DEBUG", f"🖼️ Sending image message", user_info or {})
                sent_msg = await bot.send_photo(
                    chat_id=chat_id,
                    photo=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    has_spoiler=True
                )
                log_with_user_info("INFO", f"✅ Image sent successfully, message ID: {sent_msg.message_id}", user_info or {})
            return sent_msg

    except Exception as e:
        log_with_user_info("ERROR", f"❌ Failed to send anime media for {anime_name}: {str(e)}", user_info or {})
        log_with_user_info("ERROR", f"❌ Error details - Media type: {media_type}, Edit mode: {edit_mode}, Post URL: {post['url']}", user_info or {})
        return None

async def fetch_random_content(media_type: str = "image"):
    """Fetch completely random content from Rule34"""
    log_with_user_info("INFO", f"🎲 Fetching random content type: {media_type}")
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                "page": "dapi",
                "s": "post",
                "q": "index",
                "tags": "",
                "limit": 50,
                "pid": random.randint(0, 100) + int(time.time()) % 100,
                "api_key": R34_API_KEY,
                "user_id": R34_USER_ID
            }

            async with session.get(RULE34_API_BASE, params=params) as response:
                if response.status == 200:
                    xml_content = await response.text()

                    try:
                        root = ET.fromstring(xml_content)
                        posts = []

                        for post in root.findall('.//post'):
                            file_url = post.get('file_url')
                            if file_url and file_url.startswith(('http://', 'https://')):
                                if media_type == "image" and file_url.lower().endswith(('.jpg', '.jpeg', '.webp', '.png')):
                                    # Prefer non-PNG formats for better compatibility
                                    priority = 1 if file_url.lower().endswith('.png') else 2
                                    posts.append({
                                        'url': file_url,
                                        'id': post.get('id'),
                                        'tags': post.get('tags', ''),
                                        'score': int(post.get('score', 0)),
                                        'type': 'image',
                                        'priority': priority
                                    })
                                elif media_type == "gif" and file_url.lower().endswith('.gif'):
                                    posts.append({
                                        'url': file_url,
                                        'id': post.get('id'),
                                        'tags': post.get('tags', ''),
                                        'score': int(post.get('score', 0)),
                                        'type': 'gif'
                                    })
                                elif media_type == "video" and file_url.lower().endswith(('.mp4', '.webm', '.mov')):
                                    posts.append({
                                        'url': file_url,
                                        'id': post.get('id'),
                                        'tags': post.get('tags', ''),
                                        'score': int(post.get('score', 0)),
                                        'type': 'video'
                                    })

                        if posts:
                            random.seed(int(time.time() * 1000000) % 1000000)

                            # Sort by priority then score for better compatibility
                            posts.sort(key=lambda x: (x.get('priority', 1), x['score']), reverse=True)
                            top_posts = posts[:50]
                            selected = random.choice(top_posts)
                            return selected
                    except ET.ParseError as e:
                        logger.error(f"❌ XML parsing error during random fetch: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Exception during random content fetch: {str(e)}")

    return None

async def search_rule34_live(search_query: str, media_type: str = "image"):
    """Search Rule34 API with user's custom query - Enhanced with smart tag conversion"""
    log_with_user_info("INFO", f"🔍 Starting live search for query: '{search_query}', media_type: {media_type}")

    try:
        clean_query = search_query.lower().strip()
        log_with_user_info("DEBUG", f"🧹 Cleaned query: '{clean_query}'")

        tag_conversions = {
            "kushina uzumaki": "kushina_uzumaki",
            "hinata hyuga": "hinata_hyuga", 
            "sakura haruno": "sakura_haruno",
            "ino yamanaka": "ino_yamanaka",
            "temari nara": "temari",
            "tsunade senju": "tsunade",
            "rukia kuchiki": "rukia_kuchiki",
            "orihime inoue": "orihime_inoue",
            "yoruichi shihouin": "yoruichi_shihouin",
            "rangiku matsumoto": "rangiku_matsumoto",
            "mikasa ackerman": "mikasa_ackerman",
            "annie leonhart": "annie_leonhart",
            "historia reiss": "historia_reiss",
            "sasha blouse": "sasha_blouse",
            "nezuko kamado": "nezuko_kamado",
            "shinobu kocho": "shinobu_kocho",
            "mitsuri kanroji": "mitsuri_kanroji",
            "nobara kugisaki": "nobara_kugisaki",
            "maki zenin": "maki_zenin",
            "power chainsaw": "power",
            "makima chainsaw": "makima",
            "yor forger": "yor_forger",
            "anya forger": "anya_forger",
            "naruto shippuden": "naruto",
            "attack on titan": "shingeki_no_kyojin", 
            "demon slayer": "kimetsu_no_yaiba",
            "my hero academia": "my_hero_academia",
            "jujutsu kaisen": "jujutsu_kaisen",
            "spy x family": "spy_x_family",
            "chainsaw man": "chainsaw_man",
            "one piece": "one_piece",
            "love is war": "kaguya-sama_wa_kokurasetai",
            "dress up darling": "sono_bisque_doll_wa_koi_wo_suru",
            "rent a girlfriend": "kanojo_okarishimasu",
            "one punch man": "one-punch_man",
            "dr stone": "dr._stone",
            "tower of god": "tower_of_god",
            "school uniform": "school_uniform",
            "gym uniform": "gym_uniform",
            "swim suit": "swimsuit",
            "maid outfit": "maid",
            "cat girl": "cat_girl",
            "fox girl": "fox_girl",
            "big breasts": "large_breasts",
            "small breasts": "small_breasts",
            "long hair": "long_hair",
            "short hair": "short_hair",
            "blonde hair": "blonde_hair",
            "brown hair": "brown_hair",
            "black hair": "black_hair",
            "blue hair": "blue_hair",
            "red hair": "red_hair",
            "pink hair": "pink_hair",
            "blue eyes": "blue_eyes",
            "brown eyes": "brown_eyes",
            "green eyes": "green_eyes",
            "red eyes": "red_eyes",
            "purple eyes": "purple_eyes"
        }

        formatted_query = clean_query
        for original, converted in tag_conversions.items():
            if original in formatted_query:
                formatted_query = formatted_query.replace(original, converted)

        formatted_query = formatted_query.replace(" ", "_")

        async with aiohttp.ClientSession() as session:
            params = {
                "page": "dapi",
                "s": "post",
                "q": "index",
                "tags": formatted_query,
                "limit": 100,
                "pid": random.randint(0, 100) + int(time.time()) % 100,
                "api_key": R34_API_KEY,
                "user_id": R34_USER_ID
            }

            async with session.get(RULE34_API_BASE, params=params) as response:
                if response.status == 200:
                    xml_content = await response.text()

                    try:
                        root = ET.fromstring(xml_content)
                        posts = []

                        for post in root.findall('.//post'):
                            file_url = post.get('file_url')
                            if file_url and file_url.startswith(('http://', 'https://')):
                                # Check image formats with PNG compatibility
                                if media_type == "image" and file_url.lower().endswith(('.jpg', '.jpeg', '.webp', '.png')):
                                    # Prefer non-PNG formats for telegram compatibility
                                    priority = 1 if file_url.lower().endswith('.png') else 2
                                    posts.append({
                                        'url': file_url,
                                        'id': post.get('id'),
                                        'tags': post.get('tags', ''),
                                        'score': int(post.get('score', 0)),
                                        'type': 'image',
                                        'priority': priority
                                    })
                                elif media_type == "gif" and file_url.lower().endswith('.gif'):
                                    posts.append({
                                        'url': file_url,
                                        'id': post.get('id'),
                                        'tags': post.get('tags', ''),
                                        'score': int(post.get('score', 0)),
                                        'type': 'gif'
                                    })
                                elif media_type == "video" and file_url.lower().endswith(('.mp4', '.webm', '.mov')):
                                    posts.append({
                                        'url': file_url,
                                        'id': post.get('id'),
                                        'tags': post.get('tags', ''),
                                        'score': int(post.get('score', 0)),
                                        'type': 'video'
                                    })

                        if posts:
                            random.seed(int(time.time() * 1000000) % 1000000)

                            # Sort by priority then score for better compatibility
                            posts.sort(key=lambda x: (x.get('priority', 1), x['score']), reverse=True)
                            top_posts = posts[:50]
                            selected = random.choice(top_posts)
                            return selected
                    except ET.ParseError as e:
                        logger.error(f"❌ XML parsing error during search: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Exception during search_rule34_live: {str(e)}")

    return None

def create_random_selection_keyboard():
    """Create media type selection keyboard for random content (like anime commands)"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=BUTTON_TEXTS["videos"], callback_data="select_video_random"),
            InlineKeyboardButton(text=BUTTON_TEXTS["images"], callback_data="select_image_random")
        ],
        [
            InlineKeyboardButton(text=BUTTON_TEXTS["animations"], callback_data="select_gif_random")
        ]
    ])
    return keyboard

def create_random_navigation_keyboard(media_type: str = "image", page: int = 1):
    """Create navigation keyboard for random content (matching anime command style)"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=BUTTON_TEXTS["refresh"], callback_data=f"update_random_{media_type}_{page}"),
            InlineKeyboardButton(text=BUTTON_TEXTS["next"], callback_data=f"next_random_{media_type}_{page}")
        ],
        [
            InlineKeyboardButton(text=BUTTON_TEXTS["back"], callback_data="back_random")
        ]
    ])
    return keyboard

def create_search_selection_keyboard(search_query: str):
    """Create media type selection keyboard for search results (like anime commands)"""
    encoded_query = search_query.replace(" ", "_")[:20]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=BUTTON_TEXTS["videos"], callback_data=f"select_video_{encoded_query}"),
            InlineKeyboardButton(text=BUTTON_TEXTS["images"], callback_data=f"select_image_{encoded_query}")
        ],
        [
            InlineKeyboardButton(text=BUTTON_TEXTS["animations"], callback_data=f"select_gif_{encoded_query}")
        ]
    ])
    return keyboard

def create_search_navigation_keyboard(search_query: str, media_type: str = "image", page: int = 1):
    """Create navigation keyboard for search results (matching anime command style)"""
    encoded_query = search_query.replace(" ", "_")[:20]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=BUTTON_TEXTS["refresh"], callback_data=f"update_{encoded_query}_{media_type}_{page}"),
            InlineKeyboardButton(text=BUTTON_TEXTS["next"], callback_data=f"next_{encoded_query}_{media_type}_{page}")
        ],
        [
            InlineKeyboardButton(text=BUTTON_TEXTS["back"], callback_data=f"back_{encoded_query}")
        ]
    ])
    return keyboard

def make_anime_handler(anime_name):
    async def handler(msg: Message):
        user_info = extract_user_info(msg)
        if msg.from_user and should_check_membership(msg.from_user.id):
            if not check_membership(msg.from_user.id):
                log_with_user_info("WARNING", "🚫 User failed membership check", user_info)
                await send_membership_reminder(msg.chat.id, msg.from_user.id, msg.from_user.full_name)
                return
        await send_media_selection(anime_name, msg.chat.id, user_info)
    return handler

for anime_name in ANIME_COMMANDS:
    dp.message.register(make_anime_handler(anime_name), Command(anime_name))

@dp.message(Command("start"))
async def cmd_start(msg: Message):
    user_info = extract_user_info(msg)
    log_with_user_info("INFO", "🌟 /start command received", user_info)

    await bot.send_chat_action(msg.chat.id, action="upload_photo")

    if msg.from_user and should_check_membership(msg.from_user.id):
        if not check_membership(msg.from_user.id):
            log_with_user_info("WARNING", "🚫 User failed membership check, sending reminder", user_info)
            await send_membership_reminder(
                chat_id=msg.chat.id,
                user_id=msg.from_user.id,
                user_name=msg.from_user.full_name
            )
            return

    user_name = msg.from_user.full_name if msg.from_user else "User"
    user_id = msg.from_user.id if msg.from_user else ""

    try:
        bot_info = await bot.get_me()
        bot_username = bot_info.username
        logger.debug(f"🤖 Bot info retrieved: @{bot_username}")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=BUTTON_TEXTS["updates"], url=URLS["channel"]),
                InlineKeyboardButton(text=BUTTON_TEXTS["support"], url=URLS["group"])
            ],
            [
                InlineKeyboardButton(text=BUTTON_TEXTS["add_to_group"], url=f"https://t.me/{bot_username}?startgroup=true&admin=delete_messages+ban_users+invite_users+pin_messages+manage_chat+manage_video_chats+post_messages+edit_messages+manage_topics+add_admins")
            ]
        ])

        welcome_text = BOT_MESSAGES["welcome_text"].format(user_id=user_id, user_name=user_name)

        selected_image = random.choice(MAKIMA_IMAGES)
        logger.debug(f"🖼️ Selected welcome image: {selected_image}")

        await msg.answer_photo(
            photo=selected_image,
            caption=welcome_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

        log_with_user_info("INFO", "✅ Welcome message sent successfully", user_info)
    except Exception as e:
        log_with_user_info("ERROR", f"❌ Failed to send welcome message: {str(e)}", user_info)

async def send_random_selection(chat_id: int):
    """Send initial random content with media type selection buttons (like anime commands)"""

    await bot.send_chat_action(chat_id, action="upload_photo")

    post = await fetch_random_content("image")
    if not post:
        return None

    try:
        keyboard = create_random_selection_keyboard()
        caption = BOT_MESSAGES["random_selection"]

        await bot.send_photo(
            chat_id=chat_id,
            photo=post['url'],
            caption=caption,
            reply_markup=keyboard,
            has_spoiler=True
        )
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send random selection: {str(e)}")
        return None

@dp.message(Command("random"))
async def cmd_random(msg: Message):
    """Handle random content command"""
    user_info = extract_user_info(msg)
    log_with_user_info("INFO", "🎲 /random command received", user_info)

    if msg.from_user and should_check_membership(msg.from_user.id):
        if not check_membership(msg.from_user.id):
            log_with_user_info("WARNING", "🚫 User failed membership check for random command", user_info)
            await send_membership_reminder(msg.chat.id, msg.from_user.id, msg.from_user.full_name)
            return

    await bot.send_chat_action(msg.chat.id, action="upload_photo")
    logger.debug("🎬 Sending upload photo action for random command")

    try:
        await send_random_selection(msg.chat.id)
        log_with_user_info("INFO", "✅ Random content selection sent successfully", user_info)
    except Exception as e:
        log_with_user_info("ERROR", f"❌ Failed to send random content: {str(e)}", user_info)

@dp.message(Command("privacy"))
async def cmd_privacy(msg: Message):
    """Handle privacy mode command (owner only)"""
    global privacy_mode
    user_info = extract_user_info(msg)

    if not msg.from_user:
        logger.warning("⚠️ Privacy command received from unknown user")
        return

    user_id = msg.from_user.id
    full_name = msg.from_user.full_name if msg.from_user else "Unknown User"

    if user_id != OWNER_ID:
        log_with_user_info("WARNING", "🚫 Non-owner attempted to access privacy command", user_info)
        return

    log_with_user_info("INFO", "👑 Owner accessed privacy command", user_info)

    await bot.send_chat_action(msg.chat.id, ChatAction.TYPING)

    current_mode = privacy_mode
    mode_emoji = "🔓" if current_mode == "public" else "🔒"
    mode_text = "Public" if current_mode == "public" else "Normal (Membership Required)"

    logger.info(f"🔧 Current privacy mode: {mode_text}")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔓 Set Public Mode" if current_mode == "normal" else "🔓 Public Mode ✓", 
                callback_data="privacy_public"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔒 Set Normal Mode" if current_mode == "public" else "🔒 Normal Mode ✓", 
                callback_data="privacy_normal"
            )
        ],
        [
            InlineKeyboardButton(text="📊 View Status", callback_data="privacy_status")
        ]
    ])

    privacy_text = f"""
🔐 <b>Privacy Mode Settings</b>

<b>Current Mode:</b> {mode_emoji} <b>{mode_text}</b>

<blockquote>╭─<b> 🔓 Public Mode</b>
├─ Everyone can use the bot
├─ No membership requirements
╰─ Works in groups and private chats</blockquote>

<blockquote>╭─<b> 🔒 Normal Mode</b>
├─ Membership verification required
├─ Users must join channel & group
╰─ Default secure behavior</blockquote>

<b>👑 Owner always has full access regardless of mode</b>
"""

    try:
        await msg.answer(privacy_text, reply_markup=keyboard)
        log_with_user_info("INFO", "✅ Privacy settings sent successfully", user_info)
    except Exception as e:
        log_with_user_info("ERROR", f"❌ Failed to send privacy settings: {str(e)}", user_info)

@dp.message(F.text == "/ping")
async def ping_command(msg: Message):
    """Respond with latency - works for everyone, replies in groups, direct message in private"""
    user_info = extract_user_info(msg)
    log_with_user_info("INFO", "🏓 /ping command received", user_info)

    try:
        start = time.perf_counter()

        if msg.chat.type == "private":
            response = await msg.answer("🛰️ Pinging...")
            logger.debug("📱 Ping response sent in private chat")
        else:
            response = await msg.reply("🛰️ Pinging...")
            logger.debug("👥 Ping response sent in group chat")

        end = time.perf_counter()
        latency_ms = (end - start) * 1000

        await response.edit_text(
            f"🏓 <a href='https://t.me/SoulMeetsHQ'>Pong!</a> {latency_ms:.2f}ms",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )

        log_with_user_info("INFO", f"✅ Ping completed - latency: {latency_ms:.2f}ms", user_info)

    except Exception as e:
        log_with_user_info("ERROR", f"❌ Ping command failed: {str(e)}", user_info)

@dp.message(F.chat.type == "private")
async def handle_live_search(msg: Message):
    """Handle live search in private messages"""
    user_info = extract_user_info(msg)

    log_with_user_info("DEBUG", f"💬 Private message received from user {user_info.get('user_id', 'unknown')}")

    if msg.from_user and should_check_membership(msg.from_user.id):
        log_with_user_info("DEBUG", f"🔐 Checking membership for user {msg.from_user.id}")
        if not check_membership(msg.from_user.id):
            log_with_user_info("WARNING", "🚫 User failed membership check for live search", user_info)
            await send_membership_reminder(msg.chat.id, msg.from_user.id, msg.from_user.full_name)
            return
        log_with_user_info("DEBUG", f"✅ Membership check passed for user {msg.from_user.id}")

    if not msg.text:
        log_with_user_info("DEBUG", f"⏭️ Skipping non-text message")
        return

    if msg.text.startswith('/'):
        log_with_user_info("DEBUG", f"⏭️ Skipping command message: {msg.text}")
        return

    search_text = msg.text.strip()
    if not search_text:
        log_with_user_info("DEBUG", f"⏭️ Skipping empty search text")
        return

    log_with_user_info("INFO", f"🔍 Live search initiated: '{search_text}'", user_info)

    words = search_text.split()
    if len(words) == 1:
        search_query = words[0].lower()

        if search_query in ANIME_COMMANDS:
            log_with_user_info("INFO", f"✅ Direct anime command match found: {search_query}", user_info)
            await send_media_selection(search_query, msg.chat.id, user_info)
            return

    guidance_text = BOT_MESSAGES["search_guidance"].format(search_text=search_text)

    guidance_msg = await msg.answer(guidance_text)

    post = await search_rule34_live(search_text, "image")

    if not post and " " in search_text:
        alt_search = search_text.replace(" ", "_")
        post = await search_rule34_live(alt_search, "image")

    if not post and len(search_text.split()) > 1:
        first_word = search_text.split()[0]
        post = await search_rule34_live(first_word, "image")

    if not post and len(search_text.split()) > 1:
        last_word = search_text.split()[-1]
        post = await search_rule34_live(last_word, "image")

    if not post:
        clean_name = search_text.replace(" uzumaki", "").replace(" uchiha", "").replace(" hyuga", "").replace(" kamado", "").replace(" kuchiki", "")
        if clean_name != search_text:
            post = await search_rule34_live(clean_name, "image")

    if not post:
        search_underscore = search_text.replace(" ", "_")
        no_results_text = BOT_MESSAGES["no_results"].format(search_text=search_text, search_underscore=search_underscore)

        await bot.edit_message_text(
            text=no_results_text,
            chat_id=msg.chat.id,
            message_id=guidance_msg.message_id
        )
        return

    try:
        await bot.delete_message(msg.chat.id, guidance_msg.message_id)

        keyboard = create_search_selection_keyboard(search_text)
        caption = BOT_MESSAGES["search_selection"].format(search_text=search_text)

        await bot.send_chat_action(msg.chat.id, action="upload_photo")

        await bot.send_photo(
            chat_id=msg.chat.id,
            photo=post['url'],
            caption=caption,
            reply_markup=keyboard,
            has_spoiler=True
        )
    except Exception as e:
        log_with_user_info("ERROR", f"❌ Failed to send search result: {str(e)}", user_info)

@dp.callback_query()
async def handle_callbacks(callback: CallbackQuery):
    """Handle all callback queries with membership verification for the new media selection workflow"""
    user_info = extract_user_info(callback.message) if callback.message else {}

    log_with_user_info("INFO", f"🔘 Callback query received: {callback.data}", user_info)
    log_with_user_info("INFO", f"📱 Callback button pressed: {callback.data}", user_info)

    if not callback.data or not callback.message:
        log_with_user_info("WARNING", f"⚠️ Invalid callback query - data: {callback.data}, message: {callback.message}")
        await callback.answer("Invalid button")
        return

    if callback.data == "check_membership":
        user_id = callback.from_user.id
        if check_membership(user_id):
            await callback.answer(CALLBACK_ANSWERS["membership_success"], show_alert=True)
            try:
                response_text = BOT_MESSAGES["membership_success"]

                if callback.message.content_type == "photo":
                    await bot.edit_message_caption(
                        caption=response_text,
                        chat_id=callback.message.chat.id,
                        message_id=callback.message.message_id,
                        parse_mode="HTML"
                    )
                else:
                    await bot.edit_message_text(
                        text=response_text,
                        chat_id=callback.message.chat.id,
                        message_id=callback.message.message_id,
                        parse_mode="HTML"
                    )
            except Exception as e:
                log_with_user_info("ERROR", f"❌ Failed to update message after membership success: {str(e)}", user_info)
        else:
            await callback.answer(CALLBACK_ANSWERS["membership_failed"], show_alert=True)
        return

    if callback.data.startswith('privacy_'):
        global privacy_mode

        if callback.from_user.id != OWNER_ID:
            await callback.answer(CALLBACK_ANSWERS["privacy_restricted"], show_alert=True)
            return

        if callback.data == "privacy_public":
            privacy_mode = "public"
            await callback.answer(CALLBACK_ANSWERS["privacy_public"])

        elif callback.data == "privacy_normal":
            privacy_mode = "normal"
            await callback.answer(CALLBACK_ANSWERS["privacy_normal"])

        elif callback.data == "privacy_status":
            mode_text = "Public (Everyone)" if privacy_mode == "public" else "Normal (Membership Required)"
            await callback.answer(f"📊 Current mode: {mode_text}", show_alert=True)
            return

        current_mode = privacy_mode
        mode_emoji = "🔓" if current_mode == "public" else "🔒"
        mode_text = "Public" if current_mode == "public" else "Normal (Membership Required)"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔓 Set Public Mode" if current_mode == "normal" else "🔓 Public Mode ✓", 
                    callback_data="privacy_public"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔒 Set Normal Mode" if current_mode == "public" else "🔒 Normal Mode ✓", 
                    callback_data="privacy_normal"
                )
            ],
            [
                InlineKeyboardButton(text="📊 View Status", callback_data="privacy_status")
            ]
        ])

        privacy_text = BOT_MESSAGES["privacy_settings"].format(mode_emoji=mode_emoji, mode_text=mode_text)

        try:
            await bot.edit_message_text(
                text=privacy_text,
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reply_markup=keyboard
            )
        except Exception as e:
            log_with_user_info("ERROR", f"❌ Failed to update privacy settings message: {str(e)}", user_info)
        return

    if callback.from_user and should_check_membership(callback.from_user.id):
        if not check_membership(callback.from_user.id):
            await callback.answer(CALLBACK_ANSWERS["membership_required"], show_alert=True)

            await send_membership_reminder(
                chat_id=callback.message.chat.id,
                user_id=callback.from_user.id,
                user_name=callback.from_user.full_name
            )
            return

    data_parts = callback.data.split("_")
    action = data_parts[0]

    if len(data_parts) < 2:
        await callback.answer("Invalid button format")
        return

    if action == "select":
        media_type = data_parts[1]
        target = data_parts[2]

        if target == "random":
            await callback.answer(CALLBACK_ANSWERS["loading_random"].format(media_type=media_type))
            try:
                await send_random_media(
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                    edit_mode=True,
                    media_type=media_type,
                    page=1
                )
            except Exception as e:
                log_with_user_info("ERROR", f"❌ Failed to load random media: {str(e)}", user_info)
                await callback.answer("Failed to load random content", show_alert=True)
        elif target in ANIME_COMMANDS:
            await callback.answer(CALLBACK_ANSWERS["loading_content"].format(media_type=media_type))
            try:
                await send_anime_media(
                    anime_name=target,
                    chat_id=callback.message.chat.id,
                    user_info=user_info,
                    message_id=callback.message.message_id,
                    edit_mode=True,
                    media_type=media_type,
                    page=1
                )
            except Exception as e:
                log_with_user_info("ERROR", f"❌ Failed to load anime media: {str(e)}", user_info)
                await callback.answer("Failed to load anime content", show_alert=True)
        else:
            search_query = target.replace("_", " ")
            await callback.answer(CALLBACK_ANSWERS["loading_search"].format(media_type=media_type, search_query=search_query))
            try:
                await send_search_media(
                    search_query=search_query,
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                    edit_mode=True,
                    media_type=media_type,
                    page=1
                )
            except Exception as e:
                log_with_user_info("ERROR", f"❌ Failed to load search media: {str(e)}", user_info)
                await callback.answer("Failed to load search content", show_alert=True)

    elif action in ["update", "next"]:
        target = data_parts[1]
        media_type = data_parts[2] if len(data_parts) > 2 else "image"
        page = int(data_parts[3]) if len(data_parts) > 3 else 1

        if action == "update":
            await callback.answer(CALLBACK_ANSWERS["fresh_content"])

            try:
                if target == "random":
                    await send_random_media(
                        chat_id=callback.message.chat.id,
                        message_id=callback.message.message_id,
                        edit_mode=True,
                        media_type=media_type,
                        page=page
                    )
                elif target in ANIME_COMMANDS:
                    await send_anime_media(
                        anime_name=target,
                        chat_id=callback.message.chat.id,
                        user_info=user_info,
                        message_id=callback.message.message_id,
                        edit_mode=True,
                        media_type=media_type,
                        page=page
                    )
                else:
                    search_query = target.replace("_", " ")
                    await send_search_media(
                        search_query=search_query,
                        chat_id=callback.message.chat.id,
                        message_id=callback.message.message_id,
                        edit_mode=True,
                        media_type=media_type,
                        page=page
                    )
            except Exception as e:
                log_with_user_info("ERROR", f"❌ Failed to update media: {str(e)}", user_info)
                await callback.answer("Failed to refresh content", show_alert=True)

        elif action == "next":
            await callback.answer(CALLBACK_ANSWERS["more_content"])

            try:
                if target == "random":
                    await send_random_media(
                        chat_id=callback.message.chat.id,
                        edit_mode=False,
                        media_type=media_type,
                        page=page + 1
                    )
                elif target in ANIME_COMMANDS:
                    await send_anime_media(
                        anime_name=target,
                        chat_id=callback.message.chat.id,
                        user_info=user_info,
                        edit_mode=False,
                        media_type=media_type,
                        page=page + 1
                    )
                else:
                    search_query = target.replace("_", " ")
                    await send_search_media(
                        search_query=search_query,
                        chat_id=callback.message.chat.id,
                        edit_mode=False,
                        media_type=media_type,
                        page=page + 1
                    )
            except Exception as e:
                log_with_user_info("ERROR", f"❌ Failed to load more media: {str(e)}", user_info)
                await callback.answer("Failed to load more content", show_alert=True)

    elif callback.data == "back_to_menu":
        await callback.answer(CALLBACK_ANSWERS["back_to_menu"])

        user_name = callback.from_user.full_name if callback.from_user else "User"
        user_id = callback.from_user.id if callback.from_user else ""

        welcome_text = BOT_MESSAGES["welcome_text"].format(user_id=user_id, user_name=user_name)

        bot_info = await bot.get_me()
        bot_username = bot_info.username

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=BUTTON_TEXTS["updates"], url=URLS["channel"]),
                InlineKeyboardButton(text=BUTTON_TEXTS["support"], url=URLS["group"])
            ],
            [
                InlineKeyboardButton(text=BUTTON_TEXTS["add_to_group"], url=f"https://t.me/{bot_username}?startgroup=true&admin=delete_messages+ban_users+invite_users+pin_messages+manage_chat+manage_video_chats+post_messages+edit_messages+manage_topics+add_admins")
            ]
        ])

        try:
            await bot.edit_message_text(
                text=welcome_text,
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reply_markup=keyboard
            )
        except Exception as e:
            log_with_user_info("ERROR", f"❌ Failed to return to menu: {str(e)}", user_info)
            await callback.answer("Failed to return to menu", show_alert=True)
        return

    elif action == "back":
        target = data_parts[1]
        await callback.answer(CALLBACK_ANSWERS["back_to_selection"])

        try:
            if target == "random":
                keyboard = create_random_selection_keyboard()
                caption = BOT_MESSAGES["random_selection"]
            elif target in ANIME_COMMANDS:
                anime_data = ANIME_COMMANDS.get(target)
                keyboard = create_media_selection_keyboard(target)
                if anime_data:
                    caption = BOT_MESSAGES["media_selection"].format(title=anime_data['title'])
                else:
                    caption = BOT_MESSAGES["media_selection"].format(title=target.title())
            else:
                search_query = target.replace("_", " ")
                keyboard = create_search_selection_keyboard(search_query)
                caption = BOT_MESSAGES["search_selection"].format(search_text=search_query)

            await bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=caption,
                reply_markup=keyboard
            )
        except Exception as e:
            log_with_user_info("ERROR", f"❌ Failed to go back: {str(e)}", user_info)
            await callback.answer("Failed to go back", show_alert=True)

    else:
        await callback.answer("Unknown button")

async def main():
    logger.info("🚀 Starting bot...")
    logger.debug("🔧 Initializing HTTP server thread...")

    threading.Thread(target=start_dummy_server, daemon=True).start()
    logger.debug("✅ HTTP server thread started successfully")

    try:
        await bot.set_my_commands(BOT_COMMANDS)
        logger.info("✅ Bot commands set successfully.")

        logger.info("🎯 Starting polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Fatal error in main: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("🌸 Makima Bot initializing...")
    logger.debug("🔄 Starting asyncio event loop...")
    asyncio.run(main())
