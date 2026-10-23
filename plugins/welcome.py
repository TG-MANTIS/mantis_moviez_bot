from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import db

@Client.on_message(filters.new_chat_members)
async def welcome_user(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await db.get_settings(chat_id)
    
    # സെറ്റിംഗ്സിൽ വെൽക്കം OFF ആണെങ്കിൽ ഒന്നും ചെയ്യില്ല
    if not settings.get("welcome", True):
        return

    for user in message.new_chat_members:
        # ബോട്ട് തന്നെ ജോയിൻ ചെയ്യുമ്പോൾ ഉള്ള റിപ്ലൈ
        if user.id == client.me.id:
            await message.reply_text("<b>👋 Hello! Auto-Filter has been successfully enabled in this group.</b>")
            continue
        
        # പുതിയ മെമ്പർക്ക് ഉള്ള വെൽക്കം മെസ്സേജ്
        await message.reply_text(
            text=f"<b>Welcome {user.mention} to our group! 🎉\nFeel free to request your favorite movies and series here!</b>"
        )

@Client.on_message(filters.left_chat_member)
async def goodbye_user(client: Client, message: Message):
    chat_id = message.chat.id
    settings = await db.get_settings(chat_id)
    
    # സെറ്റിംഗ്സിൽ ഗുഡ്‌ബൈ OFF ആണെങ്കിൽ ഒന്നും ചെയ്യില്ല
    if not settings.get("goodbye", True):
        return

    user = message.left_chat_member
    if user.id == client.me.id:
        return

    # ഗ്രൂപ്പ് വിട്ടുപോകുന്നവർക്കുള്ള ഗുഡ്‌ബൈ മെസ്സേജ്
    await message.reply_text(
        text=f"<b>Goodbye {user.mention}! See you again! 👋</b>"
    )
