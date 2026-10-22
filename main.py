from pyrogram import Client

API_ID = "API_ID" 
API_HASH = "API_HASH"
BOT_TOKEN = "BOT_TOKEN"

app = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

if __name__ == "__main__":
    app.run()


