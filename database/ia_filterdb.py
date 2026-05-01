import re
import base64
import logging
from struct import pack
from pyrogram.file_id import FileId
from pymongo import MongoClient, TEXT
from pymongo.errors import DuplicateKeyError, OperationFailure
from info import USE_CAPTION_FILTER, FILES_DATABASE_URL, SECOND_FILES_DATABASE_URL, DATABASE_NAME, COLLECTION_NAME, MAX_BTN, LANGUAGES, QUALITY

logger = logging.getLogger(__name__)

client = MongoClient(FILES_DATABASE_URL)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

try:
    collection.create_index([("file_name", TEXT)])
except OperationFailure as e:
    if 'quota' in str(e).lower():
        if not SECOND_FILES_DATABASE_URL:
            logger.error(f'your FILES_DATABASE_URL is already full, add SECOND_FILES_DATABASE_URL')
        else:
            logger.info('FILES_DATABASE_URL is full, now using SECOND_FILES_DATABASE_URL')
    else:
        logger.exception(e)

if SECOND_FILES_DATABASE_URL:
    second_client = MongoClient(SECOND_FILES_DATABASE_URL)
    second_db = second_client[DATABASE_NAME]
    second_collection = second_db[COLLECTION_NAME]
    second_collection.create_index([("file_name", TEXT)])


def second_db_count_documents():
     return second_collection.count_documents({})

def db_count_documents():
     return collection.count_documents({})


async def save_file(media):
    """Save file in database with Ultra-Smart Tagging"""
    file_id = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.file_name))
    file_caption = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.caption))
    text_to_scan = f"{file_name} {file_caption}".lower()

    # 1. Extract Languages & Qualities (Exact word match using regex boundary \b)
    file_langs = [lang for lang in LANGUAGES if re.search(rf"\b{lang}\b", text_to_scan)]
    file_quals = [qual for qual in QUALITY if re.search(rf"\b{qual}\b", text_to_scan)]

    # 2. Extract Year (1900 to 2099)
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', text_to_scan)
    file_year = year_match.group(1) if year_match else None

    # 3. Extract Season (e.g., S01, S1, Season 1)
    season_match = re.search(r'\b(?:s|season\s*)([0-9]{1,2})\b', text_to_scan)
    file_season = f"S{int(season_match.group(1)):02d}" if season_match else None
    
    document = {
        '_id': file_id,
        'file_name': file_name,
        'file_size': media.file_size,
        'caption': file_caption,
        'languages': file_langs,   # e.g., ['hindi', 'dual']
        'qualities': file_quals,   # e.g., ['1080p']
        'year': file_year,         # e.g., '2025'
        'season': file_season      # e.g., 'S01'
    }
    
    try:
        collection.insert_one(document)
        logger.info(f"Saved: {file_name} | Tags: {file_langs} | Qual: {file_quals} | YR: {file_year} | S: {file_season}")
        return 'suc'
    except DuplicateKeyError:
        logger.warning(f'Already Saved - {file_name}')
        return 'dup'
    except OperationFailure:
        if SECOND_FILES_DATABASE_URL:
            try:
                second_collection.insert_one(document)
                logger.info(f'Saved to 2nd db - {file_name}')
                return 'suc'
            except DuplicateKeyError:
                logger.warning(f'Already Saved in 2nd db - {file_name}')
                return 'dup'
        else:
            logger.error(f'your FILES_DATABASE_URL is already full, add SECOND_FILES_DATABASE_URL')
            return 'err'

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

    cursor = collection.find(filter_obj).sort('_id', -1)
    results = [doc for doc in cursor]

    if SECOND_FILES_DATABASE_URL:
        cursor2 = second_collection.find(filter_obj).sort('_id', -1)
        results.extend([doc for doc in cursor2])

    total_results = len(results)
    files = results[offset:][:max_results]
    
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

    langs = collection.distinct("languages", filter_obj)
    quals = collection.distinct("qualities", filter_obj)
    years = collection.distinct("year", filter_obj)
    seasons = collection.distinct("season", filter_obj)

    if SECOND_FILES_DATABASE_URL:
        langs.extend(second_collection.distinct("languages", filter_obj))
        quals.extend(second_collection.distinct("qualities", filter_obj))
        years.extend(second_collection.distinct("year", filter_obj))
        seasons.extend(second_collection.distinct("season", filter_obj))

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
        
    filter = {'file_name': regex}
    
    result1 = collection.delete_many(filter)
    
    result2 = None
    if SECOND_FILES_DATABASE_URL:
        result2 = second_collection.delete_many(filter)
    
    total_deleted = result1.deleted_count
    if result2:
        total_deleted += result2.deleted_count
    
    return total_deleted

async def delete_all_files():
    res1 = collection.delete_many({})
    total_deleted = res1.deleted_count
    if SECOND_FILES_DATABASE_URL:
        res2 = second_collection.delete_many({})
        total_deleted += res2.deleted_count
    return total_deleted

async def get_file_details(query):
    file_details = collection.find_one({'_id': query})
    if not file_details and SECOND_FILES_DATABASE_URL:
        file_details = second_collection.find_one({'_id': query})
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