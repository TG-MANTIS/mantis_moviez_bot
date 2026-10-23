import os

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

DATABASE_URL = os.environ.get("DATABASE_URL", "")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "AutoFilterBot")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "TelegramFiles")

ADMINS = [int(admin) for admin in os.environ.get("ADMINS", "").split(",") if admin.isdigit()]
DB_CHANNEL = [int(ch) for ch in os.environ.get("DB_CHANNEL", "").split(",") if ch.isdigit()]

LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", 0))
DEFAULT_F_SUB = os.environ.get("F_SUB_CHANNEL", None)
