import os

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

DATABASE_URL = os.environ.get("DATABASE_URL", "")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "AutoFilterBot")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "TelegramFiles")

ADMINS = [int(admin) for admin in os.environ.get("ADMINS", "").split(",") if admin.strip().isdigit()]

# ✨ ഇവിടെ ഒന്നിലധികം ഡിബി ചാനൽ ഐഡികൾ കോമ (,) ഇട്ട് നൽകാം (ഉദാഹരണത്തിന്: -100111,-100222)
DB_CHANNEL = [int(ch.strip()) for ch in os.environ.get("DB_CHANNEL", "").split(",") if ch.strip().replace("-", "").isdigit()]

LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", 0))
F_SUB_CHANNEL = os.environ.get("F_SUB_CHANNEL", None)
