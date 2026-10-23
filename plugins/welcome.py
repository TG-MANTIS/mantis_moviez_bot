from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import db

@Client.on_message(filters.new_chat_members)
async def welcome_user(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await db.get_settings(chat_id)
    
    if not settings.get("welcome", True):
        return

    for user in message.new_chat_members:
        if user.id == client.me.id:
            await message.reply_text("<b>👋 Auto-Filter enabled successfully!</b>")
            continue
        
        await message.reply_text(f"<b>Welcome {user.mention} to our group! 🎉</b>")

@Client.on_message(filters.left_chat_member)
async def goodbye_user(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await db.get_settings(chat_id)
    
    if not settings.get("goodbye", True):
        return

    user = message.left_chat_member
    if user.id == client.me.id:
        return

    await message.reply_text(f"<b>Goodbye {user.mention}! 👋</b>")
