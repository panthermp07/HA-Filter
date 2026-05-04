import asyncio
import re
import aiohttp
import json
from time import time as time_now
import math, os
import qrcode, random
from thefuzz import process
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
from datetime import datetime, timedelta
from info import IS_PREMIUM, PICS, TUTORIAL, SHORTLINK_API, SHORTLINK_URL, OWNER_USERNAME, RECEIPT_SEND_USERNAME, UPI_ID, UPI_NAME, PRE_DAY_AMOUNT, SECOND_FILES_DATABASE_URL, ADMINS, URL, MAX_BTN, BIN_CHANNEL, IS_STREAM, DELETE_TIME, FILMS_LINK, LOG_CHANNEL, SUPPORT_GROUP, SUPPORT_LINK, UPDATES_LINK, LANGUAGES, QUALITY, PREMIUM_NOTIFY_CHANNEL, REACTIONS
from pyrogram.types import WebAppInfo, PreCheckoutQuery, Message, LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, LinkPreviewOptions
from pyrogram import Client, filters, enums
from utils import is_premium, get_size, is_subscribed, is_check_admin, get_wish, get_shortlink, get_readable_time, get_poster, temp, get_settings, save_group_settings
from database.users_chats_db import db
from database.ia_filterdb import get_search_results, delete_files, delete_all_files, db_count_documents, second_db_count_documents, get_available_tags
from plugins.commands import get_grp_stg

BUTTONS = {}
CAP = {}
SPELL_CHECK = {}

# --- 🚀 FAST IMDB SPELL SUGGEST API ---
async def get_spell_suggest(query):
    query = query.lower().strip()
    if not query:
        return []
    first_letter = query[0]
    url = f"https://sg.media-imdb.com/suggests/{first_letter}/{query}.json"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return []
                text = await response.text()
                match = re.search(r'imdb\$.*?\((.*)\)$', text, re.DOTALL)
                if match:
                    json_data = match.group(1)
                    data = json.loads(json_data)
                    suggestions = []
                    for item in data.get('d', []):
                        if 'id' in item and str(item['id']).startswith('tt'):
                            title = item.get('l')
                            year = item.get('y', '')
                            movie_id = item.get('id')
                            year_str = f" - {year}" if year else ""
                            suggestions.append({
                                "title": f"{title}{year_str}",
                                "raw_title": title, # ✨ NEEDED FOR AUTO-CORRECTION
                                "id": movie_id
                            })
                    return suggestions
    except Exception as e:
        print(f"Error in IMDB spell suggest: {e}")
    return []

def parse_query(search_text):
    raw_search = search_text.lower()
    req_lang, req_qual, req_year, req_season = None, None, None, None
    
    for l in LANGUAGES:
        if re.search(rf"\b{l}\b", raw_search):
            req_lang = l
            raw_search = re.sub(rf"\b{l}\b", "", raw_search)
            break
            
    for q in QUALITY:
        if re.search(rf"\b{q}\b", raw_search):
            req_qual = q
            raw_search = re.sub(rf"\b{q}\b", "", raw_search)
            break
            
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', raw_search)
    if year_match:
        req_year = year_match.group(1)
        raw_search = re.sub(r'\b(19\d{2}|20\d{2})\b', "", raw_search)
        
    season_match = re.search(r'\b(?:s|season\s*)([0-9]{1,2})\b', raw_search)
    if season_match:
        req_season = f"S{int(season_match.group(1)):02d}"
        raw_search = re.sub(r'\b(?:s|season\s*)([0-9]{1,2})\b', "", raw_search)
        
    clean_search = re.sub(r"\s+", " ", re.sub(r"[-:\"';!]", " ", raw_search)).strip()
    return clean_search, req_lang, req_qual, req_year, req_season

def get_tags(search, key):
    clean_search, h_lang, h_qual, h_year, h_season = parse_query(search)
    st = temp.FILES.get(f"st_{key}", {})
    return {
        'clean_search': clean_search,
        'h_lang': h_lang, 'h_qual': h_qual, 'h_year': h_year, 'h_season': h_season,
        's_lang': st.get('l'), 's_qual': st.get('q'), 's_year': st.get('y'), 's_season': st.get('s'),
        'req_lang': h_lang or st.get('l'),
        'req_qual': h_qual or st.get('q'),
        'req_year': h_year or st.get('y'),
        'req_season': h_season or st.get('s')
    }

def insert_dynamic_buttons(btn, settings, is_prem, shortlink_url, key, req, offset, tags, available_tags):
    idx = 0
    top_btn = []
    
    if tags['h_lang']: top_btn.append(InlineKeyboardButton(f"🔒 {tags['h_lang'].title()}", callback_data=f"locked#Language#{tags['h_lang'].title()}"))
    elif tags['s_lang']: top_btn.append(InlineKeyboardButton(f"✅ {tags['s_lang'].title()}", callback_data=f"languages#{key}#{req}#{offset}"))
    elif available_tags and available_tags.get('languages'): top_btn.append(InlineKeyboardButton("📰 ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}#{req}#{offset}"))
        
    if tags['h_qual']: top_btn.append(InlineKeyboardButton(f"🔒 {tags['h_qual'].upper()}", callback_data=f"locked#Quality#{tags['h_qual'].upper()}"))
    elif tags['s_qual']: top_btn.append(InlineKeyboardButton(f"✅ {tags['s_qual'].upper()}", callback_data=f"quality#{key}#{req}#{offset}"))
    elif available_tags and available_tags.get('qualities'): top_btn.append(InlineKeyboardButton("🔍 ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{key}#{req}#{offset}"))
        
    if top_btn:
        btn.insert(idx, top_btn)
        idx += 1
        
    mid_btn = []
    if tags['h_year']: mid_btn.append(InlineKeyboardButton(f"🔒 {tags['h_year']}", callback_data=f"locked#Year#{tags['h_year']}"))
    elif tags['s_year']: mid_btn.append(InlineKeyboardButton(f"✅ {tags['s_year']}", callback_data=f"years#{key}#{req}#{offset}"))
    elif available_tags and available_tags.get('years') and len(available_tags['years']) > 1:
        mid_btn.append(InlineKeyboardButton("📅 ʏᴇᴀʀs", callback_data=f"years#{key}#{req}#{offset}"))

    if tags['h_season']: mid_btn.append(InlineKeyboardButton(f"🔒 {tags['h_season']}", callback_data=f"locked#Season#{tags['h_season']}"))
    elif tags['s_season']: mid_btn.append(InlineKeyboardButton(f"✅ {tags['s_season']}", callback_data=f"seasons#{key}#{req}#{offset}"))
    elif available_tags and available_tags.get('seasons'):
        mid_btn.append(InlineKeyboardButton("🎭 sᴇᴀsᴏɴs", callback_data=f"seasons#{key}#{req}#{offset}"))
        
    if mid_btn:
        btn.insert(idx, mid_btn)
        idx += 1
        
    if settings['shortlink'] and not is_prem and shortlink_url:
        btn.insert(idx, [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", url=shortlink_url)])
    else:
        btn.insert(idx, [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", callback_data=f"send_all#{key}#{req}")])
    return btn

def create_menu_buttons(items, tag_type, key, offset, req):
    btn = [
        [InlineKeyboardButton(text=str(items[i]).title() if tag_type != 'q' else str(items[i]).upper(), callback_data=f"ts#{tag_type}#{items[i]}#{key}#{offset}#{req}"),
         InlineKeyboardButton(text=str(items[i+1]).title() if tag_type != 'q' else str(items[i+1]).upper(), callback_data=f"ts#{tag_type}#{items[i+1]}#{key}#{offset}#{req}")]
        for i in range(0, len(items)-1, 2)
    ]
    if len(items) % 2 != 0:
        btn.append([InlineKeyboardButton(text=str(items[-1]).title() if tag_type != 'q' else str(items[-1]).upper(), callback_data=f"ts#{tag_type}#{items[-1]}#{key}#{offset}#{req}")])
        
    btn.append([InlineKeyboardButton(text="✖️ ᴄʟᴇᴀʀ ꜰɪʟᴛᴇʀ", callback_data=f"ts#{tag_type}#ALL#{key}#{offset}#{req}")])
    btn.append([InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"b2main_{req}_{key}_{offset}", style=enums.ButtonStyle.PRIMARY)])
    return btn

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_search(client, message):
    if message.text.startswith("/"): return
    try: await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    except: pass
    try: await message.react(emoji=random.choice(REACTIONS), big=True)
    except: pass

    stg = await db.get_bot_sttgs()
    if await is_premium(message.from_user.id, client):
        s = await message.reply(f"<b><i>🔎 `{message.text}` sᴇᴀʀᴄʜɪɴɢ...</i></b>", quote=True)
        await auto_filter(client, message, s)
    else:
        if stg and stg.get('PM_SEARCH'):
            s = await message.reply(f"<b><i>🔎 `{message.text}` sᴇᴀʀᴄʜɪɴɢ...</i></b>", quote=True)
            await auto_filter(client, message, s)
        else:
            clean_search, _, _, _, _ = parse_query(message.text)
            files, n_offset, total = await get_search_results(clean_search)
            if int(total) != 0:
                btn = [[InlineKeyboardButton("🗂 ᴄʟɪᴄᴋ ʜᴇʀᴇ 🗂", url=FILMS_LINK, style=enums.ButtonStyle.PRIMARY)],
                       [InlineKeyboardButton('💎 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss 💎', url=f"https://t.me/{temp.U_NAME}?start=premium", style=enums.ButtonStyle.SUCCESS)]]
                try: await message.reply_text(f'<b><i>🤗 ᴛᴏᴛᴀʟ <code>{total}</code> ʀᴇsᴜʟᴛs ꜰᴏᴜɴᴅ 👇</i></b>\n\n<b>ᴊᴏɪɴ ᴏᴜʀ ᴍᴀɪɴ ɢʀᴏᴜᴘ ᴏʀ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ ᴛᴏ ɢᴇᴛ ꜰɪʟᴇs ᴅɪʀᴇᴄᴛʟʏ ɪɴ ᴘᴍ!</b>', reply_markup=InlineKeyboardMarkup(btn), effect_id=5104841245755180586)
                except: await message.reply_text(f'<b><i>🤗 ᴛᴏᴛᴀʟ <code>{total}</code> ʀᴇsᴜʟᴛs ꜰᴏᴜɴᴅ 👇</i></b>\n\n<b>ᴊᴏɪɴ ᴏᴜʀ ᴍᴀɪɴ ɢʀᴏᴜᴘ ᴏʀ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ ᴛᴏ ɢᴇᴛ ꜰɪʟᴇs ᴅɪʀᴇᴄᴛʟʏ ɪɴ ᴘᴍ!</b>', reply_markup=InlineKeyboardMarkup(btn))

@Client.on_message(filters.group & filters.text & filters.incoming)
async def group_search(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message and message.from_user else 0
    stg = await db.get_bot_sttgs()
    if stg and stg.get('AUTO_FILTER'):
        if not user_id:
            return await message.reply("<b>⚠️ ɪ ᴀᴍ ɴᴏᴛ ᴡᴏʀᴋɪɴɢ ꜰᴏʀ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴs!</b>")
        try: await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        except: pass
        
        if message.chat.id == SUPPORT_GROUP:
            clean_search, _, _, _, _ = parse_query(message.text)
            files, offset, total = await get_search_results(clean_search)
            if files: await message.reply_text(f'<b>📊 ᴛᴏᴛᴀʟ <code>{total}</code> ʀᴇsᴜʟᴛs ꜰᴏᴜɴᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Here", url=FILMS_LINK, style=enums.ButtonStyle.PRIMARY)]]))
            return
            
        if message.text.startswith("/"): return
        elif '@admin' in message.text.lower() or '@admins' in message.text.lower():
            if await is_check_admin(client, message.chat.id, message.from_user.id): return
            admins = []
            async for member in client.get_chat_members(chat_id=message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                if not member.user.is_bot:
                    admins.append(member.user.id)
                    if member.status == enums.ChatMemberStatus.OWNER:
                        try:
                            sent_msg = await (message.reply_to_message or message).forward(member.user.id)
                            await sent_msg.reply_text(f"<b>#Attention</b>\n★ <b>User:</b> {message.from_user.mention}\n★ <b>Group:</b> {message.chat.title}\n\n★ <a href={(message.reply_to_message or message).link}><b>Go to message</b></a>", link_preview_options=LinkPreviewOptions(is_disabled=True))
                        except: pass
            hidden_mentions = (f'[\u2064](tg://user?id={uid})' for uid in admins)
            return await message.reply_text('<b>✅ ʀᴇᴘᴏʀᴛ sᴇɴᴛ!</b>' + ''.join(hidden_mentions))
            
        elif re.findall(r'https?://\S+|www\.\S+|t\.me/\S+|@\w+', message.text):
            if await is_check_admin(client, message.chat.id, message.from_user.id): return
            await message.delete()
            return await message.reply('<b>⚠️ ʟɪɴᴋs ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ʜᴇʀᴇ!</b>')
        
        elif '#request' in message.text.lower():
            if message.from_user.id in ADMINS: return
            await client.send_message(LOG_CHANNEL, f"<b>#Request</b>\n★ <b>User:</b> {message.from_user.mention}\n★ <b>Group:</b> {message.chat.title}\n\n★ <b>Message:</b> {re.sub(r'#request', '', message.text.lower())}")
            return await message.reply_text("<b>✅ ʀᴇǫᴜᴇsᴛ sᴇɴᴛ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>")
        else:
            s = await message.reply(f"<b><i>🔎 `{message.text}` sᴇᴀʀᴄʜɪɴɢ...</i></b>")
            await auto_filter(client, message, s)
    else:
        k = await message.reply_text('<b>❌ ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ ɪs ᴏꜰꜰ!</b>')
        await asyncio.sleep(5)
        await k.delete()
        try: await message.delete()
        except: pass

@Client.on_callback_query(filters.regex(r"^(next|b2main)_"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀs ʀᴇsᴜʟᴛs!", show_alert=True)
    try: offset = int(offset)
    except: offset = 0
    
    search = BUTTONS.get(key)
    cap = CAP.get(key)
    if not search: return await query.answer(f"⚠️ Request Expired!", show_alert=True)

    tags = get_tags(search, key)
    
    if ident == "b2main" and temp.FILES.get(key):
        files = temp.FILES.get(key)
        total = temp.FILES.get(f"total_{key}", 0)
        n_offset = offset + MAX_BTN if (offset + MAX_BTN) < total else 0
        if n_offset == 0 and total > MAX_BTN and offset >= MAX_BTN: 
             n_offset = ''
    else:
        files, n_offset, total = await get_search_results(tags['clean_search'], offset=offset, req_lang=tags['req_lang'], req_qual=tags['req_qual'], req_year=tags['req_year'], req_season=tags['req_season'])
        temp.FILES[key] = files
        temp.FILES[f"total_{key}"] = total

    available_tags = temp.FILES.get(f"tags_{key}", {})
    if not available_tags:
        available_tags = await get_available_tags(tags['clean_search'], req_lang=tags['req_lang'], req_qual=tags['req_qual'], req_year=tags['req_year'], req_season=tags['req_season'])
        temp.FILES[f"tags_{key}"] = available_tags
    
    if not files: return

    settings = await get_settings(query.message.chat.id)
    del_msg = f"\n\n<b><blockquote>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</blockquote></b>" if settings["auto_delete"] else ''
    
    files_link = ''
    if settings['links']:
        for file_num, file in enumerate(files, start=offset+1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file['_id']}>[{get_size(file['file_size'])}] {file['file_name']}</a></b>"""
        btn = []
    else:
        btn = [[InlineKeyboardButton(text=f"{get_size(file['file_size'])} - {file['file_name']}", callback_data=f"file#{file['_id']}")] for file in files]
        
    is_prem = await is_premium(query.from_user.id, bot)
    sl_url = await get_shortlink(f'https://t.me/{temp.U_NAME}?start=all_{query.message.chat.id}_{key}', query.from_user.id, query.message.chat.id) if settings['shortlink'] else ""
    btn = insert_dynamic_buttons(btn, settings, is_prem, sl_url, key, req, offset, tags, available_tags)

    if 0 < offset <= MAX_BTN: b_offset = 0
    elif offset == 0: b_offset = None
    else: b_offset = offset - MAX_BTN
        
    if n_offset == 0:
        btn.append([InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{b_offset}", style=enums.ButtonStyle.PRIMARY),
                    InlineKeyboardButton(f"{math.ceil(int(offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons")])
    elif b_offset is None:
        btn.append([InlineKeyboardButton(f"{math.ceil(int(offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
                    InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"next_{req}_{key}_{n_offset}", style=enums.ButtonStyle.PRIMARY)])
    else:
        btn.append([InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{b_offset}", style=enums.ButtonStyle.PRIMARY),
                    InlineKeyboardButton(f"{math.ceil(int(offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
                    InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"next_{req}_{key}_{n_offset}", style=enums.ButtonStyle.PRIMARY)])
                    
    await query.message.edit_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), link_preview_options=LinkPreviewOptions(is_disabled=True), parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"^(languages|quality|years|seasons)#"))
async def dynamic_menus(client: Client, query: CallbackQuery):
    action, key, req, offset = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀs ʀᴇsᴜʟᴛs!", show_alert=True)
        
    available_tags = temp.FILES.get(f"tags_{key}", {})
    
    if action == "languages":
        items = available_tags.get('languages', LANGUAGES)
        msg_text = "<b>ɪɴ ᴡʜɪᴄʜ ʟᴀɴɢᴜᴀɢᴇ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ, sᴇʟᴇᴄᴛ ʜᴇʀᴇ 👇</b>"
        tag_type = 'l'
    elif action == "quality":
        items = available_tags.get('qualities', QUALITY)
        msg_text = "<b>ɪɴ ᴡʜɪᴄʜ ǫᴜᴀʟɪᴛʏ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ, sᴇʟᴇᴄᴛ ʜᴇʀᴇ 👇</b>"
        tag_type = 'q'
    elif action == "years":
        items = sorted(available_tags.get('years', []), reverse=True)
        msg_text = "<b>ɪɴ ᴡʜɪᴄʜ ʏᴇᴀʀ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ, sᴇʟᴇᴄᴛ ʜᴇʀᴇ 👇</b>"
        tag_type = 'y'
    elif action == "seasons":
        items = sorted(available_tags.get('seasons', []))
        msg_text = "<b>ɪɴ ᴡʜɪᴄʜ sᴇᴀsᴏɴ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ, sᴇʟᴇᴄᴛ ʜᴇʀᴇ 👇</b>"
        tag_type = 's'

    if not items:
        return await query.answer("sᴏʀʀʏ, ɴᴏ ᴏᴘᴛɪᴏɴs ᴀᴠᴀɪʟᴀʙʟᴇ!", show_alert=True)

    btn = create_menu_buttons(items, tag_type, key, offset, req)
    await query.message.edit_text(msg_text, link_preview_options=LinkPreviewOptions(is_disabled=True), reply_markup=InlineKeyboardMarkup(btn))

@Client.on_callback_query(filters.regex(r"^ts#"))
async def generic_tag_search(client: Client, query: CallbackQuery):
    _, tag_type, val, key, offset, req = query.data.split("#")
    if int(req) != query.from_user.id: return await query.answer("⚠️ Not for you!", show_alert=True)

    search = BUTTONS.get(key)
    cap = CAP.get(key)
    if not search: return await query.answer("⚠️ Request Expired!", show_alert=True)

    st = temp.FILES.get(f"st_{key}", {})
    if val == "ALL":
        if tag_type in st: del st[tag_type] 
    else:
        st[tag_type] = val
    temp.FILES[f"st_{key}"] = st
    
    tags = get_tags(search, key)
    files, t_offset, total_results = await get_search_results(tags['clean_search'], offset=0, req_lang=tags['req_lang'], req_qual=tags['req_qual'], req_year=tags['req_year'], req_season=tags['req_season'])
    
    temp.FILES[key] = files
    temp.FILES[f"total_{key}"] = total_results
    
    available_tags = await get_available_tags(tags['clean_search'], req_lang=tags['req_lang'], req_qual=tags['req_qual'], req_year=tags['req_year'], req_season=tags['req_season'])
    temp.FILES[f"tags_{key}"] = available_tags
    
    if not files: return await query.answer(f"sᴏʀʀʏ '{val.title()}' ꜰɪʟᴇs ɴᴏᴛ ꜰᴏᴜɴᴅ 😕", show_alert=1)
        
    settings = await get_settings(query.message.chat.id)
    del_msg = f"\n\n<b><blockquote>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</blockquote></b>" if settings["auto_delete"] else ''
    files_link = ''

    if settings['links']:
        btn = []
        for file_num, file in enumerate(files, start=1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file['_id']}>[{get_size(file['file_size'])}] {file['file_name']}</a></b>"""
    else:
        btn = [[InlineKeyboardButton(text=f"{get_size(file['file_size'])} - {file['file_name']}", callback_data=f"file#{file['_id']}")] for file in files]
        
    is_prem = await is_premium(query.from_user.id, client)
    sl_url = await get_shortlink(f'https://t.me/{temp.U_NAME}?start=all_{query.message.chat.id}_{key}', query.from_user.id, query.message.chat.id) if settings['shortlink'] else ""
    
    btn = insert_dynamic_buttons(btn, settings, is_prem, sl_url, key, req, offset, tags, available_tags)
    
    if t_offset != "":
        btn.append([InlineKeyboardButton(text=f"1/{math.ceil(int(total_results) / MAX_BTN)}", callback_data="buttons"),
                    InlineKeyboardButton(text="ɴᴇxᴛ »", callback_data=f"next_{req}_{key}_{t_offset}", style=enums.ButtonStyle.PRIMARY)])
    
    await query.message.edit_text(cap + files_link + del_msg, link_preview_options=LinkPreviewOptions(is_disabled=True), reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)


@Client.on_callback_query(filters.regex(r"^locked#"))
async def locked_filter_cb(client, query):
    _, filter_type, filter_val = query.data.split("#")
    await query.answer(f"🔒 {filter_type} is explicitly locked to {filter_val} by your search query!", show_alert=True)

@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    data = query.data.split('#')
    user = int(data[2])
    if user != 0 and query.from_user.id != user:
        return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀs ʀᴇsᴜʟᴛs!", show_alert=True)

    if data[1] == "dbmatch": search = query.message.reply_markup.inline_keyboard[0][0].text.replace("✨ ", "")
    else:
        movie = await get_poster(data[1], id=True)
        search = movie.get('title')

    s = await query.message.edit_text(f"<b><i>🔍 <code>{search}</code> ᴄʜᴇᴄᴋɪɴɢ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ...</i></b>")
    await query.answer('')
    
    clean_search, req_lang, req_qual, req_year, req_season = parse_query(search)
    files, offset, total_results = await get_search_results(clean_search, req_lang=req_lang, req_qual=req_qual, req_year=req_year, req_season=req_season)
    
    if files:
        k = (search, files, offset, total_results)
        if not query.message: return await query.answer("ᴍᴇssᴀɢᴇ ᴇxᴘɪʀᴇᴅ! sᴇᴀʀᴄʜ ᴀɢᴀɪɴ.", show_alert=True)
        await auto_filter(bot, query, s, spoll=k)
    else:
        k = await query.message.edit(text=f"<b>👋 ʜᴇʟʟᴏ {query.from_user.mention},\n\nɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ '{search}' ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ. 😔</b>", link_preview_options=LinkPreviewOptions(is_disabled=True))
        asyncio.create_task(bot.send_message(LOG_CHANNEL, f"<b>#No_Result</b>\n★ <b>Requester:</b> {query.from_user.mention}\n★ <b>Content:</b> {search}"))
        await asyncio.sleep(60)
        await k.delete()
        try: await query.message.reply_to_message.delete()
        except: pass

async def auto_filter(client, msg, s, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        search = message.text
        clean_search, req_lang, req_qual, req_year, req_season = parse_query(search)
        files, offset, total_results = await get_search_results(clean_search, req_lang=req_lang, req_qual=req_qual, req_year=req_year, req_season=req_season)
        if not files:
            if settings["spell_check"]:
                return await advantage_spell_chok(client, message, s)
            else: return await s.edit(f"<b>ɪ ᴄᴀɴ'ᴛ ꜰɪɴᴅ '{search}'</b>")
    else:
        # ✨ Handle both Button Clicks and Zero-Click Auto-Correct properly
        if hasattr(msg, "message"): # CallbackQuery
            settings = await get_settings(msg.message.chat.id)
            message = msg.message.reply_to_message if msg.message.reply_to_message else msg.message
        else: # Direct text Message
            settings = await get_settings(msg.chat.id)
            message = msg
            
        search, files, offset, total_results = spoll
        clean_search, req_lang, req_qual, req_year, req_season = parse_query(search)

    if not message or message is None:
        if hasattr(msg, "answer"): await msg.answer("ᴏʟᴅ ᴍᴇꜱꜱᴀɢᴇ! ꜱᴇᴀʀᴄʜ ᴀɢᴀɪɴ.", show_alert=True)
        return await s.edit("<b>❌ ᴇʀʀᴏʀ: ᴏʀɪɢɪɴᴀʟ ᴍᴇꜱꜱᴀɢᴇ ɴᴏᴛ ꜰᴏᴜɴᴅ.</b>")

    req = message.from_user.id if message.from_user else 0
    try: key = f"{message.chat.id}-{message.id}"
    except AttributeError: key = f"{msg.message.chat.id}-{msg.message.id}"
 
    temp.FILES[f"st_{key}"] = {} 
    BUTTONS[key] = search
    tags = get_tags(search, key)
    
    temp.FILES[key] = files
    temp.FILES[f"total_{key}"] = total_results
    
    available_tags = await get_available_tags(tags['clean_search'], req_lang=tags['req_lang'], req_qual=tags['req_qual'], req_year=tags['req_year'], req_season=tags['req_season'])
    temp.FILES[f"tags_{key}"] = available_tags

    files_link = ""
    if settings['links']:
        btn = []
        for file_num, file in enumerate(files, start=1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{message.chat.id}_{file['_id']}>[{get_size(file['file_size'])}] {file['file_name']}</a></b>"""
    else:
        btn = [[InlineKeyboardButton(text=f"{get_size(file['file_size'])} - {file['file_name']}", callback_data=f'file#{file["_id"]}')] for file in files]   
    
    is_prem = await is_premium(message.from_user.id, client)
    sl_url = await get_shortlink(f'https://t.me/{temp.U_NAME}?start=all_{message.chat.id}_{key}', req, message.chat.id) if settings['shortlink'] else ""
    btn = insert_dynamic_buttons(btn, settings, is_prem, sl_url, key, req, offset, tags, available_tags)

    if offset != "":
        btn.append([InlineKeyboardButton(text=f"1/{math.ceil(int(total_results) / MAX_BTN)}", callback_data="buttons"),
                    InlineKeyboardButton(text="ɴᴇxᴛ »", callback_data=f"next_{req}_{key}_{offset}", style=enums.ButtonStyle.PRIMARY)])

    imdb = await get_poster(tags['clean_search'], file=(files[0])['file_name']) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=tags['clean_search'], title=imdb['title'], kind=imdb['kind'], votes=imdb['votes'],
            tmdb_id=imdb["tmdb_id"], runtime=imdb["runtime"], release_date=imdb['release_date'],
            year=imdb['year'], genres=imdb['genres'], poster=imdb['poster'], plot=imdb['plot'],
            rating=imdb['rating'], url=imdb['url'], languages=imdb['languages'], countries=imdb['countries'], **locals()
        )
    else: cap = f"<b>💭 ʜᴇʏ {message.from_user.mention},\n♻️ ʜᴇʀᴇ ɪ ꜰᴏᴜɴᴅ ꜰᴏʀ ʏᴏᴜʀ sᴇᴀʀᴄʜ {search}...</b>"
    CAP[key] = cap
    del_msg = f"\n\n<b><blockquote>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</blockquote></b>" if settings["auto_delete"] else ''
    
    if imdb and imdb.get('poster'):
        await s.delete()
        try:
            k = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024] + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML, quote=True)
            if settings["auto_delete"]:
                await asyncio.sleep(DELETE_TIME)
                await k.delete()
                try: await message.delete()
                except: pass
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            poster = imdb.get('poster').replace('.jpg', "._V1_UX360.jpg")
            k = await message.reply_photo(photo=poster, caption=cap[:1024] + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML, quote=True)
            if settings["auto_delete"]:
                await asyncio.sleep(DELETE_TIME)
                await k.delete()
                try: await message.delete()
                except: pass
        except Exception as e:
            k = await message.reply_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), link_preview_options=LinkPreviewOptions(is_disabled=True), parse_mode=enums.ParseMode.HTML, quote=True)
            if settings["auto_delete"]:
                await asyncio.sleep(DELETE_TIME)
                await k.delete()
                try: await message.delete()
                except: pass
    else:
        k = await s.edit_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), link_preview_options=LinkPreviewOptions(is_disabled=True), parse_mode=enums.ParseMode.HTML)
        if settings["auto_delete"]:
            await asyncio.sleep(DELETE_TIME)
            await k.delete()
            try: await message.delete()
            except: pass

# --- 🚀 ZERO-CLICK AUTO-CORRECT & SUGGESTIONS ---
async def advantage_spell_chok(client, message, s):
    search = message.text
    google_search = search.replace(" ", "+")
    user_id = message.from_user.id if message.from_user else 0
    btn = [[InlineKeyboardButton("⚠️ ɪɴꜱᴛʀᴜᴄᴛɪᴏɴꜱ", callback_data='instructions'), InlineKeyboardButton("🔎 ꜱᴇᴀʀᴄʜ ɢᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={google_search}")],[InlineKeyboardButton("🛸 ʀᴇǫᴜᴇꜱᴛ ᴍᴏᴠɪᴇ", callback_data=f"request_msg_{user_id}")]]

    movies = await get_spell_suggest(search)
        
    if movies:
        # ✨ AUTO-CORRECTION LOGIC START
        for movie in movies:
            raw_title = movie.get("raw_title")
            if not raw_title: continue
            
            clean_search = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|bro|bruh|broh|helo|that|find|dubbed|link|venum|iruka|pannunga|pannungga|anuppunga|anupunga|anuppungga|anupungga|film|undo|kitti|kitty|tharu|kittumo|kittum|movie|any(one)|with\ssubtitle(s)?)", "", raw_title, flags=re.IGNORECASE)
            clean_search = re.sub(r"\s+", " ", clean_search).strip()
            
            files, offset, total_results = await get_search_results(clean_search)
            
            if files:
                await s.edit_text(f"<b>[ ⚠️ ᴡʀᴏɴɢ ꜱᴘᴇʟʟɪɴɢ ᴅᴇᴛᴇᴄᴛᴇᴅ ]</b>\n\n✨ <i>ᴀᴜᴛᴏ-ᴄᴏʀʀᴇᴄᴛɪɴɢ ᴀɴᴅ ꜱᴇᴀʀᴄʜɪɴɢ ꜰᴏʀ:</i> <b>{raw_title}</b>...")
                await asyncio.sleep(1.5)
                spoll_data = (raw_title, files, offset, total_results)
                return await auto_filter(client, message, s, spoll=spoll_data)
        # ✨ AUTO-CORRECTION LOGIC END
        
        movielist = [m['title'] for m in movies[:5]]
        SPELL_CHECK[message.id] = movielist
        buttons = [[InlineKeyboardButton(text=movie.strip(), callback_data=f"spolling#{user_id}#{k}")] for k, movie in enumerate(movielist)]
        buttons.append([InlineKeyboardButton("🚫 ᴄʟᴏꜱᴇ 🚫", callback_data="close_data", style=enums.ButtonStyle.DANGER)])
        
        suggestion_msg = await s.edit_text(text=f"<b>👋 ʜᴇʟʟᴏ {message.from_user.mention},\n\nɪ ꜰᴏᴜɴᴅ ꜱᴏᴍᴇ ꜱɪᴍɪʟᴀʀ ᴛɪᴛʟᴇꜱ. ꜱᴇʟᴇᴄᴛ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ᴏɴᴇ: 👇</b>", reply_markup=InlineKeyboardMarkup(buttons), link_preview_options=LinkPreviewOptions(is_disabled=True))
        await asyncio.sleep(300)
        try:
            await suggestion_msg.delete()
            await message.delete()
        except: pass
        return

    # If IMDB doesn't have it, try DB Fuzzy match
    all_titles = await db.get_all_movie_titles()
    matches = process.extractBests(search, all_titles, score_cutoff=60, limit=5)
    if matches:
        # ✨ FUZZY MATCH AUTO-CORRECTION START
        best_match = matches[0][0]
        clean_search = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|bro|bruh|broh|helo|that|find|dubbed|link|venum|iruka|pannunga|pannungga|anuppunga|anupunga|anuppungga|anupungga|film|undo|kitti|kitty|tharu|kittumo|kittum|movie|any(one)|with\ssubtitle(s)?)", "", best_match, flags=re.IGNORECASE)
        clean_search = re.sub(r"\s+", " ", clean_search).strip()
        
        files, offset, total_results = await get_search_results(clean_search)
        
        if files:
            await s.edit_text(f"<b>[ ⚠️ ᴡʀᴏɴɢ ꜱᴘᴇʟʟɪɴɢ ᴅᴇᴛᴇᴄᴛᴇᴅ ]</b>\n\n✨ <i>ᴀᴜᴛᴏ-ᴄᴏʀʀᴇᴄᴛɪɴɢ ᴛᴏ ɴᴇᴀʀᴇꜱᴛ ᴍᴀᴛᴄʜ:</i> <b>{best_match}</b>...")
            await asyncio.sleep(1.5)
            spoll_data = (best_match, files, offset, total_results)
            return await auto_filter(client, message, s, spoll=spoll_data)
        # ✨ FUZZY MATCH AUTO-CORRECTION END
        
        db_btns = [[InlineKeyboardButton(text=f"✨ {match[0]}", callback_data=f"spolling#dbmatch#{user_id}#{match[0][:20]}")] for match in matches]
        db_btns.extend(btn)
        return await s.edit_text(text=f"<b>👋 ʜᴇʏ {message.from_user.mention},\n\nɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ '{search}' ᴅɪʀᴇᴄᴛʟʏ.\nᴅɪᴅ ʏᴏᴜ ᴍᴇᴀɴ ᴏɴᴇ ᴏꜰ ᴛʜᴇꜱᴇ ꜰʀᴏᴍ ᴍʏ ʟɪʙʀᴀʀʏ? 👇</b>", reply_markup=InlineKeyboardMarkup(db_btns), link_preview_options=LinkPreviewOptions(is_disabled=True))

    n = await s.edit_text(text=script.NOT_FILE_TXT.format(message.from_user.mention, search), reply_markup=InlineKeyboardMarkup(btn), link_preview_options=LinkPreviewOptions(is_disabled=True))
    asyncio.create_task(temp.BOT.send_message(LOG_CHANNEL, f"<b>#No_Result</b>\n★ <b>User:</b> {message.from_user.mention}\n★ <b>Search:</b> {search}"))
    await asyncio.sleep(60)
    await n.delete()
    try: await message.delete()
    except: pass
    return

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        try:
            user = query.message.reply_to_message.from_user.id
        except:
            user = query.from_user.id
        if int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(f"⚠️ ᴛʜɪs ɪs ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ!", show_alert=True)
        await query.answer("✅ ᴄʟᴏsᴇᴅ!")
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
            
    elif query.data == "confirm_delete_all":
        if query.from_user.id not in ADMINS:
            return await query.answer("⚠️ ᴏᴡɴᴇʀs ᴏɴʟʏ!", show_alert=True)
        await query.message.edit("<b>🗑 ᴡɪᴘɪɴɢ ᴅᴀᴛᴀʙᴀsᴇ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>")
        deleted_count = await delete_all_files()
        await query.message.edit(f"<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴡɪᴘᴇᴅ ᴇɴᴛɪʀᴇ ᴅᴀᴛᴀʙᴀsᴇ!\n\n🗑 ᴛᴏᴛᴀʟ ꜰɪʟᴇs ʀᴇᴍᴏᴠᴇᴅ: <code>{deleted_count}</code>\n🚀 ɴᴏᴡ ʏᴏᴜ ᴄᴀɴ sᴛᴀʀᴛ ᴀ ꜰʀᴇsʜ ɪɴᴅᴇxɪɴɢ.</b>")
  
    elif query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        try:
            user = query.message.reply_to_message.from_user.id
        except:
            user = query.message.from_user.id
        if int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀs ʀᴇsᴜʟᴛs!", show_alert=True)
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file_id}")

    elif query.data.startswith("get_del_file"):
        ident, group_id, file_id = query.data.split("#")
        if not await is_premium(query.from_user.id, client):
            return await query.answer(f"💎 ᴏɴʟʏ ꜰᴏʀ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs, ᴜsᴇ /plan ꜰᴏʀ ᴅᴇᴛᴀɪʟs!", show_alert=True)
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=file_{group_id}_{file_id}")
        await query.message.delete()

    elif query.data.startswith("get_del_send_all_files"):
        ident, group_id, key = query.data.split("#")
        if not await is_premium(query.from_user.id, client):
            return await query.answer(f"💎 ᴏɴʟʏ ꜰᴏʀ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs, ᴜsᴇ /plan ꜰᴏʀ ᴅᴇᴛᴀɪʟs!", show_alert=True)
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=all_{group_id}_{key}")
        await query.message.delete()
        
    elif query.data.startswith("stream"):
        file_id = query.data.split('#', 1)[1]
        if not await is_premium(query.from_user.id, client):
            return await query.answer(f"💎 ᴏɴʟʏ ꜰᴏʀ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs, ᴜsᴇ /plan ꜰᴏʀ ᴅᴇᴛᴀɪʟs!", show_alert=True)
        msg = await client.send_cached_media(chat_id=BIN_CHANNEL, file_id=file_id)
        watch = f"{URL}watch/{msg.id}"
        download = f"{URL}download/{msg.id}"
        btn=[[
            InlineKeyboardButton("🎬 ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇᴇ", url=watch, style=enums.ButtonStyle.PRIMARY),
            InlineKeyboardButton("🚀 ꜰᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ", url=download, style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('🚫 ᴄʟᴏsᴇ 🚫', callback_data='close_data', style=enums.ButtonStyle.DANGER)
        ]]
        reply_markup=InlineKeyboardMarkup(btn)
        await query.edit_message_reply_markup(
            reply_markup=reply_markup
        )
    
            
    elif query.data.startswith("checksub"):
        ident, mc = query.data.split("#")
        grp_id = None
        if mc.startswith(('file_', 'all_', 'shortlink_')):
            try:
                grp_id = int(mc.split("_")[1])
            except:
                pass
                
        btn = await is_subscribed(client, query, grp_id)
        if btn:
            await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴀʟʟ ʀᴇǫᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.", show_alert=True)
            btn.append(
                [InlineKeyboardButton("🔁 ᴛʀʏ ᴀɢᴀɪɴ 🔁", callback_data=f"checksub#{mc}", style=enums.ButtonStyle.PRIMARY)]
            )
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
            return
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start={mc}")
        await query.message.delete()

    elif query.data == "buttons":
        await query.answer()

    elif query.data == "instructions":
        await query.answer("📋 ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇsᴛ ꜰᴏʀᴍᴀᴛ:\n\n➲ ᴇxᴀᴍᴘʟᴇ: Black Adam ᴏʀ Black Adam 2022\n\n📺 ᴛᴠ sᴇʀɪᴇs ʀᴇǫᴜᴇsᴛ ꜰᴏʀᴍᴀᴛ:\n\n➲ ᴇxᴀᴍᴘʟᴇ: Loki S01E01 ᴏʀ Loki S01 E01\n\n⚠️ ᴅᴏɴ'ᴛ ᴜsᴇ sʏᴍʙᴏʟs.", show_alert=True)

    elif query.data == 'activate_trial':
        mp = await db.get_plan(query.from_user.id)
        if mp['trial']:
            return await query.message.edit('<b>⚠️ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ᴜsᴇᴅ ʏᴏᴜʀ ᴛʀɪᴀʟ, ᴜsᴇ /plan ᴛᴏ ᴀᴄᴛɪᴠᴀᴛᴇ ᴀ ᴘʟᴀɴ.</b>')
        ex = datetime.now() + timedelta(hours=1)
        mp['expire'] = ex
        mp['trial'] = True
        mp['plan'] = '1 hour'
        mp['premium'] = True
        await db.update_plan(query.from_user.id, mp)
        await query.message.edit(f"<b>🎉 ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs! ʏᴏᴜ ᴀᴄᴛɪᴠᴀᴛᴇᴅ ᴛʀɪᴀʟ ꜰᴏʀ 1 ʜᴏᴜʀ.\n\n⏳ ᴇxᴘɪʀᴇs: <code>{ex.strftime('%Y.%m.%d %H:%M:%S')}</code></b>")

    elif query.data == 'activate_plan':
        q = await query.message.edit('<b>🔢 ʜᴏᴡ ᴍᴀɴʏ ᴅᴀʏs ʏᴏᴜ ɴᴇᴇᴅ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ?\n\n➲ sᴇɴᴅ ᴅᴀʏs ᴀs ɴᴜᴍʙᴇʀ:</b>')
        msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id)
        try:
            d = int(msg.text)
        except:
            await q.delete()
            return await query.message.reply('<b>❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!\n\n➲ ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ 7 ᴅᴀʏs, ᴛʜᴇɴ sᴇɴᴅ 7 ᴏɴʟʏ.</b>')
        transaction_note = f'{d} days premium plan for {query.from_user.id}'
        amount = d * PRE_DAY_AMOUNT
        upi_uri = f"upi://pay?pa={UPI_ID}&pn={UPI_NAME}&am={amount}&cu=INR&tn={transaction_note}"
        qr = qrcode.make(upi_uri)
        p = f"upi_qr_{query.from_user.id}.png"
        qr.save(p)
        await q.delete()
        await query.message.reply_photo(p, caption=f"<b>💳 {d} ᴅᴀʏs ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ᴀᴍᴏᴜɴᴛ ɪs <code>{amount} ɪɴʀ</code>\n\n📱 sᴄᴀɴ ᴛʜɪs ǫʀ ɪɴ ʏᴏᴜʀ ᴜᴘɪ ᴀᴘᴘ ᴀɴᴅ ᴘᴀʏ ᴛʜᴇ ᴀᴍᴏᴜɴᴛ (ᴅʏɴᴀᴍɪᴄ ǫʀ)\n\n📸 sᴇɴᴅ ʏᴏᴜʀ ʀᴇᴄᴇɪᴘᴛ ᴀs ᴀ ᴘʜᴏᴛᴏ ʜᴇʀᴇ (ᴛɪᴍᴇᴏᴜᴛ ɪɴ 10 ᴍɪɴs)\n\n💬 sᴜᴘᴘᴏʀᴛ: {RECEIPT_SEND_USERNAME}</b>")
        os.remove(p)
        try:
            msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id, timeout=600)
        except ListenerTimeout:
            await q.delete()
            return await query.message.reply(f'<b>⏱ ʏᴏᴜʀ ᴛɪᴍᴇ ɪs ᴏᴠᴇʀ, sᴇɴᴅ ʏᴏᴜʀ ʀᴇᴄᴇɪᴘᴛ ᴛᴏ: {RECEIPT_SEND_USERNAME}</b>')
        if msg.photo:
            await q.delete()
            await query.message.reply(f'<b>✅ ʏᴏᴜʀ ʀᴇᴄᴇɪᴘᴛ ᴡᴀs sᴇɴᴛ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ!\n💬 sᴜᴘᴘᴏʀᴛ: {RECEIPT_SEND_USERNAME}</b>')
            await client.send_photo(RECEIPT_SEND_USERNAME, msg.photo.file_id, transaction_note)
        else:
            await q.delete()
            await query.message.reply(f"<b>❌ ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ᴘʜᴏᴛᴏ, sᴇɴᴅ ʏᴏᴜʀ ʀᴇᴄᴇɪᴘᴛ ᴛᴏ: {RECEIPT_SEND_USERNAME}</b>")

    
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton("+ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ +", url=f'http://t.me/{temp.U_NAME}?startgroup=start', style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇs', url=UPDATES_LINK),
            InlineKeyboardButton('🧑‍💻 ꜱᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
        ],[
            InlineKeyboardButton('👨‍🚒 ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('📚 ᴀʙᴏᴜᴛ', callback_data='about')
        ],[
            InlineKeyboardButton('💎 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss 💎', url=f"https://t.me/{temp.U_NAME}?start=premium")
        ],[
            InlineKeyboardButton('🌐 ᴍɪɴɪ ᴡᴇʙᴀᴘᴘ ɴᴇᴛᴡᴏʀᴋ 🌐', style=enums.ButtonStyle.SUCCESS, web_app=WebAppInfo(url=URL))
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.START_TXT.format(query.from_user.mention, get_wish())),
            reply_markup=reply_markup
        )
        
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('📊 sᴛᴀᴛᴜs 📊', callback_data='stats', style=enums.ButtonStyle.PRIMARY),
            InlineKeyboardButton('🤖 sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ 🤖', callback_data='source', style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('🧑‍💻 ʙᴏᴛ ᴏᴡɴᴇʀ 🧑‍💻', callback_data='owner')
        ],[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='start', style=enums.ButtonStyle.DANGER)
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.MY_ABOUT_TXT.format(temp.U_NAME, temp.B_NAME)),
            reply_markup=reply_markup
        )

    elif query.data == "stats":
        if query.from_user.id not in ADMINS:
            return await query.answer("⚠️ ᴀᴅᴍɪɴs ᴏɴʟʏ!", show_alert=True)
        files = db_count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        prm = await db.get_premium_count()
        used_files_db_size = get_size(await db.get_files_db_size())
        used_data_db_size = get_size(await db.get_data_db_size())

        if SECOND_FILES_DATABASE_URL:
            secnd_files_db_used_size = get_size(await db.get_second_files_db_size())
            secnd_files = second_db_count_documents()
        else:
            secnd_files_db_used_size = '-'
            secnd_files = '-'
        uptime = get_readable_time(time_now() - temp.START_TIME)
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='about', style=enums.ButtonStyle.PRIMARY)
        ]]
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.STATUS_TXT.format(users, prm, chats, used_data_db_size, files, used_files_db_size, secnd_files, secnd_files_db_used_size, uptime)),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    elif query.data == "owner":
        buttons = [[InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='about', style=enums.ButtonStyle.PRIMARY)]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.MY_OWNER_TXT),
            reply_markup=reply_markup
        )
        
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('ᴜsᴇʀ ᴄᴏᴍᴍᴀɴᴅs', callback_data='user_command', style=enums.ButtonStyle.PRIMARY),
            InlineKeyboardButton('ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs', callback_data='admin_command', style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='start', style=enums.ButtonStyle.DANGER)
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.HELP_TXT.format(query.from_user.mention)),
            reply_markup=reply_markup
        )

    elif query.data == "user_command":
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='help', style=enums.ButtonStyle.PRIMARY)
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.USER_COMMAND_TXT),
            reply_markup=reply_markup
        )
        
    elif query.data == "admin_command":
        if query.from_user.id not in ADMINS:
            return await query.answer("⚠️ ᴀᴅᴍɪɴs ᴏɴʟʏ!", show_alert=True)
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='help', style=enums.ButtonStyle.PRIMARY)
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.ADMIN_COMMAND_TXT),
            reply_markup=reply_markup
        )

    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('≼ ʙᴀᴄᴋ', callback_data='about', style=enums.ButtonStyle.PRIMARY)
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.SOURCE_TXT),
            reply_markup=reply_markup
        )
  
    elif query.data.startswith("bool_setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
            return

        if status == "True":
            await save_group_settings(int(grp_id), set_type, False)
        else:
            await save_group_settings(int(grp_id), set_type, True)

        btn = await get_grp_stg(int(grp_id))
        await query.message.edit_reply_markup(InlineKeyboardMarkup(btn))
        
    elif query.data.startswith("fsub_info"):
        _, grp_id = query.data.split("#")
        user_id = query.from_user.id
        
        if user_id in ADMINS or await db.is_sudo(user_id):
            await query.answer("💡 ᴛᴏ ᴜᴘᴅᴀᴛᴇ, sᴇɴᴅ /set_fsub ᴏʀ /set_req_fsub ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ.", show_alert=True)
        else:
            await query.answer("⚠️ ᴛʜɪs ꜰᴇᴀᴛᴜʀᴇ ɪs ᴇxᴄʟᴜsɪᴠᴇ ꜰᴏʀ sᴜᴅᴏ ᴜsᴇʀs.\nᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ ᴛᴏ ᴜɴʟᴏᴄᴋ!", show_alert=True)
            
    elif query.data.startswith("imdb_setgs"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        settings = await get_settings(int(grp_id))
        btn = [[
            InlineKeyboardButton('sᴇᴛ ɪᴍᴅʙ ᴛᴇᴍᴘʟᴀᴛᴇ', callback_data=f'set_imdb#{grp_id}', style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('ᴅᴇꜰᴀᴜʟᴛ ɪᴍᴅʙ ᴛᴇᴍᴘʟᴀᴛᴇ', callback_data=f'default_imdb#{grp_id}', style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data=f'back_setgs#{grp_id}', style=enums.ButtonStyle.DANGER)
        ]]
        await query.message.edit(f'<b>⚙️ sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴏᴘᴛɪᴏɴ\n\n📝 ᴄᴜʀʀᴇɴᴛ ᴛᴇᴍᴘʟᴀᴛᴇ:</b>\n<code>{settings["template"]}</code>', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("set_imdb"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        m = await query.message.edit('<b>📝 sᴇɴᴅ ɪᴍᴅʙ ᴛᴇᴍᴘʟᴀᴛᴇ ᴡɪᴛʜ ꜰᴏʀᴍᴀᴛs:</b>')
        msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id)
        btn = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data=f'imdb_setgs#{grp_id}', style=enums.ButtonStyle.DANGER)
        ]]
        if not msg:
            await m.delete()
            return await query.message.reply('<b>⏱ ᴛɪᴍᴇᴏᴜᴛ!</b>', reply_markup=InlineKeyboardMarkup(btn))
        await save_group_settings(int(grp_id), 'template', msg.text)
        await m.delete()
        await query.message.reply('<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ᴛᴇᴍᴘʟᴀᴛᴇ!</b>', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("default_imdb"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        await save_group_settings(int(grp_id), 'template', script.IMDB_TEMPLATE)
        btn = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data=f'imdb_setgs#{grp_id}', style=enums.ButtonStyle.DANGER)
        ]]
        await query.message.edit('<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ᴛᴇᴍᴘʟᴀᴛᴇ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ!</b>', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("welcome_setgs"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        settings = await get_settings(int(grp_id))
        btn = [[
            InlineKeyboardButton('sᴇᴛ ᴡᴇʟᴄᴏᴍᴇ', callback_data=f'set_welcome#{grp_id}', style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('ᴅᴇꜰᴀᴜʟᴛ ᴡᴇʟᴄᴏᴍᴇ', callback_data=f'default_welcome#{grp_id}', style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data=f'back_setgs#{grp_id}', style=enums.ButtonStyle.DANGER)
        ]]
        await query.message.edit(f'<b>⚙️ sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴏᴘᴛɪᴏɴ\n\n📝 ᴄᴜʀʀᴇɴᴛ ᴡᴇʟᴄᴏᴍᴇ:</b>\n<code>{settings["welcome_text"]}</code>', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("set_welcome"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        m = await query.message.edit('<b>📝 sᴇɴᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ ꜰᴏʀᴍᴀᴛs:</b>')
        msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id)
        btn = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data=f'welcome_setgs#{grp_id}', style=enums.ButtonStyle.DANGER)
        ]]
        if not msg:
            await m.delete()
            return await query.message.reply('<b>⏱ ᴛɪᴍᴇᴏᴜᴛ!</b>', reply_markup=InlineKeyboardMarkup(btn))
        await save_group_settings(int(grp_id), 'welcome_text', msg.text)
        await m.delete()
        await query.message.reply('<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ!</b>', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("default_welcome"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        await save_group_settings(int(grp_id), 'welcome_text', script.WELCOME_TEXT)
        btn = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data=f'welcome_setgs#{grp_id}', style=enums.ButtonStyle.DANGER)
        ]]
        await query.message.edit('<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ!</b>', reply_markup=InlineKeyboardMarkup(btn))

    
    elif query.data.startswith("tutorial_setgs"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        settings = await get_settings(int(grp_id))
        btn = [[
            InlineKeyboardButton('sᴇᴛ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ', callback_data=f'set_tutorial#{grp_id}', style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('ᴅᴇꜰᴀᴜʟᴛ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ', callback_data=f'default_tutorial#{grp_id}', style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data=f'back_setgs#{grp_id}', style=enums.ButtonStyle.DANGER)
        ]]
        await query.message.edit(f'<b>⚙️ sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴏᴘᴛɪᴏɴ\n\n📝 ᴄᴜʀʀᴇɴᴛ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ:</b>\n<code>{settings["tutorial"]}</code>', reply_markup=InlineKeyboardMarkup(btn), link_preview_options=LinkPreviewOptions(is_disabled=True))
        
    elif query.data.startswith("set_tutorial"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        m = await query.message.edit('<b>📝 sᴇɴᴅ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ:</b>')
        msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id)
        btn = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data=f'tutorial_setgs#{grp_id}', style=enums.ButtonStyle.DANGER)
        ]]
        if not msg:
            await m.delete()
            return await query.message.reply('<b>⏱ ᴛɪᴍᴇᴏᴜᴛ!</b>', reply_markup=InlineKeyboardMarkup(btn))
        await save_group_settings(int(grp_id), 'tutorial', msg.text)
        await m.delete()
        await query.message.reply('<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ!</b>', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("default_tutorial"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        await save_group_settings(int(grp_id), 'tutorial', TUTORIAL)
        btn = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data=f'tutorial_setgs#{grp_id}', style=enums.ButtonStyle.DANGER)
        ]]
        await query.message.edit('<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ!</b>', reply_markup=InlineKeyboardMarkup(btn))

    
    elif query.data.startswith("shortlink_setgs"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        settings = await get_settings(int(grp_id))
        btn = [[
            InlineKeyboardButton('sᴇᴛ sʜᴏʀᴛʟɪɴᴋ', callback_data=f'set_shortlink#{grp_id}', style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('ᴅᴇꜰᴀᴜʟᴛ sʜᴏʀᴛʟɪɴᴋ', callback_data=f'default_shortlink#{grp_id}', style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data=f'back_setgs#{grp_id}', style=enums.ButtonStyle.DANGER)
        ]]
        await query.message.edit(f'<b>⚙️ sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴏᴘᴛɪᴏɴ\n\n📝 ᴄᴜʀʀᴇɴᴛ sʜᴏʀᴛʟɪɴᴋ:</b>\n<code>{settings["url"]} - {settings["api"]}</code>', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("set_shortlink"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
            
        btn = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data=f'shortlink_setgs#{grp_id}', style=enums.ButtonStyle.DANGER)
        ]]
        
        m = await query.message.edit(
            '<b>📝 sᴛᴇᴘ 1: sᴇɴᴅ ʏᴏᴜʀ sʜᴏʀᴛʟɪɴᴋ ᴅᴏᴍᴀɪɴ</b>\n\n'
            '💡 <i>ᴇxᴀᴍᴘʟᴇ: shareus.io (ᴅᴏ ɴᴏᴛ ᴀᴅᴅ https://)</i>\n'
            '⚠️ ᴅᴏ ɴᴏᴛ sᴇɴᴅ ᴛʜᴇ ᴀᴘɪ ᴋᴇʏ ʜᴇʀᴇ, ᴊᴜsᴛ ᴛʜᴇ ᴡᴇʙsɪᴛᴇ ʟɪɴᴋ.',
            reply_markup=InlineKeyboardMarkup(btn)
        )
        url_msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id)
        if not url_msg:
            await m.delete()
            return await query.message.reply('<b>⏱ ᴛɪᴍᴇᴏᴜᴛ!</b>', reply_markup=InlineKeyboardMarkup(btn))
            
        shortener_url = url_msg.text.strip().lower()
        if shortener_url.startswith("https://"):
            shortener_url = shortener_url.replace("https://", "")
        elif shortener_url.startswith("http://"):
            shortener_url = shortener_url.replace("http://", "")
        if shortener_url.endswith("/"):
            shortener_url = shortener_url[:-1]

        await m.delete()
        
        k = await query.message.reply(
            '<b>📝 sᴛᴇᴘ 2: sᴇɴᴅ ʏᴏᴜʀ ᴀᴘɪ ᴋᴇʏ</b>\n\n'
            '💡 <i>ʏᴏᴜ ᴄᴀɴ ꜰɪɴᴅ ᴛʜɪs ɪɴ ʏᴏᴜʀ sʜᴏʀᴛᴇɴᴇʀ ᴅᴀsʜʙᴏᴀʀᴅ (ᴜsᴜᴀʟʟʏ ᴜɴᴅᴇʀ ᴛᴏᴏʟs ➔ ᴅᴇᴠᴇʟᴏᴘᴇʀs ᴀᴘɪ).</i>',
            reply_markup=InlineKeyboardMarkup(btn)
        )
        key_msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id)
        if not key_msg:
            await k.delete()
            return await query.message.reply('<b>⏱ ᴛɪᴍᴇᴏᴜᴛ!</b>', reply_markup=InlineKeyboardMarkup(btn))
            
        api_key = key_msg.text.strip()
        await k.delete()
        
        test_msg = await query.message.reply('<b>⏳ ᴠᴇʀɪꜰʏɪɴɢ ʏᴏᴜʀ sʜᴏʀᴛʟɪɴᴋ ᴀᴘɪ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>')
        
        try:
            from shortzy import Shortzy
            from info import LOG_CHANNEL
            import logging
            
            shortzy = Shortzy(api_key=api_key, base_site=shortener_url)
            test_link = await shortzy.convert("https://telegram.me/infinity_botzz")
            
            if test_link:
                await save_group_settings(int(grp_id), 'url', shortener_url)
                await save_group_settings(int(grp_id), 'api', api_key)
                await test_msg.edit('<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴠᴇʀɪꜰɪᴇᴅ ᴀɴᴅ ᴜᴘᴅᴀᴛᴇᴅ sʜᴏʀᴛʟɪɴᴋ!</b>', reply_markup=InlineKeyboardMarkup(btn))
                
                try:
                    grp_chat = await client.get_chat(int(grp_id))
                    log_text = (
                        "<b>🔗 #ɴᴇᴡ_ɢʀᴏᴜᴘ_sʜᴏʀᴛʟɪɴᴋ</b>\n"
                        "<code>━━━━━━━━━━━━━━━━━━</code>\n"
                        f"👤 <b>ᴀᴅᴍɪɴ:</b> {query.from_user.mention}\n"
                        f"👥 <b>ɢʀᴏᴜᴘ:</b> {grp_chat.title}\n"
                        f"🆔 <b>ɢʀᴏᴜᴘ ɪᴅ:</b> <code>{grp_id}</code>\n"
                        f"🌐 <b>ᴅᴏᴍᴀɪɴ:</b> <code>{shortener_url}</code>\n"
                        f"🔑 <b>ᴀᴘɪ ᴋᴇʏ:</b> <code>{api_key[:6]}••••••••{api_key[-4:]}</code>\n"
                        "<code>━━━━━━━━━━━━━━━━━━</code>"
                    )
                    await client.send_message(LOG_CHANNEL, log_text)
                except Exception as log_err:
                    logging.getLogger(__name__).error(f"Failed to log shortlink: {log_err}")
                    
        except Exception as e:
            error_text = (
                f"<b>❌ ᴀᴘɪ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ꜰᴀɪʟᴇᴅ!</b>\n\n"
                f"<b>⚠️ ʀᴇᴀsᴏɴ:</b> <code>{str(e)}</code>\n\n"
                f"<i>ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ɪꜰ ʏᴏᴜʀ ᴜʀʟ ᴀɴᴅ ᴀᴘɪ ᴋᴇʏ ᴀʀᴇ ᴄᴏʀʀᴇᴄᴛ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ. ɪꜰ ᴛʜᴇ ɪssᴜᴇ ᴘᴇʀsɪsᴛs, ᴄᴏɴᴛᴀᴄᴛ <a href='https://t.me/talk_mrs_bot'>sᴜᴘᴘᴏʀᴛ ᴀᴅᴍɪɴ</a>.</i>"
            )
            await test_msg.edit(error_text, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)

    elif query.data.startswith("default_shortlink"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        await save_group_settings(int(grp_id), 'url', SHORTLINK_URL)
        await save_group_settings(int(grp_id), 'api', SHORTLINK_API)
        btn = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data=f'shortlink_setgs#{grp_id}', style=enums.ButtonStyle.DANGER)
        ]]
        await query.message.edit('<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ sʜᴏʀᴛʟɪɴᴋ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ!</b>', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("caption_setgs"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        settings = await get_settings(int(grp_id))
        btn = [[
            InlineKeyboardButton('sᴇᴛ ᴄᴀᴘᴛɪᴏɴ', callback_data=f'set_caption#{grp_id}', style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('ᴅᴇꜰᴀᴜʟᴛ ᴄᴀᴘᴛɪᴏɴ', callback_data=f'default_caption#{grp_id}', style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data=f'back_setgs#{grp_id}', style=enums.ButtonStyle.DANGER)
        ]]
        await query.message.edit(f'<b>⚙️ sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴏᴘᴛɪᴏɴ\n\n📝 ᴄᴜʀʀᴇɴᴛ ᴄᴀᴘᴛɪᴏɴ:</b>\n<code>{settings["caption"]}</code>', reply_markup=InlineKeyboardMarkup(btn))
        
        
    elif query.data.startswith("set_caption"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        m = await query.message.edit('<b>📝 sᴇɴᴅ ᴄᴀᴘᴛɪᴏɴ ᴡɪᴛʜ ꜰᴏʀᴍᴀᴛs:</b>')
        msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id)
        btn = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data=f'caption_setgs#{grp_id}', style=enums.ButtonStyle.DANGER)
        ]]
        if not msg:
            await m.delete()
            return await query.message.reply('<b>⏱ ᴛɪᴍᴇᴏᴜᴛ!</b>', reply_markup=InlineKeyboardMarkup(btn))
        await save_group_settings(int(grp_id), 'caption', msg.text)
        await m.delete()
        await query.message.reply('<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ᴄᴀᴘᴛɪᴏɴ!</b>', reply_markup=InlineKeyboardMarkup(btn))


    elif query.data.startswith("default_caption"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        await save_group_settings(int(grp_id), 'caption', script.FILE_CAPTION)
        btn = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data=f'caption_setgs#{grp_id}', style=enums.ButtonStyle.DANGER)
        ]]
        await query.message.edit('<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ᴄᴀᴘᴛɪᴏɴ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ!</b>', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("back_setgs"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        btn = await get_grp_stg(int(grp_id))
        chat = await client.get_chat(int(grp_id))
        await query.message.edit(text=f"<b>⚙️ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ꜰᴏʀ: {chat.title}</b>", reply_markup=InlineKeyboardMarkup(btn))

    elif query.data == "open_group_settings":
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, query.message.chat.id, userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        btn = await get_grp_stg(query.message.chat.id)
        await query.message.edit(text=f"<b>⚙️ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ꜰᴏʀ: {query.message.chat.title}</b>", reply_markup=InlineKeyboardMarkup(btn))

    elif query.data == "open_pm_settings":
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, query.message.chat.id, userid):
            return await query.answer("⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!", show_alert=True)
        btn = await get_grp_stg(query.message.chat.id)
        try:
            await client.send_message(query.from_user.id, f"<b>⚙️ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ꜰᴏʀ: {query.message.chat.title}</b>", reply_markup=InlineKeyboardMarkup(btn))
        except:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start=settings_{query.message.chat.id}")
        btn = [[
            InlineKeyboardButton('ɢᴏ ᴛᴏ ᴘᴍ', url=f"https://t.me/{temp.U_NAME}", style=enums.ButtonStyle.PRIMARY)
        ]]
        await query.message.edit("<b>✅ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ᴘᴍ!</b>", reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("delete"):
        _, query_ = query.data.split("_", 1)
        await query.message.edit('<b>🗑 ᴅᴇʟᴇᴛɪɴɢ...</b>')
        deleted = await delete_files(query_)
        await query.message.edit(f'<b>✅ ᴅᴇʟᴇᴛᴇᴅ {deleted} ꜰɪʟᴇs ɪɴ ʏᴏᴜʀ ᴅᴀᴛᴀʙᴀsᴇ ꜰᴏʀ ǫᴜᴇʀʏ <code>{query_}</code>.</b>')
     
    elif query.data.startswith("send_all"):
        if not await is_premium(query.from_user.id, client):
            return await query.answer("💎 ᴏɴʟʏ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ᴄᴀɴ ᴜsᴇ 'sᴇɴᴅ ᴀʟʟ' ꜰᴇᴀᴛᴜʀᴇ!\n\n👉 ᴛʏᴘᴇ /plan ᴛᴏ ᴜᴘɢʀᴀᴅᴇ.", show_alert=True)
        ident, key, req = query.data.split("#")
        if int(req) != query.from_user.id:
            return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀs ʀᴇsᴜʟᴛs!", show_alert=True)        
        files = temp.FILES.get(key)
        if not files:
            await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ɴᴇᴡ ʀᴇǫᴜᴇsᴛ!", show_alert=True)
            return        
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=all_{query.message.chat.id}_{key}")

    elif query.data == "clear_normal_fsub":
        await db.update_bot_sttgs('FORCE_SUB_CHANNELS', "")
        await query.message.edit("<b>✅ ɴᴏʀᴍᴀʟ ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs ᴄʟᴇᴀʀᴇᴅ.</b>")

    elif query.data == "clear_request_fsub":
        await db.update_bot_sttgs('REQUEST_FORCE_SUB_CHANNELS', "")
        await query.message.edit("<b>✅ ʀᴇǫᴜᴇsᴛ ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs ᴄʟᴇᴀʀᴇᴅ.</b>")
        
    elif query.data == "clear_all_fsub":
        await db.update_bot_sttgs('FORCE_SUB_CHANNELS', "")
        await db.update_bot_sttgs('REQUEST_FORCE_SUB_CHANNELS', "")
        await query.message.edit("<b>🗑️ ᴀʟʟ ꜰsᴜʙ sᴇᴛᴛɪɴɢs ʜᴀᴠᴇ ʙᴇᴇɴ ᴄʟᴇᴀʀᴇᴅ.</b>")

    elif query.data == "unmute_all_members":
        if not await is_check_admin(client, query.message.chat.id, query.from_user.id):
            await query.answer("⚠️ ᴛʜɪs ɪs ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ!", show_alert=True)
            return
        users_id = []
        await query.message.edit("<b>⏳ ᴜɴᴍᴜᴛᴇ ᴀʟʟ sᴛᴀʀᴛᴇᴅ! ᴛʜɪs ᴘʀᴏᴄᴇss ᴍᴀʏ ᴛᴀᴋᴇ sᴏᴍᴇ ᴛɪᴍᴇ...</b>")
        try:
            async for member in client.get_chat_members(query.message.chat.id, filter=enums.ChatMembersFilter.RESTRICTED):
                users_id.append(member.user.id)
            for user_id in users_id:
                await client.unban_chat_member(query.message.chat.id, user_id)
        except Exception as e:
            await query.message.delete()
            await query.message.reply(f'<b>❌ sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ.\n\n<code>{e}</code></b>')
            return
        await query.message.delete()
        if users_id:
            await query.message.reply(f"<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴜɴᴍᴜᴛᴇᴅ <code>{len(users_id)}</code> ᴜsᴇʀs.</b>")
        else:
            await query.message.reply('<b>⚠️ ɴᴏ ᴜsᴇʀs ᴛᴏ ᴜɴᴍᴜᴛᴇ.</b>')

    elif query.data == "unban_all_members":
        if not await is_check_admin(client, query.message.chat.id, query.from_user.id):
            await query.answer("⚠️ ᴛʜɪs ɪs ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ!", show_alert=True)
            return
        users_id = []
        await query.message.edit("<b>⏳ ᴜɴʙᴀɴ ᴀʟʟ sᴛᴀʀᴛᴇᴅ! ᴛʜɪs ᴘʀᴏᴄᴇss ᴍᴀʏ ᴛᴀᴋᴇ sᴏᴍᴇ ᴛɪᴍᴇ...</b>")
        try:
            async for member in client.get_chat_members(query.message.chat.id, filter=enums.ChatMembersFilter.BANNED):
                users_id.append(member.user.id)
            for user_id in users_id:
                await client.unban_chat_member(query.message.chat.id, user_id)
        except Exception as e:
            await query.message.delete()
            await query.message.reply(f'<b>❌ sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ.\n\n<code>{e}</code></b>')
            return
        await query.message.delete()
        if users_id:
            await query.message.reply(f"<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴜɴʙᴀɴɴᴇᴅ <code>{len(users_id)}</code> ᴜsᴇʀs.</b>")
        else:
            await query.message.reply('<b>⚠️ ɴᴏ ᴜsᴇʀs ᴛᴏ ᴜɴʙᴀɴ.</b>')

    elif query.data == "kick_muted_members":
        if not await is_check_admin(client, query.message.chat.id, query.from_user.id):
            await query.answer("⚠️ ᴛʜɪs ɪs ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ!", show_alert=True)
            return
        users_id = []
        await query.message.edit("<b>⏳ ᴋɪᴄᴋ ᴍᴜᴛᴇᴅ ᴜsᴇʀs sᴛᴀʀᴛᴇᴅ! ᴛʜɪs ᴘʀᴏᴄᴇss ᴍᴀʏ ᴛᴀᴋᴇ sᴏᴍᴇ ᴛɪᴍᴇ...</b>")
        try:
            async for member in client.get_chat_members(query.message.chat.id, filter=enums.ChatMembersFilter.RESTRICTED):
                users_id.append(member.user.id)
            for user_id in users_id:
                await client.ban_chat_member(query.message.chat.id, user_id, datetime.now() + timedelta(seconds=30))
        except Exception as e:
            await query.message.delete()
            await query.message.reply(f'<b>❌ sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ.\n\n<code>{e}</code></b>')
            return
        await query.message.delete()
        if users_id:
            await query.message.reply(f"<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴋɪᴄᴋᴇᴅ ᴍᴜᴛᴇᴅ <code>{len(users_id)}</code> ᴜsᴇʀs.</b>")
        else:
            await query.message.reply('<b>⚠️ ɴᴏ ᴍᴜᴛᴇᴅ ᴜsᴇʀs ᴛᴏ ᴋɪᴄᴋ.</b>')

    elif query.data == "kick_deleted_accounts_members":
        if not await is_check_admin(client, query.message.chat.id, query.from_user.id):
            await query.answer("⚠️ ᴛʜɪs ɪs ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ!", show_alert=True)
            return
        users_id = []
        await query.message.edit("<b>⏳ ᴋɪᴄᴋ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs sᴛᴀʀᴛᴇᴅ! ᴛʜɪs ᴘʀᴏᴄᴇss ᴍᴀʏ ᴛᴀᴋᴇ sᴏᴍᴇ ᴛɪᴍᴇ...</b>")
        try:
            async for member in client.get_chat_members(query.message.chat.id):
                if member.user.is_deleted:
                    users_id.append(member.user.id)
            for user_id in users_id:
                await client.ban_chat_member(query.message.chat.id, user_id, datetime.now() + timedelta(seconds=30))
        except Exception as e:
            await query.message.delete()
            await query.message.reply(f'<b>❌ sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ.\n\n<code>{e}</code></b>')
            return
        await query.message.delete()
        if users_id:
            await query.message.reply(f"<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴋɪᴄᴋᴇᴅ ᴅᴇʟᴇᴛᴇᴅ <code>{len(users_id)}</code> ᴀᴄᴄᴏᴜɴᴛs.</b>")
        else:
            await query.message.reply('<b>⚠️ ɴᴏ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs ᴛᴏ ᴋɪᴄᴋ.</b>')