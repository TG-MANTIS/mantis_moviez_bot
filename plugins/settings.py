from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from database.database import db
from config import ADMINS

@Client.on_message(filters.command("settings") & filters.user(ADMINS))
async def open_settings(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await db.get_settings(chat_id)
    
    welcome_status = "✅ ON" if settings.get("welcome", True) else "❌ OFF"
    goodbye_status = "✅ ON" if settings.get("goodbye", True) else "❌ OFF"
    fsub_status = "✅ ON" if settings.get("f_sub", True) else "❌ OFF"
    imdb_status = "✅ ON" if settings.get("imdb", True) else "❌ OFF"

    buttons = [
        [
            InlineKeyboardButton(f"👋 Welcome: {welcome_status}", callback_data="toggle_welcome"),
            InlineKeyboardButton(f"🚶‍♂️ Goodbye: {goodbye_status}", callback_data="toggle_goodbye")
        ],
        [
            InlineKeyboardButton("📢 Force Sub (F-Sub)", callback_data="info_fsub"),
            InlineKeyboardButton(f"🎬 IMDb Poster: {imdb_status}", callback_data="toggle_imdb")
        ],
        [
            InlineKeyboardButton(f"📢 F-Sub Status: {fsub_status}", callback_data="toggle_fsub"),
        ],
        [
            InlineKeyboardButton("🖼️ Set Custom Photo", callback_data="info_photo"),
            InlineKeyboardButton("📝 Set Custom Caption", callback_data="info_caption")
        ],
        [
            InlineKeyboardButton("❌ Close Menu", callback_data="close_media")
        ]
    ]

    await message.reply_text(
        text="<b>⚙️ Bot Control Settings Panel:\n\nUse the buttons below to toggle features or click them for setup instructions:</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True
    )

@Client.on_callback_query(filters.regex(r"^toggle_"))
async def toggle_settings(client: Client, query: CallbackQuery):
    chat_id = query.message.chat.id
    data = query.data
    settings = await db.get_settings(chat_id)

    if data == "toggle_welcome":
        new_val = not settings.get("welcome", True)
        await db.update_setting(chat_id, "welcome", new_val)
        await query.answer(f"Welcome Message turned {'ON' if new_val else 'OFF'}!")

    elif data == "toggle_goodbye":
        new_val = not settings.get("goodbye", True)
        await db.update_setting(chat_id, "goodbye", new_val)
        await query.answer(f"Goodbye Message turned {'ON' if new_val else 'OFF'}!")

    elif data == "toggle_fsub":
        new_val = not settings.get("f_sub", True)
        await db.update_setting(chat_id, "f_sub", new_val)
        await query.answer(f"Force Subscription turned {'ON' if new_val else 'OFF'}!")

    elif data == "toggle_imdb":
        new_val = not settings.get("imdb", True)
        await db.update_setting(chat_id, "imdb", new_val)
        await query.answer(f"IMDb Poster Support turned {'ON' if new_val else 'OFF'}!")

    settings = await db.get_settings(chat_id)
    w_status = "✅ ON" if settings.get("welcome", True) else "❌ OFF"
    g_status = "✅ ON" if settings.get("goodbye", True) else "❌ OFF"
    f_status = "✅ ON" if settings.get("f_sub", True) else "❌ OFF"
    i_status = "✅ ON" if settings.get("imdb", True) else "❌ OFF"

    buttons = [
        [
            InlineKeyboardButton(f"👋 Welcome: {w_status}", callback_data="toggle_welcome"),
            InlineKeyboardButton(f"🚶‍♂️ Goodbye: {g_status}", callback_data="toggle_goodbye")
        ],
        [
            InlineKeyboardButton("📢 Force Sub (F-Sub)", callback_data="info_fsub"),
            InlineKeyboardButton(f"🎬 IMDb Poster: {i_status}", callback_data="toggle_imdb")
        ],
        [
            InlineKeyboardButton(f"📢 F-Sub Status: {f_status}", callback_data="toggle_fsub"),
        ],
        [
            InlineKeyboardButton("🖼️ Set Custom Photo", callback_data="info_photo"),
            InlineKeyboardButton("📝 Set Custom Caption", callback_data="info_caption")
        ],
        [
            InlineKeyboardButton("❌ Close Menu", callback_data="close_media")
        ]
    ]

    await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^info_fsub$"))
async def fsub_info(client: Client, query: CallbackQuery):
    text = (
        "<b>📢 Force Subscription (F-Sub) Setup Instructions:</b>\n\n"
        "This feature forces users to join your update channel before receiving files.\n\n"
        "<b>How to set up?</b>\n"
        "Send the following command in bot private chat:\n"
        "<code>/setfsub channel_id</code>\n\n"
        "<b>Example:</b>\n"
        "<code>/setfsub -1001234567890</code>\n\n"
        "<i>(Note: Make sure your bot is an Admin in that channel).</i>"
    )
    await query.message.reply_text(text=text)
    await query.answer()

@Client.on_message(filters.command("setfsub") & filters.user(ADMINS))
async def save_fsub_channel(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>Please provide the channel ID!</b>\nExample: `/setfsub -1001234567890`", quote=True)
        return
    
    channel_id = message.text.split(None, 1)[1].strip()
    await db.update_setting(message.chat.id, "f_sub_channel", channel_id)
    await message.reply_text(f"<b>✅ Force Subscription channel ID successfully saved!</b>\n\nID: `{channel_id}`", quote=True)

@Client.on_callback_query(filters.regex(r"^info_photo$"))
async def photo_info(client: Client, query: CallbackQuery):
    text = (
        "<b>🖼️ Custom Photo / Thumbnail Setup Instructions:</b>\n\n"
        "When IMDb Poster is turned OFF, this custom photo/thumbnail will be sent along with files.\n\n"
        "<b>How to set up?</b>\n"
        "Send the following command in bot private chat:\n"
        "<code>/setphoto direct_image_url</code>\n\n"
        "<b>Example:</b>\n"
        "<code>/setphoto https://telegra.ph/file/sample.jpg</code>\n\n"
        "<i>(Tip: Upload your image to Telegra.ph or any image hosting site and paste the direct URL here).</i>"
    )
    await query.message.reply_text(text=text)
    await query.answer()

@Client.on_message(filters.command("setphoto") & filters.user(ADMINS))
async def save_custom_photo(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>Please provide the image URL!</b>\nExample: `/setphoto https://telegra.ph/file/sample.jpg`", quote=True)
        return
    
    photo_url = message.text.split(None, 1)[1].strip()
    await db.update_setting(message.chat.id, "custom_photo", photo_url)
    await message.reply_text(f"<b>✅ Custom photo successfully updated!</b>\n\n`{photo_url}`", quote=True)

@Client.on_callback_query(filters.regex(r"^info_caption$"))
async def caption_info(client: Client, query: CallbackQuery):
    text = (
        "<b>📝 Custom Caption Setup Guide:</b>\n\n"
        "Customize the caption sent with files according to your style.\n\n"
        "<b>How to set up?</b>\n"
        "<code>/setcaption Your custom caption text here</code>\n\n"
        "<b>Available Variables:</b>\n"
        "• <code>{file_name}</code> - Displays original file name\n"
        "• <code>{file_size}</code> - Displays file size\n\n"
        "<b>Formatting & Links Styling (HTML):</b>\n"
        "• <b>Bold:</b> `<b>Your Text</b>`\n"
        "• <i>Italic:</i> `<i>Your Text</i>`\n"
        "• <u>Underline:</u> `<u>Your Text</u>`\n"
        "• <b>Channel Link:</b> `[Channel Name](https://t.me/YourChannel)`\n"
        "• <b>Emojis:</b> You can use 📁, 🎬, 🔥, ⚡ etc.\n\n"
        "<b>Sample Template:</b>\n"
        "<code>/setcaption 📁 File: {file_name}\n📦 Size: {file_size}\n\n✨ Join Us: @YourChannel</code>"
    )
    await query.message.reply_text(text=text)
    await query.answer()

@Client.on_message(filters.command("setcaption") & filters.user(ADMINS))
async def save_custom_caption(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>Please provide the caption text!</b>", quote=True)
        return
    
    caption_text = message.text.split(None, 1)[1]
    await db.update_setting(message.chat.id, "caption", caption_text)
    await message.reply_text(f"<b>✅ Custom caption successfully updated!</b>\n\n<b>New Caption:</b>\n{caption_text}", quote=True)
