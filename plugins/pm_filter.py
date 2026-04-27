import asyncio
import re
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
from database.ia_filterdb import get_search_results,delete_files, db_count_documents, second_db_count_documents
from plugins.commands import get_grp_stg

BUTTONS = {}
CAP = {}


@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_search(client, message):
    if message.text.startswith("/"):
        return
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        pass

    stg = await db.get_bot_sttgs()
    if await is_premium(message.from_user.id, client):
        s = await message.reply(f"<b><i>🔎 `{message.text}` sᴇᴀʀᴄʜɪɴɢ...</i></b>", quote=True)
        await auto_filter(client, message, s)

    else:
        if stg and stg.get('PM_SEARCH'):
            s = await message.reply(f"<b><i>🔎 `{message.text}` sᴇᴀʀᴄʜɪɴɢ...</i></b>", quote=True)
            await auto_filter(client, message, s)
            
        else:
            files, n_offset, total = await get_search_results(message.text)
            
            if int(total) != 0:
                btn = [[
                    InlineKeyboardButton("🗂 ᴄʟɪᴄᴋ ʜᴇʀᴇ 🗂", url=FILMS_LINK, style=enums.ButtonStyle.PRIMARY)
                ],[
                    InlineKeyboardButton('💎 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss 💎', url=f"https://t.me/{temp.U_NAME}?start=premium", style=enums.ButtonStyle.SUCCESS)
                ]]
                reply_markup = InlineKeyboardMarkup(btn)
                
                await message.reply_text(
                    f'<b><i>🤗 ᴛᴏᴛᴀʟ <code>{total}</code> ʀᴇsᴜʟᴛs ꜰᴏᴜɴᴅ 👇</i></b>\n\n'
                    f'<b>ᴊᴏɪɴ ᴏᴜʀ ᴍᴀɪɴ ɢʀᴏᴜᴘ ᴏʀ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ ᴛᴏ ɢᴇᴛ ꜰɪʟᴇs ᴅɪʀᴇᴄᴛʟʏ ɪɴ ᴘᴍ!</b>', 
                    reply_markup=reply_markup
                )
            

@Client.on_message(filters.group & filters.text & filters.incoming)
async def group_search(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message and message.from_user else 0
    stg = await db.get_bot_sttgs()
    if stg and stg.get('AUTO_FILTER'):
        if not user_id:
            await message.reply("<b>⚠️ ɪ ᴀᴍ ɴᴏᴛ ᴡᴏʀᴋɪɴɢ ꜰᴏʀ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴs!</b>")
            return
        if message.chat.id == SUPPORT_GROUP:
            files, offset, total = await get_search_results(message.text)
            if files:
                btn = [[
                    InlineKeyboardButton("Here", url=FILMS_LINK, style=enums.ButtonStyle.PRIMARY)
                ]]
                await message.reply_text(f'<b>📊 ᴛᴏᴛᴀʟ <code>{total}</code> ʀᴇsᴜʟᴛs ꜰᴏᴜɴᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>', reply_markup=InlineKeyboardMarkup(btn))
            return
            
        if message.text.startswith("/"):
            return
            
        elif '@admin' in message.text.lower() or '@admins' in message.text.lower():
            if await is_check_admin(client, message.chat.id, message.from_user.id):
                return
            admins = []
            async for member in client.get_chat_members(chat_id=message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                if not member.user.is_bot:
                    admins.append(member.user.id)
                    if member.status == enums.ChatMemberStatus.OWNER:
                        if message.reply_to_message:
                            try:
                                sent_msg = await message.reply_to_message.forward(member.user.id)
                                await sent_msg.reply_text(f"<b>#Attention</b>\n★ <b>User:</b> {message.from_user.mention}\n★ <b>Group:</b> {message.chat.title}\n\n★ <a href={message.reply_to_message.link}><b>Go to message</b></a>", link_preview_options=LinkPreviewOptions(is_disabled=True))
                            except:
                                pass
                        else:
                            try:
                                sent_msg = await message.forward(member.user.id)
                                await sent_msg.reply_text(f"<b>#Attention</b>\n★ <b>User:</b> {message.from_user.mention}\n★ <b>Group:</b> {message.chat.title}\n\n★ <a href={message.link}><b>Go to message</b></a>", link_preview_options=LinkPreviewOptions(is_disabled=True))
                            except:
                                pass
            hidden_mentions = (f'[\u2064](tg://user?id={user_id})' for user_id in admins)
            await message.reply_text('<b>✅ ʀᴇᴘᴏʀᴛ sᴇɴᴛ!</b>' + ''.join(hidden_mentions))
            return

        elif re.findall(r'https?://\S+|www\.\S+|t\.me/\S+|@\w+', message.text):
            if await is_check_admin(client, message.chat.id, message.from_user.id):
                return
            await message.delete()
            return await message.reply('<b>⚠️ ʟɪɴᴋs ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ʜᴇʀᴇ!</b>')
        
        elif '#request' in message.text.lower():
            if message.from_user.id in ADMINS:
                return
            await client.send_message(LOG_CHANNEL, f"<b>#Request</b>\n★ <b>User:</b> {message.from_user.mention}\n★ <b>Group:</b> {message.chat.title}\n\n★ <b>Message:</b> {re.sub(r'#request', '', message.text.lower())}")
            await message.reply_text("<b>✅ ʀᴇǫᴜᴇsᴛ sᴇɴᴛ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>")
            return  
        else:
            s = await message.reply(f"<b><i>🔎 `{message.text}` sᴇᴀʀᴄʜɪɴɢ...</i></b>")
            await auto_filter(client, message, s)
    else:
        k = await message.reply_text('<b>❌ ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ ɪs ᴏꜰꜰ!</b>')
        await asyncio.sleep(5)
        await k.delete()
        try:
            await message.delete()
        except:
            pass

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀs ʀᴇsᴜʟᴛs!", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    cap = CAP.get(key)
    if not search:
        await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ɴᴇᴡ ʀᴇǫᴜᴇsᴛ!", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    temp.FILES[key] = files
    settings = await get_settings(query.message.chat.id)
    del_msg = f"\n\n<b><blockquote>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</blockquote></b>" if settings["auto_delete"] else ''
    files_link = ''

    if settings['links']:
        btn = []
        for file_num, file in enumerate(files, start=offset+1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file['_id']}>[{get_size(file['file_size'])}] {file['file_name']}</a></b>"""
    else:
        btn = [[
            InlineKeyboardButton(text=f"{get_size(file['file_size'])} - {file['file_name']}", callback_data=f"file#{file['_id']}")
        ]
            for file in files
        ]
    if settings['shortlink'] and not await is_premium(query.from_user.id, bot):
        btn.insert(0,
            [InlineKeyboardButton("📰 ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}#{req}#{offset}"),
            InlineKeyboardButton("🔍 ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{key}#{req}#{offset}")]
        )
        btn.insert(1,
            [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", url=await get_shortlink(settings['url'], settings['api'], f'https://t.me/{temp.U_NAME}?start=all_{query.message.chat.id}_{key}'))]
        )
    else:
        btn.insert(0,
            [InlineKeyboardButton("📰 ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}#{req}#{offset}"),
            InlineKeyboardButton("🔍 ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{key}#{req}#{offset}")]
        )
        btn.insert(1,
            [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=f"send_all#{key}#{req}")]
        )

    if 0 < offset <= MAX_BTN:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - MAX_BTN
        
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}", style=enums.ButtonStyle.PRIMARY),
             InlineKeyboardButton(f"{math.ceil(int(offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"{math.ceil(int(offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"next_{req}_{key}_{n_offset}", style=enums.ButtonStyle.PRIMARY)])
    else:
        btn.append(
            [
                InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}", style=enums.ButtonStyle.PRIMARY),
                InlineKeyboardButton(f"{math.ceil(int(offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
                InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"next_{req}_{key}_{n_offset}", style=enums.ButtonStyle.PRIMARY)
            ]
        )
    #btn.append(
    #    [InlineKeyboardButton('💎 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss 💎', url=f"https://t.me/{temp.U_NAME}?start=premium")]
    #)
    await query.message.edit_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), link_preview_options=LinkPreviewOptions(is_disabled=True), parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"^languages"))
async def languages_(client: Client, query: CallbackQuery):
    _, key, req, offset = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀs ʀᴇsᴜʟᴛs!", show_alert=True)
    btn = [
        [InlineKeyboardButton(text=LANGUAGES[i].title(), callback_data=f"lang_search#{LANGUAGES[i]}#{key}#{offset}#{req}"),
         InlineKeyboardButton(text=LANGUAGES[i+1].title(), callback_data=f"lang_search#{LANGUAGES[i+1]}#{key}#{offset}#{req}")]
        for i in range(0, len(LANGUAGES)-1, 2)
    ]
    btn.append([InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{offset}", style=enums.ButtonStyle.PRIMARY)])  
    await query.message.edit_text("<b>ɪɴ ᴡʜɪᴄʜ ʟᴀɴɢᴜᴀɢᴇ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ, sᴇʟᴇᴄᴛ ʜᴇʀᴇ 👇</b>", link_preview_options=LinkPreviewOptions(is_disabled=True), reply_markup=InlineKeyboardMarkup(btn))

@Client.on_callback_query(filters.regex(r"^quality"))
async def quality(client: Client, query: CallbackQuery):
    _, key, req, offset = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀs ʀᴇsᴜʟᴛs!", show_alert=True)
    btn = [
        [InlineKeyboardButton(text=QUALITY[i].title(), callback_data=f"qual_search#{QUALITY[i]}#{key}#{offset}#{req}"),
         InlineKeyboardButton(text=QUALITY[i+1].title(), callback_data=f"qual_search#{QUALITY[i+1]}#{key}#{offset}#{req}")]
        for i in range(0, len(QUALITY)-1, 2)
    ]
    btn.append([InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{offset}", style=enums.ButtonStyle.PRIMARY)])  
    await query.message.edit_text("<b>ɪɴ ᴡʜɪᴄʜ ǫᴜᴀʟɪᴛʏ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ, sᴇʟᴇᴄᴛ ʜᴇʀᴇ 👇</b>", link_preview_options=LinkPreviewOptions(is_disabled=True), reply_markup=InlineKeyboardMarkup(btn))

@Client.on_callback_query(filters.regex(r"^lang_search"))
async def filter_languages_cb_handler(client: Client, query: CallbackQuery):
    _, lang, key, offset, req = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀs ʀᴇsᴜʟᴛs!", show_alert=True)

    search = BUTTONS.get(key)
    cap = CAP.get(key)
    if not search:
        await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ɴᴇᴡ ʀᴇǫᴜᴇsᴛ!", show_alert=True)
        return 

    files, l_offset, total_results = await get_search_results(search, lang=lang)
    if not files:
        await query.answer(f"sᴏʀʀʏ '{lang.title()}' ʟᴀɴɢᴜᴀɢᴇ ꜰɪʟᴇs ɴᴏᴛ ꜰᴏᴜɴᴅ 😕", show_alert=1)
        return
    temp.FILES[key] = files
    settings = await get_settings(query.message.chat.id)
    del_msg = f"\n\n<b><blockquote>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</blockquote></b>" if settings["auto_delete"] else ''
    files_link = ''

    if settings['links']:
        btn = []
        for file_num, file in enumerate(files, start=1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file['_id']}>[{get_size(file['file_size'])}] {file['file_name']}</a></b>"""
    else:
        btn = [[
            InlineKeyboardButton(text=f"{get_size(file['file_size'])} - {file['file_name']}", callback_data=f"file#{file['_id']}")
        ]
            for file in files
        ]
    if settings['shortlink'] and not await is_premium(query.from_user.id, client):
        btn.insert(0,
            [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", url=await get_shortlink(settings['url'], settings['api'], f'https://t.me/{temp.U_NAME}?start=all_{query.message.chat.id}_{key}')),
            InlineKeyboardButton("🔍 ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{key}#{req}#{offset}")]
        )
    else:
        btn.insert(0,
            [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", callback_data=f"send_all#{key}#{req}"),
            InlineKeyboardButton("🔍 ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{key}#{req}#{offset}")]
        )
    
    if l_offset != "":
        btn.append(
            [InlineKeyboardButton(text=f"1/{math.ceil(int(total_results) / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton(text="ɴᴇxᴛ »", callback_data=f"lang_next#{req}#{key}#{lang}#{l_offset}#{offset}", style=enums.ButtonStyle.PRIMARY)]
        )
    btn.append([InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{offset}", style=enums.ButtonStyle.PRIMARY)])
    await query.message.edit_text(cap + files_link + del_msg, link_preview_options=LinkPreviewOptions(is_disabled=True), reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"^lang_next"))
async def lang_next_page(bot, query):
    ident, req, key, lang, l_offset, offset = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀs ʀᴇsᴜʟᴛs!", show_alert=True)
    try:
        l_offset = int(l_offset)
    except:
        l_offset = 0
    search = BUTTONS.get(key)
    cap = CAP.get(key)
    settings = await get_settings(query.message.chat.id)
    del_msg = f"\n\n<b><blockquote>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</blockquote></b>" if settings["auto_delete"] else ''
    if not search:
        await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ɴᴇᴡ ʀᴇǫᴜᴇsᴛ!", show_alert=True)
        return
    files, n_offset, total = await get_search_results(search, offset=l_offset, lang=lang)
    if not files:
        return
    temp.FILES[key] = files
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0
    files_link = ''
    if settings['links']:
        btn = []
        for file_num, file in enumerate(files, start=l_offset+1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file['_id']}>[{get_size(file['file_size'])}] {file['file_name']}</a></b>"""
    else:
        btn = [[
            InlineKeyboardButton(text=f"{get_size(file['file_size'])} - {file['file_name']}", callback_data=f'file#{file["_id"]}')
        ]
            for file in files
        ]
    if settings['shortlink'] and not await is_premium(query.from_user.id, bot):
        btn.insert(1,
            [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", url=await get_shortlink(settings['url'], settings['api'], f'https://t.me/{temp.U_NAME}?start=all_{query.message.chat.id}_{key}')),
            InlineKeyboardButton("🔍 ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{key}#{req}#{l_offset}")]
        )
    else:
        btn.insert(1,
            [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", callback_data=f"send_all#{key}#{req}"),
            InlineKeyboardButton("🔍 ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{key}#{req}#{l_offset}")]
        )
    if 0 < l_offset <= MAX_BTN:
        b_offset = 0
    elif l_offset == 0:
        b_offset = None
    else:
        b_offset = l_offset - MAX_BTN
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"lang_next#{req}#{key}#{lang}#{b_offset}#{offset}", style=enums.ButtonStyle.PRIMARY),
             InlineKeyboardButton(f"{math.ceil(int(l_offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"lang_next#{req}#{key}#{lang}#{n_offset}#{offset}", style=enums.ButtonStyle.PRIMARY)]
        )
    elif b_offset is None:
        btn.append(
            [InlineKeyboardButton(f"{math.ceil(int(l_offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"lang_next#{req}#{key}#{lang}#{n_offset}#{offset}", style=enums.ButtonStyle.PRIMARY)]
        )
    else:
        btn.append(
            [InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"lang_next#{req}#{key}#{lang}#{b_offset}#{offset}", style=enums.ButtonStyle.PRIMARY),
             InlineKeyboardButton(f"{math.ceil(int(l_offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"lang_next#{req}#{key}#{lang}#{n_offset}#{offset}", style=enums.ButtonStyle.PRIMARY)]
        )
    btn.append([InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{offset}", style=enums.ButtonStyle.PRIMARY)])
    await query.message.edit_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), link_preview_options=LinkPreviewOptions(is_disabled=True), parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"^qual_search"))
async def quality_search(client: Client, query: CallbackQuery):
    _, qual, key, offset, req = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀs ʀᴇsᴜʟᴛs!", show_alert=True)
    search = BUTTONS.get(key)
    cap = CAP.get(key)
    if not search:
        await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ɴᴇᴡ ʀᴇǫᴜᴇsᴛ!", show_alert=True)
        return
    files, l_offset, total_results = await get_search_results(search, lang=qual)
    if not files:
        await query.answer(f"sᴏʀʀʏ '{qual.title()}' ʟᴀɴɢᴜᴀɢᴇ ꜰɪʟᴇs ɴᴏᴛ ꜰᴏᴜɴᴅ 😕", show_alert=1)
        return
    temp.FILES[key] = files
    settings = await get_settings(query.message.chat.id)
    del_msg = f"\n\n<b><blockquote>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</blockquote></b>" if settings["auto_delete"] else ''
    files_link = ''
    if settings['links']:
        btn = []
        for file_num, file in enumerate(files, start=1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file['_id']}>[{get_size(file['file_size'])}] {file['file_name']}</a></b>"""
    else:
        btn = [[
            InlineKeyboardButton(text=f"{get_size(file['file_size'])} - {file['file_name']}", callback_data=f'file#{file["_id"]}')
        ]
            for file in files
        ]
    if settings['shortlink'] and not await is_premium(query.from_user.id, client):
        btn.insert(0,
            [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", url=await get_shortlink(settings['url'], settings['api'], f'https://t.me/{temp.U_NAME}?start=all_{query.message.chat.id}_{key}'))]
        )
    else:
        btn.insert(0,
            [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", callback_data=f"send_all#{key}#{req}")]
        )  
    if l_offset != "":
        btn.append(
            [InlineKeyboardButton(text=f"1/{math.ceil(int(total_results) / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton(text="ɴᴇxᴛ »", callback_data=f"qual_next#{req}#{key}#{qual}#{l_offset}#{offset}", style=enums.ButtonStyle.PRIMARY)]
        )
    btn.append([InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{offset}", style=enums.ButtonStyle.PRIMARY)])
    await query.message.edit_text(cap + files_link + del_msg, link_preview_options=LinkPreviewOptions(is_disabled=True), reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"^qual_next"))
async def quality_next_page(bot, query):
    ident, req, key, qual, l_offset, offset = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀs ʀᴇsᴜʟᴛs!", show_alert=True)
    try:
        l_offset = int(l_offset)
    except:
        l_offset = 0
    search = BUTTONS.get(key)
    cap = CAP.get(key)
    settings = await get_settings(query.message.chat.id)
    del_msg = f"\n\n<b><blockquote>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</blockquote></b>" if settings["auto_delete"] else ''
    if not search:
        await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ɴᴇᴡ ʀᴇǫᴜᴇsᴛ!", show_alert=True)
        return
    files, n_offset, total = await get_search_results(search, offset=l_offset, lang=qual)
    if not files:
        return
    temp.FILES[key] = files
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0
    files_link = ''
    if settings['links']:
        btn = []
        for file_num, file in enumerate(files, start=l_offset+1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file['_id']}>[{get_size(file['file_size'])}] {file['file_name']}</a></b>"""
    else:
        btn = [[
            InlineKeyboardButton(text=f"{get_size(file['file_size'])} - {file['file_name']}", callback_data=f'file#{file["_id"]}')
        ]
            for file in files
        ]
    if settings['shortlink'] and not await is_premium(query.from_user.id, bot):
        btn.insert(0,
            [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", url=await get_shortlink(settings['url'], settings['api'], f'https://t.me/{temp.U_NAME}?start=all_{query.message.chat.id}_{key}'))]
        )
    else:
        btn.insert(0,
            [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", callback_data=f"send_all#{key}#{req}")]
        )
    if 0 < l_offset <= MAX_BTN:
        b_offset = 0
    elif l_offset == 0:
        b_offset = None
    else:
        b_offset = l_offset - MAX_BTN
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"qual_next#{req}#{key}#{qual}#{b_offset}#{offset}", style=enums.ButtonStyle.PRIMARY),
             InlineKeyboardButton(f"{math.ceil(int(l_offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons")]
        )
    elif b_offset is None:
        btn.append(
            [InlineKeyboardButton(f"{math.ceil(int(l_offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"qual_next#{req}#{key}#{qual}#{n_offset}#{offset}", style=enums.ButtonStyle.PRIMARY)]
        )
    else:
        btn.append(
            [InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"qual_next#{req}#{key}#{qual}#{b_offset}#{offset}", style=enums.ButtonStyle.PRIMARY),
             InlineKeyboardButton(f"{math.ceil(int(l_offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"qual_next#{req}#{key}#{qual}#{n_offset}#{offset}", style=enums.ButtonStyle.PRIMARY)]
        )
    btn.append([InlineKeyboardButton(text="⪻ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ ᴘᴀɢᴇ", callback_data=f"next_{req}_{key}_{offset}", style=enums.ButtonStyle.PRIMARY)])
    await query.message.edit_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), link_preview_options=LinkPreviewOptions(is_disabled=True), parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    data = query.data.split('#')
    user = int(data[2])
    if user != 0 and query.from_user.id != user:
        return await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀs ʀᴇsᴜʟᴛs!", show_alert=True)

    if data[1] == "dbmatch":
        search = query.message.reply_markup.inline_keyboard[0][0].text.replace("✨ ", "")
    else:
        movie = await get_poster(data[1], id=True)
        search = movie.get('title')

    s = await query.message.edit_text(f"<b><i>🔍 <code>{search}</code> ᴄʜᴇᴄᴋɪɴɢ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ...</i></b>")
    await query.answer('')
    
    files, offset, total_results = await get_search_results(search)
    if files:
        k = (search, files, offset, total_results)
        if not query.message:
            return await query.answer("ᴍᴇssᴀɢᴇ ᴇxᴘɪʀᴇᴅ! sᴇᴀʀᴄʜ ᴀɢᴀɪɴ.", show_alert=True)
        await auto_filter(bot, query, s, spoll=k)
    else:
        k = await query.message.edit(
            text=f"<b>👋 ʜᴇʟʟᴏ {query.from_user.mention},\n\nɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ '{search}' ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ. 😔</b>",
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
        asyncio.create_task(bot.send_message(LOG_CHANNEL, f"<b>#No_Result</b>\n★ <b>Requester:</b> {query.from_user.mention}\n★ <b>Content:</b> {search}"))
        
        await asyncio.sleep(60)
        await k.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

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
  
    if query.data.startswith("file"):
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
        settings = await get_settings(int(mc.split("_", 2)[1]))
        btn = await is_subscribed(client, query)
        if btn:
            await query.answer(f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.", show_alert=True)
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
            #InlineKeyboardButton('🔎 ɪɴʟɪɴᴇ', switch_inline_query_current_chat=''),
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
        m = await query.message.edit('<b>📝 sᴇɴᴅ sʜᴏʀᴛʟɪɴᴋ ᴜʀʟ:</b>')
        url_msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id)
        if not url_msg:
            await m.delete()
            return await query.message.reply('<b>⏱ ᴛɪᴍᴇᴏᴜᴛ!</b>', reply_markup=InlineKeyboardMarkup(btn))
        await m.delete()
        k = await query.message.reply('<b>📝 sᴇɴᴅ sʜᴏʀᴛʟɪɴᴋ ᴀᴘɪ ᴋᴇʏ:</b>')
        key_msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id)
        if not key_msg:
            await m.delete()
            return await query.message.reply('<b>⏱ ᴛɪᴍᴇᴏᴜᴛ!</b>', reply_markup=InlineKeyboardMarkup(btn))
        await save_group_settings(int(grp_id), 'url', url_msg.text)
        await save_group_settings(int(grp_id), 'api', key_msg.text)
        await k.delete()
        await query.message.reply('<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ sʜᴏʀᴛʟɪɴᴋ!</b>', reply_markup=InlineKeyboardMarkup(btn))

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


async def auto_filter(client, msg, s, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        search = re.sub(r"\s+", " ", re.sub(r"[-:\"';!]", " ", message.text)).strip()
        files, offset, total_results = await get_search_results(search)
        if not files:
            if settings["spell_check"]:
                return await advantage_spell_chok(message, s)
            else:
                return await s.edit(f"<b>ɪ ᴄᴀɴ'ᴛ ꜰɪɴᴅ '{search}'</b>")
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message if msg.message.reply_to_message else msg.message
        search, files, offset, total_results = spoll

    if not message or message is None:
        if isinstance(msg, CallbackQuery):
            await msg.answer("ᴏʟᴅ ᴍᴇssᴀɢᴇ! sᴇᴀʀᴄʜ ᴀɢᴀɪɴ.", show_alert=True)
        return await s.edit("<b>❌ ᴇʀʀᴏʀ: ᴏʀɪɢɪɴᴀʟ ᴍᴇssᴀɢᴇ ɴᴏᴛ ꜰᴏᴜɴᴅ.</b>")

    req = message.from_user.id if message.from_user else 0
    
    try:
        chat_id = message.chat.id
        msg_id = message.id
        key = f"{chat_id}-{msg_id}"
    except AttributeError:
        key = f"{msg.message.chat.id}-{msg.message.id}"
 
    temp.FILES[key] = files
    BUTTONS[key] = search
    files_link = ""
    if settings['links']:
        btn = []
        for file_num, file in enumerate(files, start=1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{message.chat.id}_{file['_id']}>[{get_size(file['file_size'])}] {file['file_name']}</a></b>"""
    else:
        btn = [[
            InlineKeyboardButton(text=f"{get_size(file['file_size'])} - {file['file_name']}", callback_data=f'file#{file["_id"]}')
        ]
            for file in files
        ]   
    if offset != "":
        if settings['shortlink'] and not await is_premium(message.from_user.id, client):
            btn.insert(0,
                [InlineKeyboardButton("📰 ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}#{req}#{offset}"),
                InlineKeyboardButton("🔍 ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{key}#{req}#{offset}")]
            )
            btn.insert(1,
                [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", url=await get_shortlink(settings['url'], settings['api'], f'https://t.me/{temp.U_NAME}?start=all_{message.chat.id}_{key}'))]
            )
        else:
            btn.insert(0,
                [InlineKeyboardButton("📰 ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}#{req}#{offset}"),
                InlineKeyboardButton("🔍 ǫᴜᴀʟɪᴛʏ", callback_data=f"quality#{key}#{req}#{offset}")]
            )
            btn.insert(1,
                [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=f"send_all#{key}#{req}")]
            )
        btn.append(
            [InlineKeyboardButton(text=f"1/{math.ceil(int(total_results) / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton(text="ɴᴇxᴛ »", callback_data=f"next_{req}_{key}_{offset}", style=enums.ButtonStyle.PRIMARY)]
        )
    else:
        if settings['shortlink'] and not await is_premium(message.from_user.id, client):
            btn.insert(0,
                [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", url=await get_shortlink(settings['url'], settings['api'], f'https://t.me/{temp.U_NAME}?start=all_{message.chat.id}_{key}'))]
            )
        else:
            btn.insert(0,
                [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", callback_data=f"send_all#{key}#{req}")]
            )
    #btn.append(
    #    [InlineKeyboardButton('💎 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss 💎', url=f"https://t.me/{temp.U_NAME}?start=premium")]
    #)
    imdb = await get_poster(search, file=(files[0])['file_name']) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            kind=imdb['kind'],
            votes=imdb['votes'],
            tmdb_id=imdb["tmdb_id"],
            runtime=imdb["runtime"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            languages=imdb['languages'],
            countries=imdb['countries'],
            **locals()
        )
    else:
        cap = f"<b>💭 ʜᴇʏ {message.from_user.mention},\n♻️ ʜᴇʀᴇ ɪ ꜰᴏᴜɴᴅ ꜰᴏʀ ʏᴏᴜʀ sᴇᴀʀᴄʜ {search}...</b>"
    CAP[key] = cap
    del_msg = f"\n\n<b><blockquote>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</blockquote></b>" if settings["auto_delete"] else ''
    if imdb and imdb.get('poster'):
        await s.delete()
        try:
            k = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024] + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML, quote=True)
            if settings["auto_delete"]:
                await asyncio.sleep(DELETE_TIME)
                await k.delete()
                try:
                    await message.delete()
                except:
                    pass
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            k = await message.reply_photo(photo=poster, caption=cap[:1024] + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML, quote=True)
            if settings["auto_delete"]:
                await asyncio.sleep(DELETE_TIME)
                await k.delete()
                try:
                    await message.delete()
                except:
                    pass
        except Exception as e:
            k = await message.reply_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), link_preview_options=LinkPreviewOptions(is_disabled=True), parse_mode=enums.ParseMode.HTML, quote=True)
            if settings["auto_delete"]:
                await asyncio.sleep(DELETE_TIME)
                await k.delete()
                try:
                    await message.delete()
                except:
                    pass
    else:
        k = await s.edit_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), link_preview_options=LinkPreviewOptions(is_disabled=True), parse_mode=enums.ParseMode.HTML)
        if settings["auto_delete"]:
            await asyncio.sleep(DELETE_TIME)
            await k.delete()
            try:
                await message.delete()
            except:
                pass

async def advantage_spell_chok(message, s):
    search = message.text
    google_search = search.replace(" ", "+")
    user_id = message.from_user.id if message.from_user else 0
    
    btn = [[
        InlineKeyboardButton("⚠️ ɪɴsᴛʀᴜᴄᴛɪᴏɴs", callback_data='instructions'),
        InlineKeyboardButton("🔎 sᴇᴀʀᴄʜ ɢᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={google_search}")
    ],[
        InlineKeyboardButton("🛸 ʀᴇǫᴜᴇsᴛ ᴍᴏᴠɪᴇ", callback_data=f"request_msg_{user_id}")
    ]]

    try:
        movies = await get_poster(search, bulk=True)
    except:
        movies = None
        
    if not movies:
        all_titles = await db.get_all_movie_titles()
        matches = process.extractBests(search, all_titles, score_cutoff=60, limit=5)
        
        if matches:
            db_btns = [[
                InlineKeyboardButton(text=f"✨ {match[0]}", callback_data=f"spolling#dbmatch#{user_id}#{match[0][:20]}")
            ] for match in matches]
            db_btns.extend(btn)
            
            return await s.edit_text(
                text=f"<b>👋 ʜᴇʏ {message.from_user.mention},\n\nɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ '{search}' ᴅɪʀᴇᴄᴛʟʏ.\nᴅɪᴅ ʏᴏᴜ ᴍᴇᴀɴ ᴏɴᴇ ᴏꜰ ᴛʜᴇsᴇ ꜰʀᴏᴍ ᴍʏ ʟɪʙʀᴀʀʏ? 👇</b>",
                reply_markup=InlineKeyboardMarkup(db_btns),
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )

        n = await s.edit_text(
            text=script.NOT_FILE_TXT.format(message.from_user.mention, search), 
            reply_markup=InlineKeyboardMarkup(btn),
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
        asyncio.create_task(temp.BOT.send_message(LOG_CHANNEL, f"<b>#No_Result</b>\n★ <b>User:</b> {message.from_user.mention}\n★ <b>Search:</b> {search}"))
        await asyncio.sleep(60)
        await n.delete()
        try: await message.delete()
        except: pass
        return

    buttons = [[
        InlineKeyboardButton(text=f"🎬 {movie.get('title')}", callback_data=f"spolling#{movie['id']}#{user_id}")
    ] for movie in movies]
    
    buttons.append([InlineKeyboardButton("🚫 ᴄʟᴏsᴇ 🚫", callback_data="close_data", style=enums.ButtonStyle.DANGER)])
    
    suggestion_msg = await s.edit_text(
        text=f"<b>👋 ʜᴇʟʟᴏ {message.from_user.mention},\n\nɪ ꜰᴏᴜɴᴅ sᴏᴍᴇ sɪᴍɪʟᴀʀ ᴛɪᴛʟᴇs. sᴇʟᴇᴄᴛ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ᴏɴᴇ: 👇</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
    
    await asyncio.sleep(300)
    try:
        await suggestion_msg.delete()
        await message.delete()
    except:
        pass