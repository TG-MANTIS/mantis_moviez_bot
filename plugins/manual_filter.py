from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import db
from config import ADMINS

@Client.on_message(filters.command("add") & filters.user(ADMINS) & filters.reply)
async def add_manual_filter(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>Provide a keyword!</b>\nExample: `/add keyword` (by replying)", quote=True)
        return

    keyword = message.text.split(None, 1)[1].strip().lower()
    reply_msg = message.reply_to_message
    chat_id = message.chat.id
    reply_text = reply_msg.text or reply_msg.caption or "Media/File"
    
    await db.save_manual_filter(chat_id, keyword, reply_text)
    await message.reply_text(f"<b>✅ Manual filter for <code>{keyword}</code> saved!</b>", quote=True)

@Client.on_message(filters.command("del") & filters.user(ADMINS))
async def delete_manual_filter(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>Provide keyword to delete!</b>", quote=True)
        return

    keyword = message.text.split(None, 1)[1].strip().lower()
    chat_id = message.chat.id

    deleted = await db.delete_manual_filter(chat_id, keyword)
    if deleted:
        await message.reply_text(f"<b>🗑️ Manual filter <code>{keyword}</code> deleted!</b>", quote=True)
    else:
        await message.reply_text(f"<b>❌ Filter <code>{keyword}</code> not found!</b>", quote=True)

@Client.on_message(filters.text & ~filters.command(["start", "index", "settings", "broadcast", "gcast", "groupbroadcast", "add", "del"]) & (filters.group | filters.private), group=0)
async def manual_filter_handler(client: Client, message: Message):
    query = message.text.strip().lower()
    chat_id = message.chat.id
    
    filter_data = await db.get_manual_filter(chat_id, query)
    if filter_data:
        await message.reply_text(text=filter_data.get("reply_text"), quote=True)
        return

    message.continue_propagation()
