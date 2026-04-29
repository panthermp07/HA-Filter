import re
import pytz
import random
import aiohttp
import asyncio
import requests
import logging
from pyrogram import enums
from datetime import datetime
from shortzy import Shortzy
from database.users_chats_db import db
from pyrogram.types import InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, FloodWait
from info import LONG_IMDB_DESCRIPTION, ADMINS, IS_PREMIUM, TIME_ZONE, TMDB_API_KEY, SHORTLINK_URL, SHORTLINK_API

logger = logging.getLogger(__name__)

class temp(object):
    START_TIME = 0
    BANNED_USERS = []
    BANNED_CHATS = []
    ME = None
    CANCEL = False
    U_NAME = None
    B_NAME = None
    SETTINGS = {}
    VERIFICATIONS = {}
    FILES = {}
    USERS_CANCEL = False
    GROUPS_CANCEL = False
    BOT = None
    PREMIUM = {}

async def is_subscribed(bot, query):
    btn = []
    if await is_premium(query.from_user.id, bot):
        return btn
        
    stg = await db.get_bot_sttgs()
    if not stg:
        return btn
        
    if stg.get('FORCE_SUB_CHANNELS'):
        for id in stg.get('FORCE_SUB_CHANNELS').split(' '):
            try:
                chat = await bot.get_chat(int(id))
                await bot.get_chat_member(int(id), query.from_user.id)
            except UserNotParticipant:
                btn.append(
                    [InlineKeyboardButton(f'Join : {chat.title}', url=chat.invite_link)]
                )
            except Exception as e:
                logger.error(f"Normal FSub Error: {e}")

    if stg.get('REQUEST_FORCE_SUB_CHANNELS') and not await db.find_join_req(query.from_user.id):
        id = stg.get('REQUEST_FORCE_SUB_CHANNELS')
        try:
            chat = await bot.get_chat(int(id))
            await bot.get_chat_member(int(id), query.from_user.id)
        except UserNotParticipant:
            try:
                url = await bot.create_chat_invite_link(int(id), creates_join_request=True)
                btn.append(
                    [InlineKeyboardButton(f'Request : {chat.title}', url=url.invite_link)]
                )
            except Exception as e:
                logger.error(f"Invite Link Error: {e}")
                
    return btn

def upload_image(file_path):
    with open(file_path, 'rb') as f:
        files = {'files[]': f}
        response = requests.post("https://uguu.se/upload", files=files)

    if response.status_code == 200:
        try:
            data = response.json()
            return data['files'][0]['url'].replace('\\/', '/')
        except Exception as e:
            return None
    else:
        return None


def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    else:
        return ", ".join(str(i) for i in k)


async def get_poster(query, bulk=False, id=False, file=None):
    TMDB_BASE = "https://api.themoviedb.org/3"

    year = None
    title = query

    if not id:
        query = query.strip()

        year_match = re.findall(r"[1-2]\d{3}$", query)
        if year_match:
            year = year_match[0]
            title = query.replace(year, "").strip()

        elif file:
            file_year = re.findall(r"[1-2]\d{3}", file)
            if file_year:
                year = file_year[0]

        url = f"{TMDB_BASE}/search/multi"
        params = {
            "api_key": TMDB_API_KEY,
            "query": title
        }

        res = requests.get(url, params=params).json()

        results = [
            r for r in res.get("results", [])
            if r.get("media_type") in ["movie", "tv"]
        ]

        if not results:
            return None

        if year:
            filtered = []
            for r in results:
                release = r.get("release_date") or r.get("first_air_date")
                if release and release.startswith(str(year)):
                    filtered.append(r)

            if filtered:
                results = filtered

        if bulk:
            _bulk = []
            for r in results:
                _title = r.get("title") or r.get("name")
                if _title:
                    _bulk.append({
                        "title": _title,
                        "id": r["id"]
                        })
            return _bulk

        data = results[0]
        tmdb_id = data["id"]
        media_type = data["media_type"]

    else:
        tmdb_id = query

        movie_test = requests.get(
            f"{TMDB_BASE}/movie/{tmdb_id}",
            params={"api_key": TMDB_API_KEY}
        )

        if movie_test.status_code == 200:
            media_type = "movie"
            data = movie_test.json()
        else:
            media_type = "tv"
            data = requests.get(
                f"{TMDB_BASE}/tv/{tmdb_id}",
                params={"api_key": TMDB_API_KEY}
            ).json()

    if not id:
        data = requests.get(
            f"{TMDB_BASE}/{media_type}/{tmdb_id}",
            params={"api_key": TMDB_API_KEY}
        ).json()

    title = data.get("title") or data.get("name")

    poster = None
    if data.get("poster_path"):
        poster = f"https://image.tmdb.org/t/p/original{data['poster_path']}"

    release_date = data.get("release_date") or data.get("first_air_date")

    genres = list_to_str([g["name"] for g in data.get("genres", [])])

    runtime = None
    if media_type == "movie":
        runtime = data.get("runtime")
    else:
        runtime = list_to_str(data.get("episode_run_time"))

    plot = data.get("overview")

    rating = data.get("vote_average")
    votes = data.get("vote_count")
    languages = list_to_str([l["english_name"] for l in data.get("spoken_languages", [])])
    countries = list_to_str([c["name"] for c in data.get("production_countries", [])])

    return {
        "title": title,
        "tmdb_id": tmdb_id,
        "kind": media_type,
        "languages": languages,
        "countries": countries,
        "release_date": release_date,
        "year": release_date[:4] if release_date else None,
        "genres": genres,
        "runtime": runtime,
        "rating": rating,
        "votes": votes,
        "poster": poster,
        "plot": plot,
        "url": f"https://www.themoviedb.org/{media_type}/{tmdb_id}"
    }

async def is_check_admin(bot, chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except:
        return False

async def get_verify_status(user_id):
    verify = temp.VERIFICATIONS.get(user_id)
    if not verify:
        verify = await db.get_verify_status(user_id)
        temp.VERIFICATIONS[user_id] = verify
    return verify

async def update_verify_status(user_id, verify_token="", is_verified=False, link="", expire_time=0):
    current = await get_verify_status(user_id)
    current['verify_token'] = verify_token
    current['is_verified'] = is_verified
    current['link'] = link
    current['expire_time'] = expire_time
    temp.VERIFICATIONS[user_id] = current
    await db.update_verify_status(user_id, current)

    
async def is_premium(user_id, bot):
    if not IS_PREMIUM:
        return True
    if user_id in ADMINS:
        return True
    mp = await db.get_plan(user_id)
    if mp['premium']:
        if mp['expire'] < datetime.now():
            await bot.send_message(user_id, f"Your premium {mp['plan']} plan is expired in {mp['expire'].strftime('%Y.%m.%d %H:%M:%S')}, use /plan to activate new plan again")
            mp['expire'] = ''
            mp['plan'] = ''
            mp['premium'] = False
            await db.update_plan(user_id, mp)
            return False
        return True
    else:
        return False


async def check_premium(bot):
    while True:
        premium_users = await db.get_premium_users() 
        pr = [i for i in premium_users if i.get('status', {}).get('premium')]
        
        for p in pr:
            mp = p['status']
            if mp.get('expire') and isinstance(mp['expire'], datetime):
                if mp['expire'] < datetime.now():
                    try:
                        await bot.send_message(
                            p['id'],
                            f"<b>ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ {mp['plan']} ᴘʟᴀɴ ɪs ᴇxᴘɪʀᴇᴅ ɪɴ {mp['expire'].strftime('%Y.%m.%d %H:%M:%S')}, ᴜsᴇ /plan ᴛᴏ ᴀᴄᴛɪᴠᴀᴛᴇ ɴᴇᴡ ᴘʟᴀɴ ᴀɢᴀɪɴ!</b>"
                        )
                    except Exception:
                        pass
                    mp['expire'] = ''
                    mp['plan'] = ''
                    mp['premium'] = False
                    await db.update_plan(p['id'], mp)
        
        await asyncio.sleep(1200)


async def broadcast_messages(user_id, message, pin):
    try:
        m = await message.copy(chat_id=user_id)
        if pin:
            await m.pin(both_sides=True)
        return "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message, pin)
    except Exception as e:
        await db.delete_user(int(user_id))
        return "Error"

async def groups_broadcast_messages(chat_id, message, pin):
    try:
        k = await message.copy(chat_id=chat_id)
        if pin:
            try:
                await k.pin()
            except:
                pass
        return "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await groups_broadcast_messages(chat_id, message, pin)
    except Exception as e:
        await db.delete_chat(chat_id)
        return "Error"

async def get_settings(group_id):
    settings = temp.SETTINGS.get(group_id)
    if not settings:
        settings = await db.get_settings(group_id)
        temp.SETTINGS.update({group_id: settings})
    return settings
    
async def save_group_settings(group_id, key, value):
    current = await get_settings(group_id)
    current.update({key: value})
    temp.SETTINGS.update({group_id: current})
    await db.update_settings(group_id, current)

def get_size(size):
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])


#async def get_shortlink(url, api, link):
#    shortzy = Shortzy(api_key=api, base_site=url)
#    link = await shortzy.convert(link)
#    return link

async def get_shortlink(link, user_id, grp_id=None):
    """Elite Shortener: Fixed PM Bug & Enforced 100% Accurate Weighted (70-30) Logic"""
    logger.info(f"🔗 --- sʜᴏʀᴛʟɪɴᴋ ʀᴇǫᴜᴇsᴛ sᴛᴀʀᴛᴇᴅ | ᴜsᴇʀ: {user_id} | ɢʀᴏᴜᴘ: {grp_id} ---")
    
    retry_list = []
    is_custom_group = False
    
    if grp_id:
        settings = await get_settings(grp_id)
        if settings.get('url') and settings.get('api') and settings.get('url') != SHORTLINK_URL:
            logger.info(f"🎯 ᴄᴜsᴛᴏᴍ ɢʀᴏᴜᴘ sʜᴏʀᴛᴇɴᴇʀ ꜰᴏᴜɴᴅ: {settings['url']}")
            retry_list.append({'site': settings['url'], 'api': settings['api']})
            is_custom_group = True

    if not is_custom_group:
        all_sh = await db.get_all_shorteners()
        if all_sh:
            weights = [int(sh.get('weight', 50)) for sh in all_sh]
            selected_sh = random.choices(all_sh, weights=weights, k=1)[0]
            
            logger.info(f"⚖️ ᴡᴇɪɢʜᴛ sʏsᴛᴇᴍ ᴡɪɴɴᴇʀ: {selected_sh['site']} (Weight: {selected_sh.get('weight')}%)")
            retry_list.append(selected_sh)
    retry_list.append({'site': SHORTLINK_URL, 'api': SHORTLINK_API})
    
    final_queue = []
    seen = set()
    for sh in retry_list:
        if sh['site'] not in seen:
            final_queue.append(sh)
            seen.add(sh['site'])

    logger.info(f"📋 ꜰɪɴᴀʟ ǫᴜᴇᴜᴇ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ: {[s['site'] for s in final_queue]}")

    last_error = "No specific error captured."

    for shortener in final_queue:
        logger.info(f"🔄 ᴀᴛᴛᴇᴍᴘᴛɪɴɢ: {shortener['site']}")
        try:
            shortzy = Shortzy(api_key=shortener['api'], base_site=shortener['site'])
            short_url = await shortzy.convert(link)
            
            await db.update_sh_clicks(shortener['site'])
            if not hasattr(temp, 'VERIFY_LOGS'): 
                temp.VERIFY_LOGS = {}
            temp.VERIFY_LOGS[user_id] = shortener['site']
            
            logger.info(f"✅ sᴜᴄᴄᴇss: {shortener['site']}")
            return short_url
            
        except Exception as e:
            last_error = str(e)
            logger.warning(f"❌ ꜰᴀɪʟᴇᴅ {shortener['site']} | ᴇʀʀᴏʀ: {last_error}")
            continue 
            
    logger.error("🚨 ᴀʟʟ sʜᴏʀᴛᴇɴᴇʀs ꜰᴀɪʟᴇᴅ! ᴘʀᴏᴠɪᴅɪɴɢ ᴅɪʀᴇᴄᴛ ʟɪɴᴋ.")
    try:
        if hasattr(temp, 'BOT') and temp.BOT:
            alert_msg = (
                "<b>⚠️ ᴄʀɪᴛɪᴄᴀʟ ᴀʟᴇʀᴛ: sʜᴏʀᴛᴇɴᴇʀ ᴀᴘɪs ᴅᴏᴡɴ!</b>\n\n"
                "sᴀᴀʀᴇ sʜᴏʀᴛᴇɴᴇʀs ꜰᴀɪʟ ʜᴏ ɢᴀʏᴇ ʜᴀɪɴ ᴀᴜʀ ᴜsᴇʀ ᴋᴏ <b>ᴅɪʀᴇᴄᴛ ʟɪɴᴋ</b> ᴅɪʏᴀ ɢᴀʏᴀ ʜᴀɪ.\n\n"
                f"👤 <b>ᴜsᴇʀ ɪᴅ:</b> <code>{user_id}</code>\n"
                f"❌ <b>ᴇʀʀᴏʀ:</b>\n<code>{last_error}</code>"
            )
            for admin in ADMINS:
                await temp.BOT.send_message(chat_id=admin, text=alert_msg)
    except Exception as alert_e:
        logger.error(f"Failed to send admin alert: {alert_e}")
        pass
    return link

def get_readable_time(seconds):
    periods = [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name}'
    return result

def get_wish():
    time = datetime.now(pytz.timezone(TIME_ZONE))
    now = time.strftime("%H")
    if now < "12":
        status = "ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ 🌞"
    elif now < "18":
        status = "ɢᴏᴏᴅ ᴀꜰᴛᴇʀɴᴏᴏɴ 🌗"
    else:
        status = "ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ 🌘"
    return status
    
async def get_seconds(time_string):
    def extract_value_and_unit(ts):
        value = ""
        unit = ""
        index = 0
        while index < len(ts) and ts[index].isdigit():
            value += ts[index]
            index += 1
        unit = ts[index:]
        if value:
            value = int(value)
        return value, unit
    value, unit = extract_value_and_unit(time_string)
    if unit == 's':
        return value
    elif unit == 'min':
        return value * 60
    elif unit == 'hour':
        return value * 3600
    elif unit == 'day':
        return value * 86400
    elif unit == 'month':
        return value * 86400 * 30
    elif unit == 'year':
        return value * 86400 * 365
    else:
        return 0