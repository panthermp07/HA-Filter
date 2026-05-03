import re
import base64
import logging
from struct import pack
from pyrogram.file_id import FileId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import TEXT, ASCENDING
from pymongo.errors import DuplicateKeyError, OperationFailure
import PTN
import asyncio

from info import USE_CAPTION_FILTER, FILES_DATABASE_URL, SECOND_FILES_DATABASE_URL, DATABASE_NAME, COLLECTION_NAME, MAX_BTN, LANGUAGES, QUALITY
from database.users_chats_db import data_db
from utils import send_update

logger = logging.getLogger(__name__)

client = AsyncIOMotorClient(FILES_DATABASE_URL)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

second_client = None
second_db = None
second_collection = None

if SECOND_FILES_DATABASE_URL:
    second_client = AsyncIOMotorClient(SECOND_FILES_DATABASE_URL)
    second_db = second_client[DATABASE_NAME]
    second_collection = second_db[COLLECTION_NAME]

updates_collection = data_db['notified_media']

async def setup_database():
    try:
        await updates_collection.create_index(
            [("title", ASCENDING), ("year", ASCENDING)],
            unique=True,
            name="title_year_unique"
        )
        logger.info("Updates collection indexes created/verified.")
    except OperationFailure as e:
        if e.code == 85:  # IndexOptionsConflict
            logger.warning("Updates collection index conflict. Recreating...")
            await updates_collection.drop_indexes() 
            await updates_collection.create_index(
                [("title", ASCENDING), ("year", ASCENDING)],
                unique=True,
                name="title_year_unique"
            )
            logger.info("Updates collection indexes recreated successfully.")
        else:
            logger.exception(e)
            exit()

    try:
        # Creating index for both file_name and caption
        await collection.create_index([("file_name", TEXT), ("caption", TEXT)], name="file_name_caption_text")
        logger.info("Primary Files DB indexes created/verified.")
    except OperationFailure as e:
        if e.code == 85:
            logger.warning("Primary DB index conflict. Recreating...")
            await collection.drop_indexes() 
            await collection.create_index([("file_name", TEXT), ("caption", TEXT)], name="file_name_caption_text")
        elif 'quota' in str(e).lower():
            if not SECOND_FILES_DATABASE_URL:
                logger.error('Your FILES_DATABASE_URL quota is full, add SECOND_FILES_DATABASE_URL.')
            else:
                logger.info('FILES_DATABASE_URL quota is full, relying on SECOND_FILES_DATABASE_URL')
        else:
            logger.exception(e)

    if SECOND_FILES_DATABASE_URL and second_collection is not None:
        try:
            await second_collection.create_index([("file_name", TEXT), ("caption", TEXT)], name="file_name_caption_text")
            logger.info("Secondary Files DB indexes created/verified.")
        except OperationFailure as e:
            if e.code == 85:
                await second_collection.drop_indexes()
                await second_collection.create_index([("file_name", TEXT), ("caption", TEXT)], name="file_name_caption_text")


async def second_db_count_documents():
    if second_collection is None:
        return 0
    return await second_collection.count_documents({})

async def db_count_documents():
    return await collection.count_documents({})

async def trigger_update_if_new(title, year):
    if not title:
        return
    normalized_title = str(title).strip().lower()
    try:
        await updates_collection.insert_one({
            "title": normalized_title, 
            "year": year
        })
        asyncio.create_task(send_update(title, year))
    except DuplicateKeyError:
        pass # Already notified

async def save_file(media):
    """Save file in database with Ultra-Smart Tagging + Auto-Notify"""
    file_id = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.file_name))
    file_caption = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.caption))
    text_to_scan = f"{file_name} {file_caption}".lower()

    # 1. Extract Languages & Qualities (Your Elite Regex Logic)
    file_langs = [lang for lang in LANGUAGES if re.search(rf"\b{lang}\b", text_to_scan)]
    file_quals = [qual for qual in QUALITY if re.search(rf"\b{qual}\b", text_to_scan)]

    # 2. Extract Year & Season
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', text_to_scan)
    file_year = year_match.group(1) if year_match else None

    season_match = re.search(r'\b(?:s|season\s*)([0-9]{1,2})\b', text_to_scan)
    file_season = f"S{int(season_match.group(1)):02d}" if season_match else None
    
    document = {
        '_id': file_id,
        'file_name': file_name,
        'file_size': media.file_size,
        'caption': file_caption,
        'languages': file_langs,
        'qualities': file_quals,
        'year': file_year,
        'season': file_season
    }
    
    # Extract Title for Auto-Updater using PTN
    data = PTN.parse(file_name)
    title = data.get('title')
    ptn_year = data.get('year')
    
    try:
        await collection.insert_one(document)
        logger.info(f"Saved: {file_name} | Tags: {file_langs} | Qual: {file_quals} | S: {file_season}")
        await trigger_update_if_new(title, ptn_year)
        return 'suc'
    except DuplicateKeyError:
        logger.warning(f'Already Saved - {file_name}')
        return 'dup'
    except OperationFailure:
        if SECOND_FILES_DATABASE_URL and second_collection is not None:
            try:
                await second_collection.insert_one(document)
                logger.info(f'Saved to 2nd db - {file_name}')
                await trigger_update_if_new(title, ptn_year)
                return 'suc'
            except DuplicateKeyError:
                logger.warning(f'Already Saved in 2nd db - {file_name}')
                return 'dup'
        else:
            logger.error(f'Your FILES_DATABASE_URL is already full, add SECOND_FILES_DATABASE_URL')
            return 'err'

# 🚀 Your Advanced Tag-Based Search Function (Upgraded to Motor Async)
async def get_search_results(query, max_results=MAX_BTN, offset=0, req_lang=None, req_qual=None, req_year=None, req_season=None):
    query = str(query).strip()
    filter_obj = {}

    if query:
        if ' ' not in query:
            raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
        else:
            raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
        
        try:
            regex = re.compile(raw_pattern, flags=re.IGNORECASE)
        except:
            regex = query

        if USE_CAPTION_FILTER:
            filter_obj = {'$or': [{'file_name': regex}, {'caption': regex}]}
        else:
            filter_obj = {'file_name': regex}

    and_filters = []
    
    if req_lang:
        and_filters.append({'$or': [{'languages': req_lang}, {'file_name': re.compile(rf"\b{req_lang}\b", re.IGNORECASE)}]})
    if req_qual:
        and_filters.append({'$or': [{'qualities': req_qual}, {'file_name': re.compile(rf"\b{req_qual}\b", re.IGNORECASE)}]})
    if req_year:
        and_filters.append({'$or': [{'year': req_year}, {'file_name': re.compile(rf"\b{req_year}\b", re.IGNORECASE)}]})
    if req_season:
        season_num = int(req_season[1:]) 
        and_filters.append({'$or': [{'season': req_season}, {'file_name': re.compile(rf"\b(?:s|season\s*)0?{season_num}\b", re.IGNORECASE)}]})

    if and_filters:
        if filter_obj:
            filter_obj = {'$and': [filter_obj] + and_filters}
        else:
            filter_obj = {'$and': and_filters}

    total1 = await collection.count_documents(filter_obj)
    total_results = total1
    
    if SECOND_FILES_DATABASE_URL and second_collection is not None:
        total2 = await second_collection.count_documents(filter_obj)
        total_results += total2

    files = []
    if offset < total1:
        cursor = collection.find(filter_obj).sort('_id', -1).skip(offset).limit(max_results)
        files = await cursor.to_list(length=max_results)
        if len(files) < max_results and SECOND_FILES_DATABASE_URL and second_collection is not None:
            rem = max_results - len(files)
            cursor2 = second_collection.find(filter_obj).sort('_id', -1).limit(rem)
            files.extend(await cursor2.to_list(length=rem))
    else:
        if SECOND_FILES_DATABASE_URL and second_collection is not None:
            skip_second = offset - total1
            cursor2 = second_collection.find(filter_obj).sort('_id', -1).skip(skip_second).limit(max_results)
            files = await cursor2.to_list(length=max_results)

    next_offset = offset + max_results
    if next_offset >= total_results:
        next_offset = '' 
          
    return files, next_offset, total_results

async def get_available_tags(query, req_lang=None, req_qual=None, req_year=None, req_season=None):
    """Fetch ONLY the available tags for the EXACT current filter combination!"""
    query = str(query).strip()
    filter_obj = {}

    if query:
        if ' ' not in query:
            raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
        else:
            raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
        try:
            regex = re.compile(raw_pattern, flags=re.IGNORECASE)
        except:
            regex = query

        if USE_CAPTION_FILTER:
            filter_obj = {'$or': [{'file_name': regex}, {'caption': regex}]}
        else:
            filter_obj = {'file_name': regex}

    and_filters = []
    if req_lang:
        and_filters.append({'$or': [{'languages': req_lang}, {'file_name': re.compile(rf"\b{req_lang}\b", re.IGNORECASE)}]})
    if req_qual:
        and_filters.append({'$or': [{'qualities': req_qual}, {'file_name': re.compile(rf"\b{req_qual}\b", re.IGNORECASE)}]})
    if req_year:
        and_filters.append({'$or': [{'year': req_year}, {'file_name': re.compile(rf"\b{req_year}\b", re.IGNORECASE)}]})
    if req_season:
        season_num = int(req_season[1:]) 
        and_filters.append({'$or': [{'season': req_season}, {'file_name': re.compile(rf"\b(?:s|season\s*)0?{season_num}\b", re.IGNORECASE)}]})

    if and_filters:
        if filter_obj:
            filter_obj = {'$and': [filter_obj] + and_filters}
        else:
            filter_obj = {'$and': and_filters}

    langs = await collection.distinct("languages", filter_obj)
    quals = await collection.distinct("qualities", filter_obj)
    years = await collection.distinct("year", filter_obj)
    seasons = await collection.distinct("season", filter_obj)

    if SECOND_FILES_DATABASE_URL and second_collection is not None:
        langs.extend(await second_collection.distinct("languages", filter_obj))
        quals.extend(await second_collection.distinct("qualities", filter_obj))
        years.extend(await second_collection.distinct("year", filter_obj))
        seasons.extend(await second_collection.distinct("season", filter_obj))

    return {
        'languages': list(set([x for x in langs if x])),
        'qualities': list(set([x for x in quals if x])),
        'years': list(set([x for x in years if x])),
        'seasons': list(set([x for x in seasons if x]))
    }

async def delete_files(query):
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        regex = query
        
    filter_obj = {'file_name': regex}
    
    result1 = await collection.delete_many(filter_obj)
    total_deleted = result1.deleted_count
    
    if SECOND_FILES_DATABASE_URL and second_collection is not None:
        result2 = await second_collection.delete_many(filter_obj)
        total_deleted += result2.deleted_count
    
    return total_deleted

async def delete_all_files():
    res1 = await collection.delete_many({})
    total_deleted = res1.deleted_count
    if SECOND_FILES_DATABASE_URL and second_collection is not None:
        res2 = await second_collection.delete_many({})
        total_deleted += res2.deleted_count
    return total_deleted

async def get_file_details(query):
    file_details = await collection.find_one({'_id': query})
    if not file_details and SECOND_FILES_DATABASE_URL and second_collection is not None:
        file_details = await second_collection.find_one({'_id': query})
    return file_details

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    return file_id