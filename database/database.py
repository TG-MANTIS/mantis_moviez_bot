import motor.motor_asyncio
from config import DATABASE_URL, DATABASE_NAME, COLLECTION_NAME

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self._db = self._client[database_name]
        self._col = self._db[COLLECTION_NAME]
        self._settings = self._db["bot_settings"]
        self._users = self._db["bot_users"]
        self._groups = self._db["bot_groups"]
        self._manual_filters = self._db["manual_filters"] # മാനുവൽ ഫിൽട്ടറിന് വേണ്ടി

    async def save_file(self, file_id, file_name, file_size):
        quality = self.extract_quality(file_name)
        language = self.extract_language(file_name)

        file_data = {
            "file_id": file_id,
            "file_name": file_name,
            "file_size": file_size,
            "quality": quality,
            "language": language
        }
        await self._col.insert_one(file_data)

    def extract_quality(self, text):
        qualities = ["480p", "720p", "1080p", "2160p", "4K", "HDR"]
        for q in qualities:
            if q.lower() in text.lower():
                return q
        return "Unknown"

    def extract_language(self, text):
        langs = ["Malayalam", "Tamil", "Telugu", "Kannada", "Hindi", "English", "Korean", "Japanese", "Chinese", "Dual Audio", "Multi Audio"]
        found_langs = []
        for l in langs:
            if l.lower() in text.lower():
                found_langs.append(l)
        return found_langs[0] if found_langs else "Unknown"

    async def search_files(self, query):
        filter_query = {"file_name": {'$regex': query, '$options': 'i'}}
        cursor = self._col.find(filter_query)
        files = await cursor.to_list(length=100)
        return files

    async def filter_files(self, query, lang=None, qual=None):
        filter_query = {"file_name": {'$regex': query, '$options': 'i'}}
        if lang:
            filter_query["language"] = {'$regex': lang, '$options': 'i'}
        if qual:
            filter_query["quality"] = {'$regex': qual, '$options': 'i'}
            
        cursor = self._col.find(filter_query)
        files = await cursor.to_list(length=100)
        return files

    async def get_settings(self, chat_id):
        default_settings = {
            "chat_id": chat_id,
            "welcome": True,
            "goodbye": True,
            "f_sub": True,
            "imdb": True,
            "auto_delete": 300,
            "max_btn": 8,
            "custom_photo": None,
            "caption": "<b>📁 File: {file_name}\n📦 Size: {file_size}\n\n🤖 Powered by Auto-Filter Bot</b>",
            "f_sub_channel": None
        }
        user = await self._settings.find_one({"chat_id": chat_id})
        if not user:
            await self._settings.insert_one(default_settings)
            return default_settings
        return user

    async def update_setting(self, chat_id, key, value):
        await self._settings.update_one({"chat_id": chat_id}, {"$set": {key: value}}, upsert=True)

    async def add_user(self, user_id):
        if not await self._users.find_one({"user_id": user_id}):
            await self._users.insert_one({"user_id": user_id})

    async def add_group(self, chat_id):
        if not await self._groups.find_one({"chat_id": chat_id}):
            await self._groups.insert_one({"chat_id": chat_id})

    async def get_all_users(self):
        return self._users.find({})

    async def get_all_groups(self):
        return self._groups.find({})

    # --- Manual Filter Functions ---
    async def save_manual_filter(self, chat_id, keyword, reply_text):
        await self._manual_filters.update_one(
            {"chat_id": chat_id, "keyword": keyword.lower()},
            {"$set": {"reply_text": reply_text}},
            upsert=True
        )

    async def get_manual_filter(self, chat_id, keyword):
        return await self._manual_filters.find_one({"chat_id": chat_id, "keyword": keyword.lower()})

    async def delete_manual_filter(self, chat_id, keyword):
        result = await self._manual_filters.delete_one({"chat_id": chat_id, "keyword": keyword.lower()})
        return result.deleted_count > 0

db = Database(DATABASE_URL, DATABASE_NAME)
