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

second_files_db = None
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
        'links': LINK_MODE,
        'fsub': "",
        'req_fsub': ""
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

    # ================= SUDO SYSTEM =================
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

    # ================= JOIN REQUESTS =================
    async def find_join_req(self, id):
        user = await self.req.find_one({'id': id})
        return bool(user)

    async def add_join_req(self, id):
        await self.req.insert_one({'id': id})

    async def del_join_req(self):
        await self.req.drop()

    # ================= BAN & GROUPS =================
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
        chat_status = dict(is_disabled=False, reason="")
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})
        
    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})      
    
    async def get_settings(self, id):
        chat = await self.grp.find_one({'id':int(id)})
        if chat:
            return chat.get('settings', self.default_setgs)
        return self.default_setgs
    
    async def disable_chat(self, chat, reason="No Reason"):
        chat_status = dict(is_disabled=True, reason=reason)
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
    
    # ================= DATABASE STATS =================
    async def get_files_db_size(self):
        res = await files_db.command("dbstats")
        return res['dataSize']
   
    async def get_second_files_db_size(self):
        if second_files_db is not None:
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

    # ================= PREMIUM SYSTEM =================
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
    
    # ================= PM CONNECTIONS =================
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
        
    # ================= BOT SETTINGS & SHORTENERS =================
    async def update_bot_sttgs(self, var, val):
        if not await self.stg.find_one({'id': BOT_ID}):
            await self.stg.insert_one({'id': BOT_ID, var: val})
        else:
            await self.stg.update_one({'id': BOT_ID}, {'$set': {var: val}})

    async def get_bot_sttgs(self):
        stg = await self.stg.find_one({'id': BOT_ID})
        return stg if stg else {}
    
    async def reset_all_groups_settings(self):
        result = await self.grp.update_many({}, {'$set': {'settings': self.default_setgs}})
        return result.modified_count

    async def add_shortener(self, site, api, weight=50):
        """Smart Auto-Scaling: Balances weights so total is always 100%"""
        weight = max(0, min(100, int(weight))) # Ensure weight is between 0-100
        data = await self.stg.find_one({'id': BOT_ID})
        shortener_list = data.get('shortener_list', []) if data else []

        existing_item = None
        other_shorteners = []
        for sh in shortener_list:
            if sh['site'] == site:
                existing_item = sh
            else:
                other_shorteners.append(sh)

        if existing_item:
            existing_item['api'] = api
            new_item = existing_item
        else:
            new_item = {'site': site, 'api': api, 'total_clicks': 0}

        new_item['weight'] = weight
        remaining_weight = 100 - weight

        if remaining_weight <= 0:
            # Agar naye ko 100% diya, toh baaki sab 0% ho jayenge
            for sh in other_shorteners:
                sh['weight'] = 0
        elif other_shorteners:
            total_other = sum(sh.get('weight', 0) for sh in other_shorteners)
            if total_other == 0:
                # Agar purano ka weight 0 tha, toh bacha hua equally baant do
                per_sh = remaining_weight // len(other_shorteners)
                for sh in other_shorteners:
                    sh['weight'] = per_sh
                other_shorteners[0]['weight'] += remaining_weight % len(other_shorteners)
            else:
                # Proportional Auto-Scaling
                temp_total = 0
                for sh in other_shorteners:
                    sh['weight'] = int(round(sh.get('weight', 0) * (remaining_weight / total_other)))
                    temp_total += sh['weight']
                
                # Fix rounding missing precision
                diff = remaining_weight - temp_total
                if diff != 0:
                    highest_sh = max(other_shorteners, key=lambda x: x.get('weight', 0))
                    highest_sh['weight'] += diff

        final_list = other_shorteners + [new_item]
        
        return await self.stg.update_one(
            {'id': BOT_ID},
            {'$set': {'shortener_list': final_list}},
            upsert=True
        )

    async def remove_shortener(self, site):
        """Auto-balances remaining shorteners to 100% when one is deleted"""
        data = await self.stg.find_one({'id': BOT_ID})
        if not data or 'shortener_list' not in data:
            return False

        shortener_list = data['shortener_list']
        new_list = [sh for sh in shortener_list if sh['site'] != site]

        if not new_list:
            return await self.stg.update_one({'id': BOT_ID}, {'$set': {'shortener_list': []}})

        total_remaining = sum(sh.get('weight', 0) for sh in new_list)
        if total_remaining == 0:
            per_sh = 100 // len(new_list)
            for sh in new_list:
                sh['weight'] = per_sh
            new_list[0]['weight'] += 100 % len(new_list)
        else:
            temp_total = 0
            for sh in new_list:
                sh['weight'] = int(round(sh.get('weight', 0) * (100 / total_remaining)))
                temp_total += sh['weight']

            diff = 100 - temp_total
            if diff != 0:
                highest_sh = max(new_list, key=lambda x: x.get('weight', 0))
                highest_sh['weight'] += diff

        await self.stg.update_one({'id': BOT_ID}, {'$set': {'shortener_list': new_list}})
        return True

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

    # ================= REFERRAL SYSTEM =================
    async def add_referral(self, inviter_id):
        """Increments referral count and returns updated document."""
        return await self.col.find_one_and_update(
            {'id': int(inviter_id)},
            {'$inc': {'referral_count': 1}},
            return_document=True
        )

    async def get_referral_count(self, user_id):
        """Gets current referral count."""
        user = await self.col.find_one({'id': int(user_id)})
        return user.get('referral_count', 0) if user else 0

    async def get_repair_mode(self):
        stg = await self.stg.find_one({'id': BOT_ID})
        if not stg:
            return False
        return stg.get('REPAIR_MODE', False)

    async def set_repair_mode(self, value: bool):
        await self.update_bot_sttgs('REPAIR_MODE', value)
        
db = Database()