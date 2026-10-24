import asyncio
from pyrogram import Client
from aiohttp import web
from web import web_server
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

async def main():
    # bot start 
    await app.start()
    print("Bot Started Successfully!")
    
    # റെണ്ടറിനായി വെബ് സർവർ സ്റ്റാർട്ട് ചെയ്യുന്നു
    runner = web.AppRunner(await web_server())
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print("Web Server Started Successfully!")
    
    # ബോട്ട് നിർന്നുപോകാതെ റൺ ചെയ്തുകൊണ്ടിരിക്കാൻ
    await asyncio.Event().wait()

if __name__ == "__main__":
    # ഇവന്റ് ലൂപ്പ് എറർ വരാതിരിക്കാൻ asyncio.run() ഉപയോഗിക്കുന്നു
    asyncio.run(main())
