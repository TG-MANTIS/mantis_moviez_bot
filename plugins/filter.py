import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from database.database import db

UPCOMING_KEYWORDS = ["upcoming", "teaser", "trailer", "release", "2027", "2028", "announcement", "first look"]

@Client.on_message(filters.text & ~filters.command(["start", "index"]) & (filters.group | filters.private))
async def auto_filter(client: Client, message: Message):
    if message.text.startswith("/"):
        return
    
    query = message.text.strip()
    if len(query) < 2:
        return

    query_lower = query.lower()
    chat_id = message.chat.id
    settings = await db.get_settings(chat_id)

    for word in UPCOMING_KEYWORDS:
        if word in query_lower:
            reply = await message.reply_text(
                text=f"❌ <b>Sorry! '{query}' has not been released yet.</b>",
                quote=True
            )
            await handle_auto_delete(reply, settings)
            return

    files = await db.search_files(query)

    if not files:
        reply = await message.reply_text(
            text=f"⚠️ <b>The movie/series '{query}' you requested is not found!</b>",
            quote=True
        )
        await handle_auto_delete(reply, settings)
        return

    max_btn = settings.get("max_btn", 8)
    buttons = []
    
    for file in files[:max_btn]:
        file_name = file["file_name"]
        file_id = file["file_id"]
        file_size = file.get("file_size", "N/A")
        buttons.append([InlineKeyboardButton(f"📁 {file_size} | {file_name}", callback_data=f"file#{file_id}")])

    if len(files) > max_btn:
        buttons.append([InlineKeyboardButton(f"1/{len(files)//max_btn + 1} ➔", callback_data=f"next#{query}#1")])

    buttons.append([
        InlineKeyboardButton("🌐 Language", callback_data=f"lang_menu#{query}"),
        InlineKeyboardButton("🎬 Quality", callback_data=f"qual_menu#{query}")
    ])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    reply = await message.reply_text(
        text=f"<b>Results found for: <code>{query}</code>\nSelect your file below:</b>",
        reply_markup=reply_markup,
        quote=True
    )
    await handle_auto_delete(reply, settings)

@Client.on_callback_query()
async def callback_handler(client: Client, query_data: CallbackQuery):
    data = query_data.data
    chat_id = query_data.message.chat.id
    settings = await db.get_settings(chat_id)

    if data.startswith("next#") or data.startswith("back#"):
        _, movie_query, page = data.split("#")
        page = int(page)
        max_btn = settings.get("max_btn", 8)
        
        files = await db.search_files(movie_query)
        total_pages = len(files) // max_btn + (1 if len(files) % max_btn > 0 else 0)
        
        start_idx = page * max_btn
        end_idx = start_idx + max_btn
        current_files = files[start_idx:end_idx]

        buttons = []
        for file in current_files:
            file_name = file["file_name"]
            file_id = file["file_id"]
            file_size = file.get("file_size", "N/A")
            buttons.append([InlineKeyboardButton(f"📁 {file_size} |  {file_name}", callback_data=f"file#{file_id}")])

        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"back#{movie_query}#{page-1}"))
        
        nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="pages"))

        if page + 1 < total_pages:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"next#{movie_query}#{page+1}"))

        buttons.append(nav_buttons)
        buttons.append([
            InlineKeyboardButton("🌐 Language", callback_data=f"lang_menu#{movie_query}"),
            InlineKeyboardButton("🎬 Quality", callback_data=f"qual_menu#{movie_query}")
        ])

        await query_data.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
        await query_data.answer()

    elif data.startswith("lang_menu#"):
        movie_query = data.split("#")[1]
        buttons = [
            [
                InlineKeyboardButton("Malayalam", callback_data=f"filter#{movie_query}#Malayalam#None"),
                InlineKeyboardButton("Tamil", callback_data=f"filter#{movie_query}#Tamil#None")
            ],
            [
                InlineKeyboardButton("Telugu", callback_data=f"filter#{movie_query}#Telugu#None"),
                InlineKeyboardButton("Kannada", callback_data=f"filter#{movie_query}#Kannada#None")
            ],
            [
                InlineKeyboardButton("Hindi", callback_data=f"filter#{movie_query}#Hindi#None"),
                InlineKeyboardButton("English", callback_data=f"filter#{movie_query}#English#None")
            ],
            [InlineKeyboardButton("« Home Menu", callback_data=f"home#{movie_query}")]
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
            [InlineKeyboardButton("« Home Menu", callback_data=f"home#{movie_query}")]
        ]
        await query_data.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("home#"):
        movie_query = data.split("#")[1]
        files = await db.search_files(movie_query)
        max_btn = settings.get("max_btn", 8)
        
        buttons = []
        for file in files[:max_btn]:
            buttons.append([InlineKeyboardButton(f"📁 {file['file_name']} | 📦 {file.get('file_size', 'N/A')}", callback_data=f"file#{file['file_id']}")])
        
        buttons.append([
            InlineKeyboardButton("🌐 Language", callback_data=f"lang_menu#{movie_query}"),
            InlineKeyboardButton("🎬 Quality", callback_data=f"qual_menu#{movie_query}")
        ])
        await query_data.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("filter#"):
        _, movie_query, lang, qual = data.split("#")
        lang_val = None if lang == "None" else lang
        qual_val = None if qual == "None" else qual

        files = await db.filter_files(movie_query, lang_val, qual_val)
        if not files:
            await query_data.answer("No files available!", show_alert=True)
            return

        buttons = []
        for file in files[:10]:
            buttons.append([InlineKeyboardButton(f"📁 {file['file_name']} | 📦 {file.get('file_size', 'N/A')}", callback_data=f"file#{file['file_id']}")])
        
        buttons.append([InlineKeyboardButton("« Home Menu", callback_data=f"home#{movie_query}")])
        await query_data.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

async def handle_auto_delete(message: Message, settings: dict):
    auto_del_time = settings.get("auto_delete", 300)
    if auto_del_time > 0:
        await asyncio.sleep(auto_del_time)
        try:
            await message.delete()
        except:
            pass
