from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from config import OWNER_NAME
from database.database import db

# നമ്മൾ കോഡിൽ തന്നെ ഫിക്സ് ചെയ്ത് വെക്കുന്ന ഫോട്ടോകൾ (ഇവിടെ നിങ്ങളുടെ ഫോട്ടോ ലിങ്കുകൾ നൽകാം)
SETTINGS_PHOTO = "https://telegra.ph/file/sample.jpg"
HELP_PHOTO = "https://telegra.ph/file/sample.jpg"
ABOUT_PHOTO = "https://telegra.ph/file/sample.jpg"

# 1. /start കമാൻഡ് ഹാൻഡ് ചെയ്യുമ്പോൾ (ഡാറ്റാബേസിൽ നിന്നുള്ള ഫോട്ടോയും ടെക്സ്റ്റും)
@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await db.get_settings(chat_id)
    
    bot_name = client.me.mention if client.me else "Auto Filter Bot"
    user_mention = message.from_user.mention
    
    # കസ്റ്റമൈസ് ചെയ്യാവുന്ന സ്റ്റാർട്ട് മെസ്സേജും ഫോട്ടോയും ഡാറ്റാബേസിൽ നിന്ന് എടുക്കുന്നു
    custom_text = settings.get("start_text", "<b>👋 Hello {mention},\n\nWelcome to Auto-Filter Bot! Send me any movie or series name to search files.</b>")
    welcome_text = custom_text.format(mention=user_mention, bot_name=bot_name)
    start_photo = settings.get("start_photo", "https://telegra.ph/file/sample.jpg")
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("🤖 About", callback_data="about"),
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ])
    
    try:
        await message.reply_photo(
            photo=start_photo,
            caption=welcome_text,
            reply_markup=keyboard
        )
    except Exception:
        await message.reply_text(
            text=welcome_text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )

# 2. Start മെനുവിലേക്ക് തിരികെ വരാൻ (Back button)
@Client.on_callback_query(filters.regex("^start$"))
async def start_callback(client: Client, query: CallbackQuery):
    chat_id = query.message.chat.id
    settings = await db.get_settings(chat_id)
    
    bot_name = client.me.mention if client.me else "Auto Filter Bot"
    user_mention = query.from_user.mention
    
    custom_text = settings.get("start_text", "<b>👋 Hello {mention},\n\nWelcome to Auto-Filter Bot! Send me any movie or series name to search files.</b>")
    welcome_text = custom_text.format(mention=user_mention, bot_name=bot_name)
    start_photo = settings.get("start_photo", "https://telegra.ph/file/sample.jpg")
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("🤖 About", callback_data="about"),
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ])
    
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=start_photo, caption=welcome_text),
            reply_markup=keyboard
        )
    except Exception:
        try:
            await query.message.edit_text(
                text=welcome_text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        except Exception:
            pass

# 3. Settings ബട്ടൺ ക്ലിക്ക് ചെയ്യുമ്പോൾ (കോഡിൽ ഫിക്സ് ചെയ്ത ഫോട്ടോ)
@Client.on_callback_query(filters.regex("^settings$"))
async def settings_callback(client: Client, query: CallbackQuery):
    settings_text = (
        "<b>⚙️ Bot Settings Panel:</b>\n\n"
        "Here you can manage your bot's configurations, file caption styles, "
        "IMDb poster settings, and other preferences directly from your group or database."
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Back", callback_data="start")]
    ])
    
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=SETTINGS_PHOTO, caption=settings_text),
            reply_markup=keyboard
        )
    except Exception:
        try:
            await query.message.edit_text(
                text=settings_text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        except Exception:
            pass

# 4. Help ബട്ടൺ ക്ലിക്ക് ചെയ്യുമ്പോൾ (കോഡിൽ ഫിക്സ് ചെയ്ത ഫോട്ടോ)
@Client.on_callback_query(filters.regex("^help$"))
async def help_callback(client: Client, query: CallbackQuery):
    help_text = (
        "<b>❓ Help & Commands Guide:</b>\n\n"
        "Welcome to the Help menu! Here are the available commands and their uses:\n\n"
        "<b>1️⃣ /start</b>\n"
        "• <b>Description:</b> Starts the bot and opens the main interactive menu.\n\n"
        "<b>2️⃣ /index</b>\n"
        "• <b>Description:</b> Indexes all files from your configured DB channels automatically.\n\n"
        "<b>3️⃣ /broadcast</b>\n"
        "• <b>Description:</b> Sends a broadcast text/media message to all private chat users.\n\n"
        "<b>4️⃣ /group_broadcast</b>\n"
        "• <b>Description:</b> Sends a broadcast message to all connected groups where the bot is added.\n\n"
        "<i>💡 Note: You can also forward any file from your database channel to trigger quick indexing!</i>"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("◀️ Back", callback_data="start"),
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ])
    
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=HELP_PHOTO, caption=help_text),
            reply_markup=keyboard
        )
    except Exception:
        try:
            await query.message.edit_text(
                text=help_text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        except Exception:
            pass

# 5. About ബട്ടൺ ക്ലിക്ക് ചെയ്യുമ്പോൾ (ഡൈനാമിക് ബോട്ട് നെയിമും ഹൈപ്പർലിങ്കും ചേർത്തത്)
@Client.on_callback_query(filters.regex("^about$"))
async def about_callback(client: Client, query: CallbackQuery):
    bot_name = client.me.first_name if client.me else "Auto Filter Bot"
    bot_username = client.me.username if client.me else "bot"
    owner_name = OWNER_NAME if 'OWNER_NAME' in globals() or 'OWNER_NAME' in locals() else "Ajeesh Aji"
    
    # ഹൈപ്പർലിങ്ക് ടാഗ് ഉപയോഗിച്ച് ബോട്ടിന്റെ പേര് പ്രൊഫൈൽ ലിങ്കിലേക്ക് കണക്റ്റ് ചെയ്തിരിക്കുന്നു
    bot_display = f"<a href='https://t.me/{bot_username}'>{bot_name}</a>" if client.me else bot_name
    
    about_text = (
        "<b>🤖 My Details:</b>\n\n"
        f"<b>• Bot Name:</b> {bot_display}\n"
        "<b>• Developer:</b> <code>Ajeesh Aji</code>\n"
        f"<b>• Bot Owner:</b> <code>{owner_name}</code>\n"
        "<b>• Language:</b> <code>Python 3</code>\n"
        "<b>• Library:</b> <code>Pyrogram</code>\n"
        "<b>• Database:</b> <code>MongoDB</code>\n\n"
        "<i>✨ This is a high-performance auto-filter bot with multi-channel support and smart indexing!</i>"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Back", callback_data="start")]
    ])
    
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=ABOUT_PHOTO, caption=about_text),
            reply_markup=keyboard
        )
    except Exception:
        try:
            await query.message.edit_text(
                text=about_text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        except Exception:
            pass

# 6. മെസ്സേജ് ക്ലോസ് ചെയ്യാൻ
@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client: Client, query: CallbackQuery):
    try:
        await query.message.delete()
    except Exception:
        pass
