import time
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from info import (
    BOT_ID, ADMINS, DATABASE_NAME, DATA_DATABASE_URL, FILES_DATABASE_URL, 
    SECOND_FILES_DATABASE_URL, IMDB_TEMPLATE, WELCOME_TEXT, LINK_MODE, 
    TUTORIAL, SHORTLINK_URL, SHORTLINK_API, SHORTLINK, FILE_CAPTION, 
    IMDB, WELCOME, SPELL_CHECK, PROTECT_CONTENT, AUTO_DELETE, IS_STREAM, VERIFY_EXPIRE
)

files_db_client = AsyncIOMotorClient(FILES_DATABASE_URL)
files_db = files_db_client[DATABASE_NAME]

data_db_client = AsyncIOMotorClient(DATA_DATABASE_URL)
data_db = data_db_client[DATABASE_NAME]

if SECOND_FILES_DATABASE_URL:
    second_files_db_client = AsyncIOMotorClient(SECOND_FILES_DATABASE_URL)
    second_files_db = second_files_db_client[DATABASE_NAME]

class Database:
    default_setgs = {
        'file_secure': PROTECT_CONTENT,
        'imdb': IMDB,
        'spell_check': SPELL_CHECK,
        'auto_delete': AUTO_DELETE,
        'welcome': WELCOME,
        'welcome_text': WELCOME_TEXT,
        'template': IMDB_TEMPLATE,
        'caption': FILE_CAPTION,
        'url': SHORTLINK_URL,
        'api': SHORTLINK_API,
        'shortlink': SHORTLINK,
        'tutorial': TUTORIAL,
        'links': LINK_MODE
    }

    default_verify = {
        'is_verified': False,
        'verified_time': 0,
        'verify_token': "",
        'link': "",
        'expire_time': 0
    }
    
    default_prm = {
        'expire': '',
        'trial': False,
        'plan': '',
        'premium': False
    }

    def __init__(self):
        self.col = data_db.Users
        self.grp = data_db.Groups
        self.prm = data_db.Premiums
        self.req = data_db.Requests
        self.con = data_db.Connections
        self.stg = data_db.Settings
        self.sudo = data_db.Sudoers
        self.movies = files_db.Files

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
            verify_status=self.default_verify
        )

    def new_group(self, id, title):
        return dict(
            id = id,
            title = title,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
            settings=self.default_setgs
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        return await self.col.count_documents({})
    
    async def remove_ban(self, id):
        ban_status = dict(is_banned=False, ban_reason='')
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(is_banned=True, ban_reason=ban_reason)
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(is_banned=False, ban_reason='')
        user = await self.col.find_one({'id':int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        return await self.col.find({}).to_list(length=None)
    
    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def delete_chat(self, grp_id):
        await self.grp.delete_many({'id': int(grp_id)})

    # --- SUDO MANAGEMENT (FIXED ASYNC) ---
    async def add_sudo(self, user_id):
        if not await self.sudo.find_one({'id': int(user_id)}):
            await self.sudo.insert_one({'id': int(user_id), 'added_at': datetime.now()})
            return True
        return False

    async def remove_sudo(self, user_id):
        res = await self.sudo.delete_one({'id': int(user_id)})
        return res.deleted_count > 0

    async def get_sudo_list(self):
        cursor = await self.sudo.find({}).to_list(length=None)
        return [user['id'] for user in cursor]

    async def is_sudo(self, user_id):
        if user_id in ADMINS:
            return True
        user = await self.sudo.find_one({'id': int(user_id)})
        return bool(user)

    # --- MISC LOGIC (FIXED ASYNC) ---
    async def find_join_req(self, id):
        user = await self.req.find_one({'id': id})
        return bool(user)

    async def add_join_req(self, id):
        await self.req.insert_one({'id': id})

    async def del_join_req(self):
        await self.req.drop()

    async def get_banned(self):
        users = await self.col.find({'ban_status.is_banned': True}).to_list(length=None)
        chats = await self.grp.find({'chat_status.is_disabled': True}).to_list(length=None)
        b_chats = [chat['id'] for chat in chats]
        b_users = [user['id'] for user in users]
        return b_users, b_chats
    
    async def add_chat(self, chat, title):
        chat_data = self.new_group(chat, title)
        await self.grp.insert_one(chat_data)

    async def get_chat(self, chat):
        chat_data = await self.grp.find_one({'id':int(chat)})
        return False if not chat_data else chat_data.get('chat_status')
    
    async def re_enable_chat(self, id):
        chat_status=dict(is_disabled=False, reason="")
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})
        
    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})      
    
    async def get_settings(self, id):
        chat = await self.grp.find_one({'id':int(id)})
        if chat:
            return chat.get('settings', self.default_setgs)
        return self.default_setgs
    
    async def disable_chat(self, chat, reason="No Reason"):
        chat_status=dict(is_disabled=True, reason=reason)
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})
    
    async def get_verify_status(self, user_id):
        user = await self.col.find_one({'id':int(user_id)})
        if user:
            info = user.get('verify_status', self.default_verify)
            if 'expire_time' not in info:
                verified_time = info.get('verified_time', 0)
                expire_time = verified_time + VERIFY_EXPIRE
                info['expire_time'] = expire_time
            return info
        return self.default_verify
        
    async def update_verify_status(self, user_id, verify):
        await self.col.update_one({'id': int(user_id)}, {'$set': {'verify_status': verify}})
    
    async def total_chat_count(self):
        return await self.grp.count_documents({})
    
    async def get_all_chats(self):
        return await self.grp.find({}).to_list(length=None)
    
    async def get_files_db_size(self):
        res = await files_db.command("dbstats")
        return res['dataSize']
   
    async def get_second_files_db_size(self):
        if SECOND_FILES_DATABASE_URL:
            res = await second_files_db.command("dbstats")
            return res['dataSize']
        return 0
    
    async def get_data_db_size(self):
        res = await data_db.command("dbstats")
        return res['dataSize']
    
    async def get_all_chats_count(self):
        return await self.grp.count_documents({})

    async def get_all_movie_titles(self):
        cursor = self.movies.find({}, {"title": 1, "file_name": 1})
        titles = []
        async for t in cursor:
            title = t.get('title') or t.get('file_name')
            if title:
                titles.append(title)
        return list(set(titles))

    async def get_plan(self, id):
        st = await self.prm.find_one({'id': id})
        if st:
            return st['status']
        return self.default_prm
    
    async def update_plan(self, id, data):
        await self.prm.update_one({'id': id}, {'$set': {'status': data}}, upsert=True)

    async def has_premium_access(self, user_id):
        user_data = await self.prm.find_one({'id': user_id})
        if user_data and user_data.get('status'):
            expiry_time = user_data['status'].get("expire")
            if not expiry_time:
                return False
            if isinstance(expiry_time, datetime) and datetime.now() <= expiry_time:
                return True
            else:
                user_data['status']['premium'] = False
                user_data['status']['expire'] = ""
                await self.update_plan(user_id, user_data['status'])
        return False
    
    async def check_remaining_usage(self, user_id):
        user_data = await self.prm.find_one({'id': user_id})
        if user_data and user_data.get('status'):
            expiry_time = user_data['status'].get("expire")
            if isinstance(expiry_time, datetime):
                return expiry_time - datetime.now()
        return timedelta(seconds=0)
    
    async def get_free_trial_status(self, user_id):
        user_data = await self.prm.find_one({'id': user_id})
        if user_data and user_data.get('status'):
            return user_data['status'].get("trial", False)
        return False

    async def give_free_trail(self, user_id):        
        seconds = 5 * 60         
        expiry_time = datetime.now() + timedelta(seconds=seconds)
        status = {
            'expire': expiry_time,
            'plan': '5 Mins Trial',
            'premium': True,
            'trial': True
        }
        await self.update_plan(user_id, status)

    async def get_premium_count(self):
        return await self.prm.count_documents({'status.premium': True})
    
    async def get_premium_users(self):
        return await self.prm.find({}).to_list(length=None)
    
    async def add_connect(self, group_id, user_id):
        user = await self.con.find_one({'_id': user_id})
        if user:
            if group_id not in user["group_ids"]:
                await self.con.update_one({'_id': user_id}, {"$push": {"group_ids": group_id}})
        else:
            await self.con.insert_one({'_id': user_id, 'group_ids': [group_id]})

    async def get_connections(self, user_id):
        user = await self.con.find_one({'_id': user_id})
        if user:
            return user["group_ids"]
        return []
        
    async def update_bot_sttgs(self, var, val):
        if not await self.stg.find_one({'id': BOT_ID}):
            await self.stg.insert_one({'id': BOT_ID, var: val})
        await self.stg.update_one({'id': BOT_ID}, {'$set': {var: val}})

    async def get_bot_sttgs(self):
        return await self.stg.find_one({'id': BOT_ID})
    
    async def reset_all_groups_settings(self):
        result = await self.grp.update_many({}, {'$set': {'settings': self.default_setgs}})
        return result.modified_count

    async def add_shortener(self, site, api, weight=50):
        """Adds a shortener with a custom traffic weight (default 50)"""
        return await self.stg.update_one(
            {'id': BOT_ID},
            {'$push': {'shortener_list': {
                'site': site, 
                'api': api, 
                'weight': int(weight), 
                'total_clicks': 0
            }}},
            upsert=True
        )

    async def remove_shortener(self, site):
        return await self.stg.update_one(
            {'id': BOT_ID},
            {'$pull': {'shortener_list': {'site': site}}}
        )

    async def get_all_shorteners(self):
        data = await self.stg.find_one({'id': BOT_ID})
        return data.get('shortener_list', []) if data else []

    async def update_sh_clicks(self, site):
        today = datetime.now().strftime("%Y-%m-%d")
        await self.stg.update_one(
            {'id': BOT_ID, 'shortener_list.site': site},
            {
                '$inc': {
                    'shortener_list.$.total_clicks': 1,
                    f'shortener_list.$.clicks_{today}': 1
                }
            }
        )

db = Database()