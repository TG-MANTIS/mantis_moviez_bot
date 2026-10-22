import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMINS, DB_CHANNEL
from database import save_file  # ഡാറ്റാബേസ് ഫങ്ഷൻ

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("index") & filters.user(ADMINS))
async def index_files(client: Client, message: Message):
    if not DB_CHANNEL:
        await message.reply_text("പ്രധാനപ്പെട്ട വിവരങ്ങൾ: കോൺഫിഗറേഷനിൽ 'DB_CHANNEL' സെറ്റ് ചെയ്തിട്ടില്ല!")
        return
    
    # ഇൻഡക്സിംഗ് പ്രക്രിയ ഇവിടെ ആരംഭിക്കാം
    await message.reply_text("ഫയൽ ഇൻഡക്സിംഗ് പ്രക്രിയ ആരംഭിച്ചിരിക്കുന്നു...")
