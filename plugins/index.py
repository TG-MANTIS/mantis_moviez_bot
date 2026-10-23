import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from database.database import db
from config import ADMINS

CANCEL_INDEX = {}

@Client.on_message(filters.private & filters.user(ADMINS) & filters.forwarded & ~filters.command(["start", "settings", "broadcast"]))
async def index_forward_handler(client: Client, message: Message):
    media = message.video or message.document or message.audio
    if not media:
        await message.reply_text("<b>⚠️ Please forward a file from your DB Channel!</b>", quote=True)
        return

    forward_from = message.forward_from_chat
    if not forward_from:
        await message.reply_text("<b>⚠️ Forward directly from your DB Channel!</b>", quote=True)
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
            "<b>📊 Database Indexing Request:\n\n"
            f"📁 Channel ID: <code>{db_channel_id}</code>\n"
            f"🔢 Start Message ID: <code>{start_message_id}</code>\n\n"
            "Do you want to add files?</b>"
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True
    )

@Client.on_callback_query(filters.regex(r"^cancel_index$"))
async def cancel_index_query(client: Client, query: CallbackQuery):
    await query.message.edit_text("<b>❌ Indexing cancelled.</b>")
    await query.answer()

@Client.on_callback_query(filters.regex(r"^start_index#"))
async def start_indexing_process(client: Client, query: CallbackQuery):
    _, db_channel_id, start_message_id = query.data.split("#")
    db_channel_id = int(db_channel_id)
    start_message_id = int(start_message_id)
    user_id = query.from_user.id
    
    CANCEL_INDEX[user_id] = False

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⏹️ Stop Indexing", callback_data=f"stop_process#{user_id}")]
    ])

    status_msg = await query.message.edit_text(
        text="<b>🚀 Indexing started...</b>",
        reply_markup=buttons
    )
    await query.answer()

    added_files = 0
    duplicates = 0
    videos = 0
    documents = 0

    try:
        async for message in client.get_chat_history(db_channel_id, limit=5000):
            if CANCEL_INDEX.get(user_id, False):
                await status_msg.edit_text("<b>⚠️ Indexing stopped by admin!</b>")
                return

            media = message.video or message.document or message.audio
            if media:
                file_id = media.file_id
                file_name = media.file_name or "Unknown_File.mp4"
                file_size = f"{round(media.file_size / (1024 * 1024), 2)} MB"

                if message.video:
                    videos += 1
                elif message.document:
                    documents += 1

                is_saved = await db.save_file_unique(file_id, file_name, file_size)
                if is_saved:
                    added_files += 1
                else:
                    duplicates += 1

                if (added_files + duplicates) % 5 == 0:
                    await status_msg.edit_text(
                        text=(
                            f"<b>📊 Indexing in Progress...\n\n"
                            f"📁 Scanned: {added_files + duplicates}\n"
                            f"✅ Added: {added_files}\n"
                            f"🔄 Duplicates: {duplicates}\n"
                            f"🎬 Videos: {videos}\n"
                            f"📦 Documents: {documents}</b>"
                        ),
                        reply_markup=buttons
                    )
            await asyncio.sleep(0.1)

        await status_msg.edit_text(
            text=(
                f"<b>🎉 Indexing Completed!\n\n"
                f"✅ Added: {added_files}\n"
                f"🔄 Duplicates: {duplicates}\n"
                f"🎬 Videos: {videos}\n"
                f"📦 Documents: {documents}</b>"
            )
        )
    except Exception as e:
        await status_msg.edit_text(f"<b>❌ Error:</b>\n<code>{str(e)}</code>")

@Client.on_callback_query(filters.regex(r"^stop_process#"))
async def stop_indexing_process(client: Client, query: CallbackQuery):
    user_id = int(query.data.split("#")[1])
    if query.from_user.id == user_id:
        CANCEL_INDEX[user_id] = True
        await query.answer("Stop signal sent!", show_alert=True)
