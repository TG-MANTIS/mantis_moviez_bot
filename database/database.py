import motor.motor_asyncio
from config import DATABASE_URL, DATABASE_NAME, COLLECTION_NAME

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self._db = self._client[database_name]
        self._col = self._db[COLLECTION_NAME]

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
        # കൂടുതൽ ലാംഗ്വേജുകൾ ഇവിടെ ചേർത്തിരിക്കുന്നു
        langs = ["Malayalam", "Tamil", "Telugu", "Kannada", "Hindi", "English", "Korean", "Japanese", "Chinese", "Dual Audio", "Multi Audio"]
        found_langs = []
        for l in langs:
            if l.lower() in text.lower():
                found_langs.append(l)
        return found_langs[0] if found_langs else "Unknown"

    async def search_files(self, query):
        filter_query = {"file_name": {'$regex': query, '$options': 'i'}}
        cursor = self._col.find(filter_query)
        files = await cursor.to_list(length=20)
        return files

    async def filter_files(self, query, lang=None, qual=None):
        filter_query = {"file_name": {'$regex': query, '$options': 'i'}}
        if lang:
            filter_query["language"] = {'$regex': lang, '$options': 'i'}
        if qual:
            filter_query["quality"] = {'$regex': qual, '$options': 'i'}
            
        cursor = self._col.find(filter_query)
        files = await cursor.to_list(length=10)
        return files

db = Database(DATABASE_URL, DATABASE_NAME)
