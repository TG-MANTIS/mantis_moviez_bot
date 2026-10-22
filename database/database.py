import motor.motor_asyncio
from config import DATABASE_URL, DATABASE_NAME, COLLECTION_NAME

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self._db = self._client[database_name]
        self._col = self._db[COLLECTION_NAME]

    async def save_file(self, file_id, file_name, file_size):
        file_data = {
            "file_id": file_id,
            "file_name": file_name,
            "file_size": file_size
        }
        await self._col.insert_one(file_data)

db = Database(DATABASE_URL, DATABASE_NAME)
