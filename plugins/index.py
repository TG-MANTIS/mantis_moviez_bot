from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.database import db
from config import ADMINS, DB_CHANNEL
import asyncio

# 1. ഫോർവേഡ് ചെയ്യുമ്പോൾ ചാനൽ ഓട്ടോമാറ്റിക്കായി ഇൻഡക്സ് ചെയ്യാൻ ചോദിക്കുന്ന ഫീച്ചർ (പഴയതുപോലെ)
@Client.on_message(filters.forwarded & filters.user(ADMINS))
async def forwarded_index_handler(client: Client, message: Message):
    if message.forward_from_chat:
        chat_id = message.forward_from_chat.id
        chat_title = message.forward_from_chat.title or "Unknown Channel"
        
        button = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes, Index This Channel", callback_data=f"index_yes_{chat_id}"),
                InlineKeyboardButton("❌ No", callback_data="index_no")
            ]
        ])
        
        await message.reply_text(
            f"<b>📁 Detected Forwarded Channel!</b>\n\n"
            f"<b>Title:</b> <code>{chat_title}</code>\n"
            f"<b>ID:</b> <code>{chat_id}</code>\n\n"
            f"Do you want to add this channel to your Database/Index list?",
            reply_markup=button
        )

@Client.on_callback_query(filters.regex(r"^index_"))
async def index_callback_handler(client, query):
    data = query.data
    if data == "index_no":
        return await query.message.edit_text("<b>❌ Indexing cancelled.</b>")
    
    if data.startswith("index_yes_"):
        chat_id = int(data.split("_")[2])
        await query.message.edit_text(f"<b>⏳ Indexing started for channel <code>{chat_id}</code>... Please wait.</b>")
        
        total_files = 0
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
            
            await query.message.edit_text(
                f"<b>✅ Channel Indexing Completed Successfully!\n\n"
                f"📁 Total New Files Indexed: <code>{total_files}</code>\n"
                f"📌 Channel ID: <code>{chat_id}</code></b>"
            )
        except Exception as e:
            await query.message.edit_text(f"<b>❌ Error during indexing:</b>\n<code>{e}</code>")


# 2. കമാൻഡ് വഴി /index കൊടുക്കുമ്പോൾ config-ൽ ഉള്ള ഒന്നിലധികം DB ചാനലുകളിൽ നിന്നും ഇൻഡക്സ് ചെയ്യുന്ന ഫീച്ചർ
@Client.on_message(filters.command("index") & filters.user(ADMINS))
async def index_files_command(client: Client, message: Message):
    if not DB_CHANNEL:
        return await message.reply_text("<b>❌ DB_CHANNEL IDs configured ചെയ്തിട്ടില്ല!</b>")
    
    msg = await message.reply_text("<b>⏳ Indexing started from all configured DB Channels... Please wait.</b>")
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
