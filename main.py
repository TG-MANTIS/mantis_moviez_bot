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
    # ബോട്ട് സ്റ്റാർട്ട് ചെയ്യുന്നു
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
    # എറർ വരാത്ത രീതിയിൽ asyncio.run() ഉപയോഗിച്ച് ലൂപ്പ് സ്റ്റാർട്ട് ചെയ്യുന്നു
    asyncio.run(main())
