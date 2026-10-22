import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMINS, DB_CHANNEL
from database.database import db

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("index") & filters.user(ADMINS))
async def index_files(client: Client, message: Message):
    if not DB_CHANNEL:
        await message.reply_text("ശ്രദ്ധിക്കുക: കോൺഫിഗറേഷനിൽ 'DB_CHANNEL' സെറ്റ് ചെയ്തിട്ടില്ല!")
        return

    m = await message.reply_text("ഇൻഡക്സിംഗ് പ്രക്രിയ ആരംഭിക്കുന്നുവെന്ന് ഉറപ്പാക്കാൻ ശ്രമിക്കുന്നു...")
    
    # ഇവിടെ ചാനലിൽ നിന്നുള്ള മെസ്സേജുകൾ റീഡ് ചെയ്ത് ഡാറ്റാബേസിലേക്ക് സേവ് ചെയ്യുന്ന ലൂപ്പ് നൽകാം.
    # ഉദാഹരണത്തിന് ഒരൊറ്റ ചാനൽ ഐഡി ആണെങ്കിൽ:
    chat_id = DB_CHANNEL[0] if isinstance(DB_CHANNEL, list) else DB_CHANNEL
    
    try:
        count = 0
        async for msg in client.iter_messages(chat_id):
            if msg.media:
                media = getattr(msg, msg.media.value)
                if media:
                    file_id = media.file_id
                    file_name = getattr(media, "file_name", "No Name")
                    file_size = getattr(media, "file_size", 0)
                    
                    # ഡാറ്റാബേസിലേക്ക് സേവ് ചെയ്യുന്നു
                    await db.save_file(file_id, file_name, file_size)
                    count += 1
        
        await m.edit_text(f"Successful! ആകെ {count} ഫയലുകൾ ഇൻഡക്സ് ചെയ്തിട്ടുണ്ട്.")
    except Exception as e:
        await m.edit_text(f"ഇൻഡക്സിംഗിൽ ഒരു തടസ്സം നേരിട്ടു: `{e}`")
