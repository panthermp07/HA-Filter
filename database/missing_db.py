from motor.motor_asyncio import AsyncIOMotorClient
from info import SECOND_FILES_DATABASE_URL, DATABASE_NAME

client = AsyncIOMotorClient(SECOND_FILES_DATABASE_URL)
db = client[DATABASE_NAME]
missing_col = db['missing_files']

async def add_missing(query):
    await missing_col.update_one({'query': query.lower()}, {'$set': {'query': query.lower()}}, upsert=True)

async def get_all_missing():
    cursor = missing_col.find({})
    return [doc['query'] async for doc in cursor]

async def clear_missing():
    await missing_col.delete_many({})
