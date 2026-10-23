from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from database.database import db

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await db.get_settings(chat_id)
    
    start_photo = settings.get("start_photo")
    start_text_template = settings.get("start_text", "<b>👋 Hello {mention}, Welcome to Auto-Filter Bot!</b>")
    
    user_mention = message.from_user.mention
    first_name = message.from_user.first_name
    
    formatted_text = start_text_template.format(mention=user_mention, first_name=first_name)

    buttons = [
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="bot_help"),
            InlineKeyboardButton("🤖 About", callback_data="bot_about")
        ],
        [
            InlineKeyboardButton("⚙️ Settings Panel", callback_data="open_settings_panel")
        ]
    ]

    if start_photo:
        try:
            await message.reply_photo(
                photo=start_photo,
                caption=formatted_text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
        except Exception:
            pass

    await message.reply_text(
        text=formatted_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True
    )
