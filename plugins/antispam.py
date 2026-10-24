import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import db

# സ്പാം ലിങ്കുകളും കീവേഡുകളും കണ്ടെത്താൻ
SPAM_KEYWORDS = ["http://", "https://", "t.me/", "telegram.me/", "www.", "join fast", "crypto", "betting"]

WARNING_STICKER = "CAACAgUAAxkBAAEJ..." # നിങ്ങളുടെ സ്റ്റിക്കറിന്റെ File ID ഇവിടെ നൽകാം

@Client.on_message(filters.group & ~filters.service)
async def anti_spam_handler(client: Client, message: Message):
    if not message.from_user:
        return
        
    chat_id = message.chat.id
    settings = await db.get_settings(chat_id)
    
    # ഗ്രൂപ്പ് സെറ്റിംഗ്സിൽ Anti-Spam ഓഫ് ചെയ്തിട്ടുണ്ടെങ്കിൽ ഒഴിവാക്കാം
    if not settings.get("anti_spam", True):
        return

    # ഗ്രൂപ്പ് ഓണറോ അഡ്മിൻമാരോ ബ്രോഡ്കാസ്റ്റ് വഴി അയക്കുന്ന മെസ്സേജുകൾ/ലിങ്കുകൾ ഒരിക്കലും ഡിലീറ്റ് ചെയ്യരുത്
    try:
        member = await client.get_chat_member(chat_id, message.from_user.id)
        if member.status in ["administrator", "creator"]:
            return
    except Exception:
        pass

    text = message.text or message.caption or ""
    text_lower = text.lower()

    # സാധാരണ യൂസർമാരുടെ മെസ്സേജുകളിൽ ലിങ്കുകളോ സ്പാം വാക്കുകളോ ഉണ്ടോ എന്ന് പരിശോധിക്കുന്നു
    is_spam = any(keyword in text_lower for keyword in SPAM_KEYWORDS)

    if is_spam:
        try:
            # 1. യൂസർ അയച്ച സ്പാം മെസ്സേജ് തൽക്ഷണം ഡിലീറ്റ് ചെയ്യുന്നു
            await message.delete()
            
            # 2. മുന്നറിയിപ്പ് ടെക്സ്റ്റും സ്റ്റിക്കറും അയക്കുന്നു
            warning_text = f"⚠️ <b>Hey {message.from_user.mention}, links and promotions are not allowed in this group! Please stick to movie requests.</b>"
            
            try:
                sticker_msg = await message.reply_sticker(sticker=WARNING_STICKER)
            except Exception:
                sticker_msg = None

            warning_msg = await message.reply_text(text=warning_text)
            
            # 5 സെക്കൻഡിനു ശേഷം മുന്നറിയിപ്പ് ഡിലീറ്റ് ചെയ്യാം
            await asyncio.sleep(5)
            if sticker_msg:
                await sticker_msg.delete()
            await warning_msg.delete()
            
        except Exception as e:
            print(f"Anti-spam deletion error: {e}")
