import os

API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Owner and Admin IDs
OWNER_ID = int(os.environ.get("OWNER_ID", ""))
ADMINS = [OWNER_ID]

# Log Channel and Support Group
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))
SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "")

# DB Channel (ഫയലുകൾ ഇൻഡക്സ് ചെയ്യാൻ ഉപയോഗിക്കുന്ന ചാനൽ ഐഡി)
DB_CHANNEL = [int(ch) for ch in os.environ.get("DB_CHANNEL", "").split()]

# Bot Settings
START_PIC = os.environ.get("START_PIC", None)
START_TEXT = os.environ.get("START_TEXT", "Hi {first}, Good Morning!")
FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL", None)

# MongoDB Database URL
DATABASE_URL = os.environ.get("DATABASE_URL", "")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "KDBots")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "telegram_files")
