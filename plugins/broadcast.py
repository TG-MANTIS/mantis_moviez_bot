import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked
from config import ADMINS
from database.database import db

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_users(client: Client, message: Message):
    reply_msg = message.reply_to_message
    if not reply_msg:
        await message.reply_text("<b>Reply to a message!</b>", quote=True)
        return

    m = await message.reply_text("<b>🚀 Users Broadcast started...</b>", quote=True)
    success = 0
    failed = 0
    
    async for user in await db.get_all_users():
        user_id = user.get("user_id")
        try:
            await reply_msg.copy(chat_id=user_id)
            success += 1
            await asyncio.sleep(0.2)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await reply_msg.copy(chat_id=user_id)
                success += 1
            except:
                failed += 1
        except:
            failed += 1

    await m.edit_text(f"<b>📊 Users Broadcast Completed!\nSuccessful: {success}\nFailed: {failed}</b>")

@Client.on_message(filters.command(["gcast", "groupbroadcast"]) & filters.user(ADMINS) & filters.reply)
async def broadcast_groups(client: Client, message: Message):
    reply_msg = message.reply_to_message
    if not reply_msg:
        await message.reply_text("<b>Reply to a message!</b>", quote=True)
        return

    m = await message.reply_text("<b>🚀 Groups Broadcast started...</b>", quote=True)
    success = 0
    failed = 0
    
    async for group in await db.get_all_groups():
        chat_id = group.get("chat_id")
        try:
            await reply_msg.copy(chat_id=chat_id)
            success += 1
            await asyncio.sleep(0.2)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await reply_msg.copy(chat_id=chat_id)
                success += 1
            except:
                failed += 1
        except:
            failed += 1

    await m.edit_text(f"<b>📊 Groups Broadcast Completed!\nSuccessful: {success}\nFailed: {failed}</b>")

@Client.on_message(filters.private & ~filters.user(ADMINS), group=-1)
async def auto_save_users(client, message):
    await db.add_user(message.from_user.id)
    message.continue_propagation()

@Client.on_message(filters.group, group=-1)
async def auto_save_groups(client, message):
    await db.add_group(message.chat.id)
    message.continue_propagation()
