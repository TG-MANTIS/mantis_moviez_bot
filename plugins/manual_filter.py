from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import db
from config import ADMINS

# 1. Add Manual Filter: Reply to a message with `/add keyword`
@Client.on_message(filters.command("add") & filters.user(ADMINS) & filters.reply)
async def add_manual_filter(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>Please provide a keyword!</b>\nExample: `/add movie_name` (by replying to a message)", quote=True)
        return

    keyword = message.text.split(None, 1)[1].strip().lower()
    reply_msg = message.reply_to_message
    chat_id = message.chat.id

    # മെസ്സേജോ ടെക്സ്റ്റോ ഡാറ്റാബേസിൽ സേവ് ചെയ്യാൻ കോപ്പി ചെയ്യാം അല്ലെങ്കിൽ ടെക്സ്റ്റ് എടുക്കാം
    reply_text = reply_msg.text or reply_msg.caption or "Media/File"
    
    await db.save_manual_filter(chat_id, keyword, reply_text)
    await message.reply_text(f"<b>✅ Manual filter for <code>{keyword}</code> successfully saved!</b>", quote=True)


# 2. Delete Manual Filter: `/del keyword`
@Client.on_message(filters.command("del") & filters.user(ADMINS))
async def delete_manual_filter(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>Please provide the keyword to delete!</b>\nExample: `/del movie_name`", quote=True)
        return

    keyword = message.text.split(None, 1)[1].strip().lower()
    chat_id = message.chat.id

    deleted = await db.delete_manual_filter(chat_id, keyword)
    if deleted:
        await message.reply_text(f"<b>🗑️ Manual filter for <code>{keyword}</code> successfully deleted!</b>", quote=True)
    else:
        await message.reply_text(f"<b>❌ Filter <code>{keyword}</code> not found in database!</b>", quote=True)


# 3. Handle Manual Filter when user/group sends a message
@Client.on_message(filters.text & ~filters.command(["start", "index", "settings", "broadcast", "gcast", "groupbroadcast", "add", "del"]) & (filters.group | filters.private), group=0)
async def manual_filter_handler(client: Client, message: Message):
    query = message.text.strip().lower()
    chat_id = message.chat.id
    
    # ഡാറ്റാബേസിൽ മാനുവൽ ഫിൽറ്റർ ഉണ്ടോ എന്ന് നോക്കുന്നു
    filter_data = await db.get_manual_filter(chat_id, query)
    if filter_data:
        reply_text = filter_data.get("reply_text")
        await message.reply_text(text=reply_text, quote=True)
        return

    # മാനുവൽ ഫിൽറ്റർ ഇല്ലെങ്കിൽ അടുത്ത ഫിൽറ്ററിലേക്ക് (Auto-Filter) പോകും
    message.continue_propagation()
