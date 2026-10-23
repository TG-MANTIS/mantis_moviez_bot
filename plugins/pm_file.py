from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from pyrogram.errors import UserNotParticipant
from database.database import db
from config import DB_CHANNEL

@Client.on_callback_query(filters.regex(r"^file#"))
async def send_file_to_pm(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    chat_id_settings = query.message.chat.id
    settings = await db.get_settings(chat_id_settings)
    
    # 1. Force Subscription check
    if settings.get("f_sub", True):
        f_sub_channel = settings.get("f_sub_channel")
        if f_sub_channel:
            try:
                await client.get_chat_member(f_sub_channel, user_id)
            except UserNotParticipant:
                try:
                    chat = await client.get_chat(f_sub_channel)
                    invite_link = chat.invite_link or f"https://t.me/{chat.username}" if chat.username else None
                    if invite_link:
                        buttons = [
                            [InlineKeyboardButton(f"🔔 Join {chat.title}", url=invite_link)],
                            [InlineKeyboardButton("🔄 Try Again", callback_data=query.data)]
                        ]
                        await query.answer("⚠️ You must join our update channel to get files!", show_alert=True)
                        await query.message.reply_text(
                            text="<b>⚠️ For security reasons, please join our update channels first. Click 'Try Again' after joining:</b>",
                            reply_markup=InlineKeyboardMarkup(buttons),
                            quote=True
                        )
                        return
                except:
                    pass

    await query.answer("🎉 Success! You have joined the channel. Sending file...", show_alert=False)

    # 2. Send file to PM
    file_id = query.data.split("#")[1]
    
    try:
        db_chat_id = DB_CHANNEL[0] if isinstance(DB_CHANNEL, list) else DB_CHANNEL
        
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🗑️ Close / Delete", callback_data="close_media")]]
        )
        
        caption_template = settings.get("caption", "<b>📁 File: {file_name}\n📦 Size: {file_size}\n\n🤖 Powered by Auto-Filter Bot</b>")
        
        # Fetch file info to replace variables if needed
        # (Assuming basic replacement)
        caption = caption_template.format(file_name="Movie File", file_size="")

        await client.send_cached_media(
            chat_id=user_id,
            file_id=file_id,
            caption=caption,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        await query.answer(f"Sorry, an error occurred while sending the file!", show_alert=True)

@Client.on_callback_query(filters.regex(r"^close_media$"))
async def close_media(client: Client, query: CallbackQuery):
    try:
        await query.message.delete()
    except:
        await query.answer("Failed to delete message!", show_alert=True)
