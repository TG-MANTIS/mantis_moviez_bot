from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import OWNER_NAME

# 1. /start കമാൻഡ് ഹാൻഡ് ചെയ്യുമ്പോൾ മെയിൻ മെനു കാണിക്കാൻ
@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    bot_name = client.me.mention if client.me else "Auto Filter Bot"
    
    welcome_text = (
        f"<b>👋 Hello {message.from_user.mention}!\n\n"
        f"I am {bot_name}, an advanced and powerful Auto-Filter Bot. "
        f"I can help you find and filter files in your groups easily!</b>\n\n"
        f"<i>✨ Click the buttons below to check out my features, settings, or help guide.</i>"
    )
    
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
    
    await message.reply_text(
        text=welcome_text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

# 2. Start മെനുവിലേക്ക് തിരികെ വരാൻ (Back button)
@Client.on_callback_query(filters.regex("start"))
async def start_callback(client: Client, query: CallbackQuery):
    bot_name = client.me.mention if client.me else "Auto Filter Bot"
    
    welcome_text = (
        f"<b>👋 Hello {query.from_user.mention}!\n\n"
        f"I am {bot_name}, an advanced and powerful Auto-Filter Bot. "
        f"I can help you find and filter files in your groups easily!</b>\n\n"
        f"<i>✨ Click the buttons below to check out my features, settings, or help guide.</i>"
    )
    
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
    
    await query.message.edit_text(
        text=welcome_text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

# 3. Settings ബട്ടൺ ക്ലിക്ക് ചെയ്യുമ്പോൾ
@Client.on_callback_query(filters.regex("settings"))
async def settings_callback(client: Client, query: CallbackQuery):
    settings_text = (
        "<b>⚙️ Bot Settings Panel:</b>\n\n"
        "Here you can manage your bot's configurations, file caption styles, "
        "IMDb poster settings, and other preferences directly from your group or database."
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Back", callback_data="start")]
    ])
    
    await query.message.edit_text(
        text=settings_text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

# 4. Help ബട്ടൺ ക്ലിക്ക് ചെയ്യുമ്പോൾ (കമാൻഡുകളും വിവരങ്ങളും)
@Client.on_callback_query(filters.regex("help"))
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
    
    await query.message.edit_text(
        text=help_text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

# 5. About ബട്ടൺ ക്ലിക്ക് ചെയ്യുമ്പോൾ (ബോട്ട് വിവരങ്ങളും ഓണർ പേരും)
@Client.on_callback_query(filters.regex("about"))
async def about_callback(client: Client, query: CallbackQuery):
    bot_name = client.me.mention if client.me else "Auto Filter Bot"
    owner_name = OWNER_NAME if 'OWNER_NAME' in globals() or 'OWNER_NAME' in locals() else "Ajeesh Aji"
    
    about_text = (
        "<b>🤖 My Details:</b>\n\n"
        f"<b>• Bot Name:</b> {bot_name}\n"
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
    
    await query.message.edit_text(
        text=about_text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

# 6. മെസ്സേജ് ക്ലോസ് ചെയ്യാൻ (Close button)
@Client.on_callback_query(filters.regex("close"))
async def close_callback(client: Client, query: CallbackQuery):
    await query.message.delete()
