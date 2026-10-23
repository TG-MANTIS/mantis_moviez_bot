from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from database.database import db
import datetime

# റിലീസ് ആവാത്തതോ വരാനിരിക്കുന്നതോ ആയ സിനിമകൾ തിരിച്ചറിയാനുള്ള ചില പ്രധാന വാക്കുകൾ (Keywords)
UPCOMING_KEYWORDS = ["upcoming", "teaser", "trailer", "release", "2027", "2028", "announcement", "first look"]

@Client.on_message(filters.text & ~filters.command(["start", "index"]) & (filters.group | filters.private))
async def auto_filter(client: Client, message: Message):
    if message.text.startswith("/"):
        return
    
    query = message.text.strip()
    if len(query) < 2:
        return

    query_lower = query.lower()

    # 1. റിലീസ് ആവാത്ത മൂവികളാണോ എന്ന് പരിശോധിക്കുന്നു
    for word in UPCOMING_KEYWORDS:
        if word in query_lower:
            await message.reply_text(
                text=f"❌ <b>ക്ഷമിക്കണം! '{query}' ഇതുവരെ തിയേറ്ററിലോ ഒടിടിയിലോ റിലീസ് ആയിട്ടില്ല. അതിനാൽ ഈ മൂവി നൽകാൻ കഴിയുന്നതല്ല.</b>",
                quote=True
            )
            return

    # 2. ഡാറ്റാബേസിൽ നിന്ന് ഫയലുകൾ തെരയുന്നു
    files = await db.search_files(query)

    if not files:
        # ഡാറ്റാബേസിൽ ഇല്ലെങ്കിൽ ലഭ്യമല്ല എന്ന മെസ്സേജ് അയക്കുന്നു
        await message.reply_text(
            text=f"⚠️ <b>നിങ്ങൾ ചോദിച്ച '{query}' എന്ന മൂവി നിലവിൽ ഞങ്ങളുടെ ഡാറ്റാബേസിൽ ആഡ് ചെയ്തിട്ടില്ല. ദയവായി പിന്നീട് ശ്രമിക്കുക!</b>",
            quote=True
        )
        return

    # ഫയലുകൾ ഉണ്ടെങ്കിൽ ലാംഗ്വേജും ക്വാളിറ്റിയും തിരഞ്ഞെടുക്കാനുള്ള ഡ്യുവൽ ബട്ടണുകൾ കാണിക്കുന്നു
    buttons = [
        [
            InlineKeyboardButton("🌐 Language", callback_data=f"lang_menu#{query}"),
            InlineKeyboardButton("🎬 Quality", callback_data=f"qual_menu#{query}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await message.reply_text(
        text=f"<b>ഫലം കണ്ടെത്തി: <code>{query}</code>\nതാഴെയുള്ള ഓപ്ഷനുകൾ ഉപയോഗിച്ച് ഫിൽട്ടർ ചെയ്യുക:</b>",
        reply_markup=reply_markup,
        quote=True
    )

# ബട്ടണുകൾ ക്ലിക്ക് ചെയ്യുമ്പോൾ വർക്ക് ചെയ്യുന്ന ഭാഗം (Callback Query Handler)
@Client.on_callback_query()
async def callback_handler(client: Client, query_data: CallbackQuery):
    data = query_data.data
    
    if data.startswith("lang_menu#"):
        movie_query = data.split("#")[1]
        buttons = [
            [
                InlineKeyboardButton("Malayalam", callback_data=f"filter#{movie_query}#Malayalam#None"),
                InlineKeyboardButton("Tamil", callback_data=f"filter#{movie_query}#Tamil#None")
            ],
            [
                InlineKeyboardButton("English", callback_data=f"filter#{movie_query}#English#None"),
                InlineKeyboardButton("Kannada", callback_data=f"filter#{movie_query}#Kannada#None")
            ],
            [InlineKeyboardButton("« Back", callback_data=f"back#{movie_query}")]
        ]
        await query_data.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("qual_menu#"):
        movie_query = data.split("#")[1]
        buttons = [
            [
                InlineKeyboardButton("480p", callback_data=f"filter#{movie_query}#None#480p"),
                InlineKeyboardButton("720p", callback_data=f"filter#{movie_query}#None#720p")
            ],
            [
                InlineKeyboardButton("1080p", callback_data=f"filter#{movie_query}#None#1080p"),
                InlineKeyboardButton("4K", callback_data=f"filter#{movie_query}#None#4K")
            ],
            [InlineKeyboardButton("« Back", callback_data=f"back#{movie_query}")]
        ]
        await query_data.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("back#"):
        movie_query = data.split("#")[1]
        buttons = [
            [
                InlineKeyboardButton("🌐 Language", callback_data=f"lang_menu#{movie_query}"),
                InlineKeyboardButton("🎬 Quality", callback_data=f"qual_menu#{movie_query}")
            ]
        ]
        await query_data.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("filter#"):
        _, movie_query, lang, qual = data.split("#")
        lang_val = None if lang == "None" else lang
        qual_val = None if qual == "None" else qual

        files = await db.filter_files(movie_query, lang_val, qual_val)

        if not files:
            await query_data.answer("ക്ഷമിക്കണം, ഈ ഫിൽട്ടറിൽ ഫയലുകൾ ലഭ്യമല്ല!", show_alert=True)
            return

        buttons = []
        for file in files:
            file_name = file["file_name"]
            file_id = file["file_id"]
            quality = file.get("quality", "Unknown")
            language = file.get("language", "Unknown")
            
            btn_text = f"📁 {file_name} [{quality}] [{language}]"
            buttons.append(
                [InlineKeyboardButton(btn_text, callback_data=f"get#{file_id}")]
            )
        
        buttons.append([InlineKeyboardButton("« Back to Menu", callback_data=f"back#{movie_query}")])

        reply_markup = InlineKeyboardMarkup(buttons)
        await query_data.message.edit_text(
            text=f"<b>ഫിൽട്ടർ ചെയ്ത ഫയലുകൾ (Language: {lang}, Quality: {qual}):</b>",
            reply_markup=reply_markup
        )
