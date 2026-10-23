import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked
from config import ADMINS
from database.database import db

# 1. User Broadcast Command: /broadcast
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_users(client: Client, message: Message):
    reply_msg = message.reply_to_message
    if not reply_msg:
        await message.reply_text("<b>Please reply to a message to broadcast to users!</b>", quote=True)
        return

    m = await message.reply_text("<b>🚀 Users Broadcast started... Please wait.</b>", quote=True)
    
    success_users = 0
    failed_users = 0
    
    async for user in await db.get_all_users():
        user_id = user.get("user_id")
        try:
            await reply_msg.copy(chat_id=user_id)
            success_users += 1
            await asyncio.sleep(0.2)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await reply_msg.copy(chat_id=user_id)
                success_users += 1
            except:
                failed_users += 1
        except (InputUserDeactivated, UserIsBlocked):
            failed_users += 1
        except Exception:
            failed_users += 1

    report = (
        f"<b>📊 Users Broadcast Completed!\n\n"
        f"👥 Successful: {success_users}\n"
        f"❌ Failed: {failed_users}</b>"
    )
    await m.edit_text(report)


# 2. Group Broadcast Command: /gcast (അല്ലെങ്കിൽ /groupbroadcast)
@Client.on_message(filters.command(["gcast", "groupbroadcast"]) & filters.user(ADMINS) & filters.reply)
async def broadcast_groups(client: Client, message: Message):
    reply_msg = message.reply_to_message
    if not reply_msg:
        await message.reply_text("<b>Please reply to a message to broadcast to groups!</b>", quote=True)
        return

    m = await message.reply_text("<b>🚀 Groups Broadcast started... Please wait.</b>", quote=True)
    
    success_groups = 0
    failed_groups = 0
    
    async for group in await db.get_all_groups():
        chat_id = group.get("chat_id")
        try:
            await reply_msg.copy(chat_id=chat_id)
            success_groups += 1
            await asyncio.sleep(0.2)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await reply_msg.copy(chat_id=chat_id)
                success_groups += 1
            except:
                failed_groups += 1
        except Exception:
            failed_groups += 1

    report = (
        f"<b>📊 Groups Broadcast Completed!\n\n"
        f"🏢 Successful: {success_groups}\n"
        f"❌ Failed: {failed_groups}</b>"
    )
    await m.edit_text(report)


# ഓട്ടോമാറ്റിക് ആയി യൂസർമാരെയും ഗ്രൂപ്പുകളെയും ഡാറ്റാബേസിൽ സേവ് ചെയ്യാൻ
@Client.on_message(filters.private & ~filters.user(ADMINS), group=-1)
async def auto_save_users(client, message):
    await db.add_user(message.from_user.id)
    message.continue_propagation()

@Client.on_message(filters.group, group=-1)
async def auto_save_groups(client, message):
    await db.add_group(message.chat.id)
    message.continue_propagation()
