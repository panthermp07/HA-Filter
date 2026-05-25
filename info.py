import os
import re
import logging
from os import environ
from Script import script

logger = logging.getLogger(__name__)

def is_enabled(type, value):
    data = environ.get(type, str(value))
    if data.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif data.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        logger.error(f'{type} is invalid, exiting now')
        exit()

def is_valid_ip(ip):
    ip_pattern = r'\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    return re.match(ip_pattern, ip) is not None

# BOT INFORMATION
API_ID = environ.get('API_ID', '')
API_HASH = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', '')
PORT = int(environ.get('PORT', '8080'))

# Upload your images to "postimages.org" and get direct link
PICS = (environ.get('PICS', 'https://i.ibb.co/gFRnRvwy/photo-2026-05-04-10-32-00-7635982760254898208.jpg https://i.ibb.co/FkvYMqP5/photo-2026-05-04-10-44-04-7635985642177953808.jpg')).split()

# Bot Admins
ADMINS = environ.get('ADMINS', '')

# Channels
INDEX_CHANNELS = [int(index_channels) if index_channels.startswith("-") else index_channels for index_channels in environ.get('INDEX_CHANNELS', '').split()]
LOG_CHANNEL = environ.get('LOG_CHANNEL', '')
SUPPORT_GROUP = environ.get('SUPPORT_GROUP', '')
UPDATES_SEND_CHANNEL = environ.get('UPDATES_SEND_CHANNEL', '-1003982751488')
VERIFICATION_NOTIFY_CHANNEL = environ.get('VERIFICATION_NOTIFY_CHANNEL', '')

# ==========================================
# 3. MONGODB INFORMATION
# ==========================================
DATA_DATABASE_URL = environ.get('DATA_DATABASE_URL', "")
FILES_DATABASE_URL = environ.get('FILES_DATABASE_URL', "")
SECOND_FILES_DATABASE_URL = environ.get('SECOND_FILES_DATABASE_URL', "")
DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Files')

# Links
SUPPORT_LINK = environ.get('SUPPORT_LINK', 'https://t.me/talk_mrs_bot')
UPDATES_LINK = environ.get('UPDATES_LINK', 'https://t.me/infinity_botzz')
FILMS_LINK = environ.get('FILMS_LINK', 'https://t.me/infinity_botzz')
TUTORIAL = environ.get("TUTORIAL", "https://t.me/infinity_botzz")
VERIFY_TUTORIAL = environ.get("VERIFY_TUTORIAL", "https://t.me/infinity_botzz")

# Bot settings
TIME_ZONE = environ.get('TIME_ZONE', 'Asia/Kolkata')
DELETE_TIME = int(environ.get('DELETE_TIME', 3600))
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
MAX_BTN = int(environ.get('MAX_BTN', 8))
PM_FILE_DELETE_TIME = int(environ.get('PM_FILE_DELETE_TIME', '3600'))
VERIFY_EXPIRE = int(environ.get('VERIFY_EXPIRE', 86400))

# Massive Global Language & Quality Tags Array
LANGUAGES = [language.lower() for language in environ.get('LANGUAGES', 'hindi english telugu tamil kannada malayalam bengali marathi punjabi gujrati odia bhojpuri assamese urdu korean japanese chinese french spanish german russian arabic turkish portuguese thai dual multi org dubbed esub').split()]
QUALITY = [quality.lower() for quality in environ.get('QUALITY', '240p 360p 480p 576p 720p 1080p 1440p 2160p').split()]
INDEX_EXTENSIONS = [extensions.lower() for extensions in environ.get('INDEX_EXTENSIONS', 'mp4 mkv').split()]

IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", script.IMDB_TEMPLATE)
FILE_CAPTION = environ.get("FILE_CAPTION", script.FILE_CAPTION)
WELCOME_TEXT = environ.get("WELCOME_TEXT", script.WELCOME_TEXT)

SHORTLINK_URL = environ.get("SHORTLINK_URL", "")
SHORTLINK_API = environ.get("SHORTLINK_API", "")

# TMDB API
TMDB_API_KEY = environ.get("TMDB_API_KEY", "")

# Boolean settings
USE_CAPTION_FILTER = is_enabled('USE_CAPTION_FILTER', False)
IS_VERIFY = is_enabled('IS_VERIFY', True)
AUTO_DELETE = is_enabled('AUTO_DELETE', True)
WELCOME = is_enabled('WELCOME', True)
PROTECT_CONTENT = is_enabled('PROTECT_CONTENT', False)
LONG_IMDB_DESCRIPTION = is_enabled("LONG_IMDB_DESCRIPTION", False)
LINK_MODE = is_enabled("LINK_MODE", True)
IMDB = is_enabled('IMDB', False)
SPELL_CHECK = is_enabled("SPELL_CHECK", True)
SHORTLINK = is_enabled('SHORTLINK', False)
IS_STREAM = is_enabled('IS_STREAM', True)

# Streaming Configuration
BIN_CHANNEL = environ.get("BIN_CHANNEL", "")
URL = environ.get("URL", "")

# ==========================================
# 6. REACTIONS & EFFECTS (🆕 Public Update)
# ==========================================
REACTIONS = [reactions for reactions in environ.get('REACTIONS', '🤝 😇 🤗 😍 👍 🎅 😐 🥰 🤩 😱 🤣 😘 👏 😛 😈 🎉 ⚡️ 🫡 🤓 😎 🏆 🔥 🤭 🌚 🆒 👻 😁').split()]
# 🆕 Telegram Premium Message Effects Added
EFFECT_IDS = [effect for effect in environ.get('EFFECT_IDS', '5104841245755180586 5104858069142078462 5159385139981059251 5046509860389126442 5046589136895476101 5107584321108051014').split()]

# ==========================================
# 7. PREMIUM SETTINGS (UPI & 🆕 STARS/CRYPTO)
# ==========================================
IS_PREMIUM = is_enabled('IS_PREMIUM', True)
OWNER_USERNAME = environ.get("OWNER_USERNAME", "talk_mrs_bot")
PREMIUM_NOTIFY_CHANNEL = environ.get('PREMIUM_NOTIFY_CHANNEL', '')

# Your Custom UPI Integration (Retained)
PRE_DAY_AMOUNT = int(environ.get('PRE_DAY_AMOUNT', '1')) 
UPI_ID = environ.get("UPI_ID", "")
UPI_NAME = environ.get("UPI_NAME", "")
RECEIPT_SEND_USERNAME = environ.get("RECEIPT_SEND_USERNAME", "@talk_mrs_bot")

# 🆕 Global/Advanced Payment Configs (From Public Repo)
PAYMENT_QR_CODE = environ.get("PAYMENT_QR_CODE", "")
PAYMENT_ID = environ.get("PAYMENT_ID", "")
PAYMENT_TYPE = environ.get("PAYMENT_TYPE", "UPI")
PREMIUM_PLANS = {
    7: ['INR', 10], 
    30: ['INR', 40],
    90: ['INR', 109],
    180: ['INR', 199]
}


# ==========================================
# 8. VALIDATIONS (Execution Stops if Missing)
# ==========================================

if len(API_ID) == 0:
    logger.error('API_ID is missing, exiting now')
    exit()
else:
    API_ID = int(API_ID)

if len(API_HASH) == 0:
    logger.error('API_HASH is missing, exiting now')
    exit()

if len(BOT_TOKEN) == 0:
    logger.error('BOT_TOKEN is missing, exiting now')
    exit()

BOT_ID = BOT_TOKEN.split(":")[0]

if len(ADMINS) == 0:
    logger.error('ADMINS is missing, exiting now')
    exit()
else:
    ADMINS = [int(admins) for admins in ADMINS.split()]

if len(INDEX_CHANNELS) == 0:
    logger.info('INDEX_CHANNELS is empty')

if len(LOG_CHANNEL) == 0:
    logger.error('LOG_CHANNEL is missing, exiting now')
    exit()
else:
    LOG_CHANNEL = int(LOG_CHANNEL)

if len(SUPPORT_GROUP) == 0:
    logger.error('SUPPORT_GROUP is missing, exiting now')
    exit()
else:
    SUPPORT_GROUP = int(SUPPORT_GROUP)

if len(UPDATES_SEND_CHANNEL) == 0:
    logger.info('UPDATES_SEND_CHANNEL is missing')
    UPDATES_SEND_CHANNEL = None
else:
    UPDATES_SEND_CHANNEL = int(UPDATES_SEND_CHANNEL)

if len(DATA_DATABASE_URL) == 0:
    logger.error('DATA_DATABASE_URL is missing, exiting now')
    exit()

if len(FILES_DATABASE_URL) == 0:
    logger.error('FILES_DATABASE_URL is missing, exiting now')
    exit()

if len(SECOND_FILES_DATABASE_URL) == 0:
    logger.info('SECOND_FILES_DATABASE_URL is empty')

if len(BIN_CHANNEL) == 0:
    logger.error('BIN_CHANNEL is missing, exiting now')
    exit()
else:
    BIN_CHANNEL = int(BIN_CHANNEL)

if len(PREMIUM_NOTIFY_CHANNEL) == 0:
    logger.error('PREMIUM_NOTIFY_CHANNEL is missing, exiting now')
    exit()
else:
    PREMIUM_NOTIFY_CHANNEL = int(PREMIUM_NOTIFY_CHANNEL)

if len(VERIFICATION_NOTIFY_CHANNEL) == 0:
    logger.error('VERIFICATION_NOTIFY_CHANNEL is missing, exiting now')
    exit()
else:
    VERIFICATION_NOTIFY_CHANNEL = int(VERIFICATION_NOTIFY_CHANNEL)

if len(URL) == 0:
    logger.error('URL is missing, exiting now')
    exit()
else:
    if URL.startswith(('https://', 'http://')):
        if not URL.endswith("/"):
            URL += '/'
    elif is_valid_ip(URL):
        URL = f'http://{URL}/'
    else:
        logger.error('URL is not valid, exiting now')
        exit()

if len(TMDB_API_KEY) == 0:
    logger.error('TMDB_API_KEY is missing, exiting now')
    exit()