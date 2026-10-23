from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from database.database import db
from config import ADMINS, DB_CHANNEL
import asyncio

@Client.on_message(filters.command("index") & filters.user(ADMINS))
async def index_files(client: Client, message: Message):
    if not DB_CHANNEL:
        return await message.reply_text("<b>❌ DB_CHANNEL ID configured ചെയ്തിട്ടില്ല!</b>")
    
    # ഒന്നിലധികം ചാനലുകൾ ഉണ്ടോ എന്ന് പരിശോധിക്കുന്നു
    if len(DB_CHANNEL) == 1:
        chat_id = DB_CHANNEL[0]
        try:
            chat = await client.get_chat(chat_id)
        except Exception as e:
            return await message.reply_text(f"<b>❌ Error:</b> <code>{e}</code>")
        
        msg = await message.reply_text("<b>⏳ Indexing started... Please wait.</b>")
        total_files = 0
        async for msg_obj in client.get_chat_history(chat_id):
            if msg_obj.media:
                media = getattr(msg_obj, msg_obj.media.value)
                if media:
                    file_id = media.file_id
                    file_name = getattr(media, "file_name", "Untitled")
                    file_size = getattr(media, "file_size", 0)
                    
                    is_saved = await db.save_file(file_id, file_name, file_size)
                    if is_saved:
                        total_files += 1
                        
        await msg.edit_text(f"<b>✅ Indexing Completed!\n📁 Total New Files Indexed: <code>{total_files}</code></b>")
    
    else:
        # ഒന്നിലധികം ചാനലുകൾ ഉള്ളപ്പോൾ എല്ലാറ്റിൽ നിന്നും ഇൻഡക്സ് ചെയ്യും
        msg = await message.reply_text("<b>⏳ Indexing started from all DB Channels... Please wait.</b>")
        total_files = 0
        
        for chat_id in DB_CHANNEL:
            try:
                async for msg_obj in client.get_chat_history(chat_id):
                    if msg_obj.media:
                        media = getattr(msg_obj, msg_obj.media.value)
                        if media:
                            file_id = media.file_id
                            file_name = getattr(media, "file_name", "Untitled")
                            file_size = getattr(media, "file_size", 0)
                            
                            is_saved = await db.save_file(file_id, file_name, file_size)
                            if is_saved:
                                total_files += 1
            except Exception as e:
                print(f"Error indexing channel {chat_id}: {e}")
                continue
                
        await msg.edit_text(f"<b>✅ Multiple Channels Indexing Completed!\n📁 Total New Files Indexed: <code>{total_files}</code></b>")
