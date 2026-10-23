import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from database.database import db
from config import ADMINS

# ഇൻഡക്സിങ് പ്രോസസ്സ് കൺട്രോൾ ചെയ്യാൻ ഒരു ഗ്ലോബൽ ഡിക്ഷ്ണറി
CANCEL_INDEX = {}

# 1. DB ചാനലിൽ നിന്നും ബോട്ടിന്റെ പ്രൈവറ്റ് ചാറ്റിലേക്ക് ഫയൽ ഫോർവേഡ് ചെയ്യുമ്പോൾ
@Client.on_message(filters.private & filters.user(ADMINS) & filters.forwarded & ~filters.command(["start", "settings", "broadcast"]))
async def index_forward_handler(client: Client, message: Message):
    # ഫോർവേഡ് ചെയ്ത മെസ്സേജിൽ മീഡിയ (വീഡിയോ, ഡോക്യുമെന്റ് മുതലായവ) ഉണ്ടോ എന്ന് നോക്കുന്നു
    media = message.video or message.document or message.audio
    
    if not media:
        await message.reply_text("<b>⚠️ Please forward a file/media message from your Database Channel!</b>", quote=True)
        return

    # മെസ്സേജിൽ നിന്ന് ഒറിജിനൽ ചാറ്റ് ഐഡിയും മെസ്സേജ് ഐഡിയും എടുക്കുന്നു
    forward_from = message.forward_from_chat
    if not forward_from:
        await message.reply_text("<b>⚠️ This does not look like a forwarded message from a channel. Please forward directly from your DB Channel!</b>", quote=True)
        return

    db_channel_id = forward_from.id
    start_message_id = message.forward_from_message_id

    buttons = [
        [
            InlineKeyboardButton("✅ Yes, Start Indexing", callback_data=f"start_index#{db_channel_id}#{start_message_id}"),
            InlineKeyboardButton("❌ No, Cancel", callback_data="cancel_index")
        ]
    ]

    await message.reply_text(
        text=(
            "<b>📊 Database Indexing Request Detected!\n\n"
            f"📁 Channel ID: <code>{db_channel_id}</code>\n"
            f"🔢 Start Message ID: <code>{start_message_id}</code>\n\n"
            "Do you want to add files from this channel to the bot database?</b>"
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True
    )

# 2. 'No' ബട്ടൺ ക്ലിക്ക് ചെയ്യുമ്പോൾ
@Client.on_callback_query(filters.regex(r"^cancel_index$"))
async def cancel_index_query(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        "<b>❌ You selected No. Database indexing has been cancelled, and no files were added to the database.</b>"
    )
    await query.answer()

# 3. 'Yes' ബട്ടൺ ക്ലിക്ക് ചെയ്ത് പ്രൊസസ്സ് ആരംഭിക്കുമ്പോൾ
@Client.on_callback_query(filters.regex(r"^start_index#"))
async def start_indexing_process(client: Client, query: CallbackQuery):
    _, db_channel_id, start_message_id = query.data.split("#")
    db_channel_id = int(db_channel_id)
    start_message_id = int(start_message_id)
    user_id = query.from_user.id
    
    CANCEL_INDEX[user_id] = False

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⏹️ Stop / Cancel Indexing", callback_data=f"stop_process#{user_id}")]
    ])

    status_msg = await query.message.edit_text(
        text="<b>🚀 Indexing process started...\n\n⏳ Scanning messages, please wait...</b>",
        reply_markup=buttons
    )
    await query.answer()

    added_files = 0
    duplicates = 0
    videos = 0
    documents = 0
    others = 0
    current_msg_id = start_message_id

    # അവസാനം വരെ ലൂപ്പ് ചെയ്ത് ഫയലുകൾ ഇൻഡക്സ് ചെയ്യുന്നു
    try:
        # ബോട്ടിന്റെ പ്രൈവറ്റ് ചാറ്റിൽ നിന്ന് DB ചാനലിലെ ഏറ്റവും പുതിയ മെസ്സേജ് വരെ പരിശോധിക്കാം
        # (ഇവിടെ സുരക്ഷിതമായി ലൂപ്പ് റൺ ചെയ്യാൻ ഒരു റേഞ്ച് ഉപയോഗിക്കുന്നു)
        async for message in client.get_chat_history(db_channel_id, limit=5000):
            # യൂസർ സ്റ്റോപ്പ് ബട്ടൺ അമർത്തിയാൽ ലൂപ്പ് നിർത്തും
            if CANCEL_INDEX.get(user_id, False):
                await status_msg.edit_text("<b>⚠️ Indexing process was stopped by the admin!</b>")
                return

            media = message.video or message.document or message.audio
            if media:
                file_id = media.file_id
                file_name = media.file_name or "Unknown_File.mp4"
                file_size = message.utils.get_size(media.file_size) if hasattr(message, "utils") else f"{round(media.file_size / (1024 * 1024), 2)} MB"

                if message.video:
                    videos += 1
                elif message.document:
                    documents += 1
                else:
                    others += 1

                # ഡാറ്റാബേസിൽ ഫയൽ സേവ് ചെയ്യുക (Duplicate check ഉൾപ്പെടുത്തി)
                is_saved = await db.save_file_unique(file_id, file_name, file_size)
                if is_saved:
                    added_files += 1
                else:
                    duplicates += 1

                # ഓരോ 10 ഫയലുകൾ കൂടുമ്പോഴും ലൈവ് പ്രോഗ്രസ്സ് അപ്ഡേറ്റ് ചെയ്യുക
                if (added_files + duplicates) % 5 == 0:
                    await status_msg.edit_text(
                        text=(
                            f"<b>📊 Indexing in Progress...\n\n"
                            f"📁 Total Scanned: {added_files + duplicates}\n"
                            f"✅ Successfully Added: {added_files}\n"
                            f"🔄 Duplicates Skipped: {duplicates}\n"
                            f"🎬 Videos: {videos}\n"
                            f"📦 Documents: {documents}\n\n"
                            f"⏳ Status: Running...</b>"
                        ),
                        reply_markup=buttons
                    )
            await asyncio.sleep(0.1)

        await status_msg.edit_text(
            text=(
                f"<b>🎉 Database Indexing Completed Successfully!\n\n"
                f"✅ Successfully Added: {added_files}\n"
                f"🔄 Duplicates Skipped: {duplicates}\n"
                f"🎬 Total Videos: {videos}\n"
                f"📦 Total Documents: {documents}</b>"
            )
        )

    except Exception as e:
        await status_msg.edit_text(f"<b>❌ An error occurred during indexing:</b>\n<code>{str(e)}</code>")

# 4. പ്രൊസസ്സ് നടക്കുന്ന വഴിയിൽ 'Stop' ബട്ടൺ ക്ലിക്ക് ചെയ്യുമ്പോൾ
@Client.on_callback_query(filters.regex(r"^stop_process#"))
async def stop_indexing_process(client: Client, query: CallbackQuery):
    user_id = int(query.data.split("#")[1])
    if query.from_user.id == user_id:
        CANCEL_INDEX[user_id] = True
        await query.answer("Indexing stop signal sent!", show_alert=True)
    else:
        await query.answer("You are not authorized to stop this process!", show_alert=True)
