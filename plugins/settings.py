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
    antispam_status = "✅ ON" if settings.get("anti_spam", True) else "❌ OFF" # 👈 ആന്റി-സ്പാം സ്റ്റാറ്റസ്
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
            # 👈 ആന്റി-സ്പാം ടോഗ്ഗൽ ബട്ടൺ ഇവിടെ ചേർത്തിരിക്കുന്നു
            InlineKeyboardButton(f"🛡️ Anti-Spam: {antispam_status}", callback_data="toggle_antispam")
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
            InlineKeyboardButton("🌅 Set Start Photo", callback_data="info_startphoto"),
            InlineKeyboardButton("📝 Set Start Text", callback_data="info_starttext")
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

    elif data == "toggle_fsub":
        new_val = not settings.get("f_sub", True)
        await db.update_setting(chat_id, "f_sub", new_val)
        await query.answer(f"Force Subscription turned {'ON' if new_val else 'OFF'}!")

    elif data == "toggle_imdb":
        new_val = not settings.get("imdb", True)
        await db.update_setting(chat_id, "imdb", new_val)
        await query.answer(f"IMDb Poster turned {'ON' if new_val else 'OFF'}!")

    elif data == "toggle_antispam": # 👈 ആന്റി-സ്പാം ഓൺ/ഓഫ് ചെയ്യാനുള്ള കോഡ്
        new_val = not settings.get("anti_spam", True)
        await db.update_setting(chat_id, "anti_spam", new_val)
        await query.answer(f"Anti-Spam turned {'ON' if new_val else 'OFF'}!")

    settings = await db.get_settings(chat_id)
    w_status = "✅ ON" if settings.get("welcome", True) else "❌ OFF"
    g_status = "✅ ON" if settings.get("goodbye", True) else "❌ OFF"
    f_status = "✅ ON" if settings.get("f_sub", True) else "❌ OFF"
    i_status = "✅ ON" if settings.get("imdb", True) else "❌ OFF"
    as_status = "✅ ON" if settings.get("anti_spam", True) else "❌ OFF" # 👈 ആന്റി-സ്പാം സ്റ്റാറ്റസ് റിഫ്രഷ് ചെയ്യാൻ
    autodel_time = settings.get("auto_delete", 300)
    autodel_status = f"✅ ({autodel_time}s)" if autodel_time > 0 else "❌ OFF"
    max_btn = settings.get("max_btn", 8)

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
            # 👈 ബട്ടൺ ലിസ്റ്റിലും ആന്റി-സ്പാം അപ്ഡേറ്റ് ചെയ്തു
            InlineKeyboardButton(f"🛡️ Anti-Spam: {as_status}", callback_data="toggle_antispam")
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
            InlineKeyboardButton("🌅 Set Start Photo", callback_data="info_startphoto"),
            InlineKeyboardButton("📝 Set Start Text", callback_data="info_starttext")
        ],
        [
            InlineKeyboardButton("❌ Close Menu", callback_data="close_media")
        ]
    ]

    await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^info_fsub$"))
async def fsub_info(client: Client, query: CallbackQuery):
    text = "<b>📢 Force Subscription (F-Sub) Setup:\n\n<code>/setfsub channel_id</code></b>"
    await query.message.reply_text(text=text)
    await query.answer()

@Client.on_message(filters.command("setfsub") & filters.user(ADMINS))
async def save_fsub_channel(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>Provide channel ID!</b>", quote=True)
        return
    channel_id = message.text.split(None, 1)[1].strip()
    await db.update_setting(message.chat.id, "f_sub_channel", channel_id)
    await message.reply_text(f"<b>✅ F-Sub channel ID saved:</b> `{channel_id}`", quote=True)

@Client.on_callback_query(filters.regex(r"^info_photo$"))
async def photo_info(client: Client, query: CallbackQuery):
    text = "<b>🖼️ Custom Photo Setup:\n\n<code>/setphoto image_url</code></b>"
    await query.message.reply_text(text=text)
    await query.answer()

@Client.on_message(filters.command("setphoto") & filters.user(ADMINS))
async def save_custom_photo(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>Provide image URL!</b>", quote=True)
        return
    photo_url = message.text.split(None, 1)[1].strip()
    await db.update_setting(message.chat.id, "custom_photo", photo_url)
    await message.reply_text(f"<b>✅ Custom photo updated!</b>", quote=True)

@Client.on_callback_query(filters.regex(r"^info_caption$"))
async def caption_info(client: Client, query: CallbackQuery):
    text = "<b>📝 Custom Caption Setup:\n\n<code>/setcaption Your caption text</code></b>"
    await query.message.reply_text(text=text)
    await query.answer()

@Client.on_message(filters.command("setcaption") & filters.user(ADMINS))
async def save_custom_caption(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>Provide caption text!</b>", quote=True)
        return
    caption_text = message.text.split(None, 1)[1]
    await db.update_setting(message.chat.id, "caption", caption_text)
    await message.reply_text(f"<b>✅ Custom caption updated!</b>", quote=True)

@Client.on_callback_query(filters.regex(r"^info_autodel$"))
async def autodel_info(client: Client, query: CallbackQuery):
    text = "<b>🗑️ Auto Delete Setup:\n\n<code>/setautodel 300</code></b>"
    await query.message.reply_text(text=text)
    await query.answer()

@Client.on_message(filters.command("setautodel") & filters.user(ADMINS))
async def save_autodel(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>Provide seconds!</b>", quote=True)
        return
    seconds = int(message.text.split(None, 1)[1])
    await db.update_setting(message.chat.id, "auto_delete", seconds)
    await message.reply_text(f"<b>✅ Auto delete set to {seconds}s!</b>", quote=True)

@Client.on_callback_query(filters.regex(r"^info_maxbtn$"))
async def maxbtn_info(client: Client, query: CallbackQuery):
    text = "<b>🔢 Results Count Setup:\n\n<code>/setmaxbtn 8</code></b>"
    await query.message.reply_text(text=text)
    await query.answer()

@Client.on_message(filters.command("setmaxbtn") & filters.user(ADMINS))
async def save_maxbtn(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>Provide number!</b>", quote=True)
        return
    count = int(message.text.split(None, 1)[1])
    await db.update_setting(message.chat.id, "max_btn", count)
    await message.reply_text(f"<b>✅ Max buttons set to {count}!</b>", quote=True)

@Client.on_callback_query(filters.regex(r"^info_startphoto$"))
async def startphoto_info(client: Client, query: CallbackQuery):
    text = "<b>🌅 Start Photo Setup:\n\nSend a photo and reply to it with <code>/setstartphoto</code> to set it as start photo!</b>"
    await query.message.reply_text(text=text)
    await query.answer()

@Client.on_message(filters.command("setstartphoto") & filters.user(ADMINS))
async def save_start_photo(client: Client, message: Message):
    photo = message.reply_to_message.photo if message.reply_to_message else message.photo
    
    if not photo:
        await message.reply_text("<b>❌ Please reply to a photo or send a photo with /setstartphoto command!</b>", quote=True)
        return
    
    file_id = photo.file_id
    await db.update_setting(message.chat.id, "start_photo", file_id)
    await message.reply_text(f"<b>✅ Start photo updated successfully!</b>", quote=True)

@Client.on_callback_query(filters.regex(r"^info_starttext$"))
async def starttext_info(client: Client, query: CallbackQuery):
    text = "<b>📝 Start Text Setup:\n\n<code>/setstartmsg Your text</code></b>"
    await query.message.reply_text(text=text)
    await query.answer()

@Client.on_message(filters.command("setstartmsg") & filters.user(ADMINS))
async def save_start_msg(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>Provide message text!</b>", quote=True)
        return
    start_text = message.text.split(None, 1)[1]
    await db.update_setting(message.chat.id, "start_text", start_text)
    await message.reply_text(f"<b>✅ Start message updated!</b>", quote=True)
