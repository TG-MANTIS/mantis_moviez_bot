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
            InlineKeyboardButton(f"📢 Force Sub (F-Sub)", callback_data="info_fsub"),
            InlineKeyboardButton(f"🎬 IMDb Poster: {imdb_status}", callback_data="toggle_imdb")
        ],
        [
            InlineKeyboardButton(f"📢 F-Sub: {fsub_status}", callback_data="toggle_fsub"),
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
        text="<b>⚙️ ബോട്ട് കൺട്രോൾ സെറ്റിംഗ്സ് പാനൽ:\n\nതാഴെയുള്ള ഓപ്ഷനുകൾ ഉപയോഗിച്ച് ഫീച്ചറുകൾ On/Off ചെയ്യുകയോ അല്ലെങ്കിൽ ബട്ടണുകൾ ക്ലിക്ക് ചെയ്ത് വിശദമായ നിർദ്ദേശങ്ങൾ അറിയുകയോ ചെയ്യാം:</b>",
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
        await query.answer(f"Welcome Message {'ON' if new_val else 'OFF'} ആക്കി!")

    elif data == "toggle_goodbye":
        new_val = not settings.get("goodbye", True)
        await db.update_setting(chat_id, "goodbye", new_val)
        await query.answer(f"Goodbye Message {'ON' if new_val else 'OFF'} ആക്കി!")

    elif data == "toggle_fsub":
        new_val = not settings.get("f_sub", True)
        await db.update_setting(chat_id, "f_sub", new_val)
        await query.answer(f"Force Subscription {'ON' if new_val else 'OFF'} ആക്കി!")

    elif data == "toggle_imdb":
        new_val = not settings.get("imdb", True)
        await db.update_setting(chat_id, "imdb", new_val)
        await query.answer(f"IMDb Poster Support {'ON' if new_val else 'OFF'} ആക്കി!")

    # അപ്ഡേറ്റ് ചെയ്ത ബട്ടണുകൾ വീണ്ടും ലോഡ് ചെയ്യുന്നു
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

# 1. Force Sub (F-Sub) ഇൻസ്ട്രക്ഷൻ നൽകുന്ന ഭാഗം
@Client.on_callback_query(filters.regex(r"^info_fsub$"))
async def fsub_info(client: Client, query: CallbackQuery):
    text = (
        "<b>📢 Force Subscription (F-Sub) സജ്ജീകരിക്കുന്നതിനുള്ള നിർദ്ദേശങ്ങൾ:</b>\n\n"
        "യൂസർമാർക്ക് ഫയലുകൾ ലഭിക്കുന്നതിന് മുമ്പ് നിങ്ങളുടെ അപ്ഡേറ്റ് ചാനലിൽ ജോയിൻ ചെയ്യാൻ നിർബന്ധിതമാക്കുന്ന ഫീച്ചറാണിത്.\n\n"
        "<b>എങ്ങനെ സെറ്റ് ചെയ്യാം?</b>\n"
        "ബോട്ടിന്റെ പ്രൈവറ്റ് ചാറ്റിൽ താഴെ കാണുന്ന കമാൻഡ് അയക്കുക:\n"
        "<code>/setfsub ചാനൽ_ഐഡി</code>\n\n"
        "<b>ഉദാഹരണം:</b>\n"
        "<code>/setfsub -1001234567890</code>\n\n"
        "<i>(ശ്രദ്ധിക്കുക: നിങ്ങളുടെ ബോട്ടിനെ ആ ചാനലിൽ അഡ്മിൻ (Admin) ആയി ചേർത്തിരിക്കണം).</i>"
    )
    await query.message.reply_text(text=text)
    await query.answer()

@Client.on_message(filters.command("setfsub") & filters.user(ADMINS))
async def save_fsub_channel(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>ദയവായി ചാനൽ ഐഡി കൂടി നൽകുക!</b>\nഉദാഹരണം: `/setfsub -1001234567890`", quote=True)
        return
    
    channel_id = message.text.split(None, 1)[1].strip()
    await db.update_setting(message.chat.id, "f_sub_channel", channel_id)
    await message.reply_text(f"<b>✅ Force Subscription ചാനൽ ഐഡി വിജയികരമായി സേവ് ചെയ്തിരിക്കുന്നു!</b>\n\nID: `{channel_id}`", quote=True)

# 2. Set Custom Photo ഇൻസ്ട്രക്ഷൻ നൽകുന്ന ഭാഗം
@Client.on_callback_query(filters.regex(r"^info_photo$"))
async def photo_info(client: Client, query: CallbackQuery):
    text = (
        "<b>🖼️ കസ്റ്റം ഫോട്ടോ/പോസ്റ്റർ സജ്ജീകരിക്കുന്നതിനുള്ള നിർദ്ദേശങ്ങൾ:</b>\n\n"
        "IMDb Poster ഫീച്ചർ OFF ആക്കി വെക്കുമ്പോൾ, ഫയലുകൾ അയക്കുമ്പോൾ കൂടെ കാണിക്കേണ്ട സ്വന്തം ഫോട്ടോ അല്ലെങ്കിൽ തംബ്‌നെയിൽ ഇവിടെ സെറ്റ് ചെയ്യാം.\n\n"
        "<b>എങ്ങനെ സെറ്റ് ചെയ്യാം?</b>\n"
        "ബോട്ടിന്റെ പ്രൈവറ്റ് ചാറ്റിൽ താഴെ കാണുന്ന കമാൻഡ് അയക്കുക:\n"
        "<code>/setphoto ഫോട്ടോയുടെ_ഡയറക്ട്_ലിങ്ക്</code>\n\n"
        "<b>ഉദാഹരണം:</b>\n"
        "<code>/setphoto https://telegra.ph/file/sample.jpg</code>\n\n"
        "<i>(സൂചന: Telegra.ph വഴിയോ അല്ലെങ്കിൽ ഏതെങ്കിലും ഇമേജ് ഹോസ്റ്റിംഗ് സൈറ്റ് വഴിയോ ഫോട്ടോ അപ്‌ലോഡ് ചെയ്ത് അതിന്റെ Direct URL ഇവിടെ നൽകാവുന്നതാണ്).</i>"
    )
    await query.message.reply_text(text=text)
    await query.answer()

@Client.on_message(filters.command("setphoto") & filters.user(ADMINS))
async def save_custom_photo(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>ദയവായി ഫോട്ടോയുടെ URL ലിങ്ക് നൽകുക!</b>\nഉദാഹരണം: `/setphoto https://telegra.ph/file/sample.jpg`", quote=True)
        return
    
    photo_url = message.text.split(None, 1)[1].strip()
    await db.update_setting(message.chat.id, "custom_photo", photo_url)
    await message.reply_text(f"<b>✅ കസ്റ്റം ഫോട്ടോ വിജയികരമായി അപ്ഡേറ്റ് ചെയ്തിരിക്കുന്നു!</b>\n\n`{photo_url}`", quote=True)

# 3. Set Custom Caption വിപുലമായ ഇൻസ്ട്രക്ഷൻ നൽകുന്ന ഭാഗം
@Client.on_callback_query(filters.regex(r"^info_caption$"))
async def caption_info(client: Client, query: CallbackQuery):
    text = (
        "<b>📝 കസ്റ്റം ക്യാപ്ഷൻ സജ്ജീകരിക്കുന്നതിനുള്ള സമ്പൂർണ്ണ ഗൈഡ്:</b>\n\n"
        "ഫയലുകൾ യൂസർക്ക് സെൻ്റ് ചെയ്യുമ്പോൾ കൂടെ വരുന്ന ക്യാപ്ഷൻ നിങ്ങളുടെ ഇഷ്ടപ്രകാരം മനോഹരമായി ഡിസൈൻ ചെയ്യാം.\n\n"
        "<b>എങ്ങനെ സെറ്റ് ചെയ്യാം?</b>\n"
        "<code>/setcaption നിങ്ങളുടെ ക്യാപ്ഷൻ ടെക്സ്റ്റ് ഇവിടെ നൽകുക</code>\n\n"
        "<b>ഉപയോഗിക്കാവുന്ന വേരിയബിളുകൾ (Variables):</b>\n"
        "• <code>{file_name}</code> - ഫയലിന്റെ ഒറിജിനൽ പേര് കാണിക്കാൻ\n"
        "• <code>{file_size}</code> - ഫയലിന്റെ സൈസ് കാണിക്കാൻ\n\n"
        "<b>സ്റ്റൈലിങ് & ലിങ്കുകൾ ചേർക്കുന്ന വിധം (HTML Formatting):</b>\n"
        "• <b>Bold (കട്ടിയുള്ള അക്ഷരങ്ങൾ):</b> `<b>നിങ്ങളുടെ ടെക്സ്റ്റ്</b>`\n"
        "• <i>Italic (ചരിഞ്ഞ അക്ഷരങ്ങൾ):</i> `<i>നിങ്ങളുടെ ടെക്സ്റ്റ്</i>`\n"
        "• <u>Underline (അടിവരയിട്ടത്):</u> `<u>നിങ്ങളുടെ ടെക്സ്റ്റ്</u>`\n"
        "• <b>ചാനൽ ലിങ്ക് ടെക്സ്റ്റ് കൊടുക്കാൻ:</b> `[ചാനൽ പേര്](https://t.me/YourChannel)` അല്ലെങ്കിൽ HTML ടാഗ് ഉപയോഗിച്ച് `[Link Text](https://t.me/YourChannel)` നൽകാം.\n"
        "• <b>ഇമോജികൾ:</b> നിങ്ങൾക്ക് ഇഷ്ടമുള്ളതുപോലെ 📁, 🎬, 🔥, ⚡ തുടങ്ങിയ ഇമോജികൾ ചേർത്ത് ഭംഗിയാക്കാം.\n\n"
        "<b>മാതൃകാ ക്യാപ്ഷൻ (Sample Template):</b>\n"
        "<code>/setcaption 📁 ഫയൽ: {file_name}\n📦 സൈസ്: {file_size}\n\n✨ കൂടുതൽ മൂവികൾക്കായി ജോയിൻ ചെയ്യൂ: @YourChannel</code>"
    )
    await query.message.reply_text(text=text)
    await query.answer()

@Client.on_message(filters.command("setcaption") & filters.user(ADMINS))
async def save_custom_caption(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("<b>ദയവായി ക്യാപ്ഷൻ ടെക്സ്റ്റ് കൂടി നൽകുക!</b>", quote=True)
        return
    
    caption_text = message.text.split(None, 1)[1]
    await db.update_setting(message.chat.id, "caption", caption_text)
    await message.reply_text(f"<b>✅ കസ്റ്റം ക്യാപ്ഷൻ വിജയികരമായി അപ്ഡേറ്റ് ചെയ്തിരിക്കുന്നു!</b>\n\n<b>New Caption:</b>\n{caption_text}", quote=True)
