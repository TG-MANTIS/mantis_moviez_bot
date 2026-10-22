import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import START_TEXT, START_PIC

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    start_time = time.time()
    first_name = message.from_user.first_name
    
    text = START_TEXT.format(first=first_name)
    
    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Support", url="https://t.me/your_support_chat")]
        ]
    )
    
    if START_PIC:
        await message.reply_photo(
            photo=START_PIC,
            caption=text,
            reply_markup=reply_markup
        )
    else:
        await message.reply_text(
            text=text,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
