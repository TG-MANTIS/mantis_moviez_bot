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
    autodel_time = settings.get("auto_delete", 300)
    autodel_status = f"✅ ({autodel_time}s)" if autodel_time > 0 else "❌ OFF"
    max_btn = settings.get("max_btn", 8)

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
            InlineKeyboardButton(f"🗑️ Auto Delete: {autodel_status}", callback_data="info_autodel"),
            InlineKeyboardButton(f"🔢 Results Count: [{max_btn}]", callback_data="info_maxbtn")
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
        text="<b>⚙️ Bot Control Settings Panel:\n\nManage your bot features below:</b>",
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

    elif data == "toggle_imdb":
        new_val = not settings.get("imdb", True)
        await db.update_setting(chat_id, "imdb", new_val)
        await query.answer(f"IMDb Poster turned {'ON' if new_val else 'OFF'}!")

    # പാനൽ റിഫ്രഷ് ചെയ്യാൻ settings കമാൻഡ് ഫംഗ്ഷൻ പോലെ റീലോഡ് ചെയ്യാം
    await query.answer("Updated!")

# Auto Delete Info & Command
@Client.on_callback_query(filters.regex(r"^info_autodel$"))
async def autodel_info(client: Client, query: CallbackQuery):
    text = (
        "<b>🗑️ Auto Delete Setup Instructions:</b>\n\n"
        "Automatically delete movie result messages in groups after a certain time to keep the group clean.\n\n"
        "<b>How to set up? (Time in seconds, 0 to disable):</b>\n"
        "<code>/setautodel 300</code> (300 seconds = 5 minutes)\n"
        "<code>/setautodel 0</code> (To turn OFF)"
    )
    await query.message.reply_text(text=text)
    await query.answer()

@Client.on_message(filters.command("setautodel") & filters.user(ADMINS))
async def save_autodel(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>Please provide time in seconds!</b>\nExample: `/setautodel 300`", quote=True)
        return
    seconds = int(message.text.split(None, 1)[1])
    await db.update_setting(message.chat.id, "auto_delete", seconds)
    await message.reply_text(f"<b>✅ Auto Delete time successfully set to {seconds} seconds!</b>", quote=True)

# Max Results Buttons Info & Command
@Client.on_callback_query(filters.regex(r"^info_maxbtn$"))
async def maxbtn_info(client: Client, query: CallbackQuery):
    text = (
        "<b>🔢 Results Count Setup Instructions:</b>\n\n"
        "Set how many file buttons should appear per page in group results.\n\n"
        "<b>How to set up?</b>\n"
        "<code>/setmaxbtn 8</code> (Shows 8 buttons per page)"
    )
    await query.message.reply_text(text=text)
    await query.answer()

@Client.on_message(filters.command("setmaxbtn") & filters.user(ADMINS))
async def save_maxbtn(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>Please provide the number of buttons!</b>\nExample: `/setmaxbtn 8`", quote=True)
        return
    count = int(message.text.split(None, 1)[1])
    await db.update_setting(message.chat.id, "max_btn", count)
    await message.reply_text(f"<b>✅ Max filter buttons per page set to {count}!</b>", quote=True)

# (മുമ്പത്തെ info_fsub, info_photo, info_caption കമാൻഡുകൾ ഇതിൽ നിലനിർത്തുക)
