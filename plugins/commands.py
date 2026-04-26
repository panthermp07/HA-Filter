import os
import random
import string
import asyncio
from datetime import datetime, timedelta
from time import monotonic
from time import time as time_now
from Script import script
from database.users_chats_db import db
from pyrogram import Client, filters, enums
from utils import is_premium, upload_image, get_settings, get_size, is_subscribed, is_check_admin, get_shortlink, get_verify_status, update_verify_status, save_group_settings, temp, get_readable_time, get_wish, get_seconds
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions, WebAppInfo
from database.ia_filterdb import db_count_documents, second_db_count_documents, get_file_details, delete_files
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from info import OWNER_USERNAME, IS_PREMIUM, PRE_DAY_AMOUNT, RECEIPT_SEND_USERNAME, URL, BIN_CHANNEL, SECOND_FILES_DATABASE_URL, INDEX_CHANNELS, ADMINS, IS_VERIFY, VERIFY_TUTORIAL, VERIFY_EXPIRE, SHORTLINK_API, SHORTLINK_URL, DELETE_TIME, SUPPORT_LINK, UPDATES_LINK, LOG_CHANNEL, PICS, IS_STREAM, REACTIONS, PM_FILE_DELETE_TIME, PREMIUM_NOTIFY_CHANNEL, VERIFICATION_NOTIFY_CHANNEL

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            username = f'@{message.chat.username}' if message.chat.username else 'Private'
            await client.send_message(LOG_CHANNEL, script.NEW_GROUP_TXT.format(message.chat.title, message.chat.id, username, total))       
            await db.add_chat(message.chat.id, message.chat.title)
        wish = get_wish()
        user = message.from_user.mention if message.from_user else "Dear"
        btn = [[
            InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ', url=UPDATES_LINK, style=enums.ButtonStyle.PRIMARY),
            InlineKeyboardButton('🛠️ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url=SUPPORT_LINK, style=enums.ButtonStyle.PRIMARY)
        ]]
        
        await message.reply(text=f"<b>ʜᴇʏ {user}, <i>{wish}</i>\n\nɪ ᴀᴍ ᴀʟɪᴠᴇ ᴀɴᴅ ʀᴇᴀᴅʏ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ. sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴍᴏᴠɪᴇ ɴᴀᴍᴇ!</b>", 
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return 
        
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        await message.react(emoji="⚡️", big=True)

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.NEW_USER_TXT.format(message.from_user.mention, message.from_user.id))

    verify_status = await get_verify_status(message.from_user.id)
    if verify_status['is_verified'] and datetime.now() > verify_status['expire_time']:
        await update_verify_status(message.from_user.id, is_verified=False)
    if (len(message.command) != 2) or (len(message.command) == 2 and message.command[1] == 'start'):
        buttons = [[
            InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀᴛ ➕", url=f'http://t.me/{temp.U_NAME}?startgroup=start', style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇs', url=UPDATES_LINK),
            InlineKeyboardButton('🛠️ sᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
        ],[
            InlineKeyboardButton('👨‍🚒 ʜᴇʟᴘ ɢᴜɪᴅᴇ', callback_data='help'),
            #InlineKeyboardButton('🔎 sᴇᴀʀᴄʜ ɪɴʟɪɴᴇ', switch_inline_query_current_chat=''),
            InlineKeyboardButton('📚 ᴀʙᴏᴜᴛ ʙᴏᴛ', callback_data='about')
        ],[
            InlineKeyboardButton('💎 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss 💎', url=f"https://t.me/{temp.U_NAME}?start=premium")
        ],[
            InlineKeyboardButton('🌐 ᴍɪɴɪ ᴡᴇʙᴀᴘᴘ ɴᴇᴛᴡᴏʀᴋ 🌐', style=enums.ButtonStyle.SUCCESS, web_app=WebAppInfo(url=URL))
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, get_wish()),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return

    mc = message.command[1]

    if mc == 'premium':
        return await plan(client, message)
    
    if mc.startswith('settings'):
        _, group_id = message.command[1].split("_")
        if not await is_check_admin(client, (int(group_id)), message.from_user.id):
            return await message.reply("<b>❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>")
        btn = await get_grp_stg(int(group_id))
        chat = await client.get_chat(int(group_id))
        return await message.reply(f"<b>⚙️ ᴄʜᴀɴɢᴇ sᴇᴛᴛɪɴɢs ꜰᴏʀ: {chat.title}</b>", reply_markup=InlineKeyboardMarkup(btn))

    if mc.startswith('inline_fsub'):
        btn = await is_subscribed(client, message)
        if btn:
            reply_markup = InlineKeyboardMarkup(btn)
            await message.reply(f"Please join my 'Updates Channel' and use inline search. 👍",
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            return 

    if mc.startswith('verify'):
        _, token = mc.split("_", 1)
        verify_status = (await get_verify_status(message.from_user.id)).copy()
        if verify_status['verify_token'] != token:
            return await message.reply("<b>❌ ʏᴏᴜʀ ᴠᴇʀɪꜰʏ ᴛᴏᴋᴇɴ ɪs ɪɴᴠᴀʟɪᴅ!</b>")
        expiry_time = datetime.now() + timedelta(seconds=VERIFY_EXPIRE)
        await update_verify_status(message.from_user.id, is_verified=True, expire_time=expiry_time)
        
        if VERIFICATION_NOTIFY_CHANNEL:
            try:
                date_str = datetime.now().strftime('%d %B %Y')
                await client.send_message(
                    VERIFICATION_NOTIFY_CHANNEL,
                    f"[♻️ ᴜsᴇʀ ᴠᴇʀɪꜰɪᴇᴅ ✓]</b>\n\n"
                    f"👤 <b>ɴᴀᴍᴇ:</b> {message.from_user.first_name}\n"
                    f"🆔 <b>ᴜsᴇʀ ɪᴅ:</b> <code>{message.from_user.id}</code>\n"
                    f"📅 <b>ᴅᴀᴛᴇ:</b> {date_str}\n\n"
                    f"<b>#ᴍᴏᴠɪᴇs_ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ_ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b>"
                )
            except Exception as e:
                print(f"Verification Notify Error: {e}")

        if verify_status["link"] == "":
            reply_markup = None
        else:
            btn = [[InlineKeyboardButton("📌 ɢᴇᴛ ꜰɪʟᴇ ɴᴏᴡ 📌", url=f'https://t.me/{temp.U_NAME}?start={verify_status["link"]}', style=enums.ButtonStyle.PRIMARY)]]
            reply_markup = InlineKeyboardMarkup(btn)
            
        await message.reply(f"<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴠᴇʀɪꜰɪᴇᴅ ᴜɴᴛɪʟ: {get_readable_time(VERIFY_EXPIRE)}</b>", reply_markup=reply_markup, protect_content=True)
        return
    
    verify_status = await get_verify_status(message.from_user.id)
    
    if IS_VERIFY and not verify_status['is_verified'] and not await is_premium(message.from_user.id, client):
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        await update_verify_status(message.from_user.id, verify_token=token, link="" if mc == 'inline_verify' else mc)
        link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://t.me/{temp.U_NAME}?start=verify_{token}')
        btn = [[
            InlineKeyboardButton("🧿 ᴠᴇʀɪꜰʏ ɴᴏᴡ 🧿", url=link, style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('🗳 ᴛᴜᴛᴏʀɪᴀʟ ɢᴜɪᴅᴇ 🗳', url=VERIFY_TUTORIAL, style=enums.ButtonStyle.PRIMARY)
        ]]
        
        await message.reply(
            text="<b>🔒 ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ!\n\nʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪꜰɪᴇᴅ ꜰᴏʀ ᴛᴏᴅᴀʏ. ᴋɪɴᴅʟʏ ᴠᴇʀɪꜰʏ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ ᴀɴᴅ ᴜɴʟᴏᴄᴋ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛᴇᴅ ᴄᴏɴᴛᴇɴᴛ.</b>", 
            reply_markup=InlineKeyboardMarkup(btn), 
            protect_content=True
        )
        return

    btn = await is_subscribed(client, message)
    if btn:
        btn.append(
            [InlineKeyboardButton("🔁 ᴛʀʏ ᴀɢᴀɪɴ 🔁", callback_data=f"checksub#{mc}", style=enums.ButtonStyle.PRIMARY)]
        )
        reply_markup = InlineKeyboardMarkup(btn)
        
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=(
                f"<b>👋 ʜᴇʏ {message.from_user.mention},\n\n"
                f"ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ. ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ 'ᴛʀʏ ᴀɢᴀɪɴ' ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ. 😇</b>"
            ),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
        
    if mc.startswith('all'):
        _, grp_id, key = mc.split("_", 2)
        files = temp.FILES.get(key)
        if not files:
            return await message.reply('No Such All Files Exist!')
        settings = await get_settings(int(grp_id))
        file_ids = []
        total_files = await message.reply(f"<b><i>🗂 Total files - <code>{len(files)}</code></i></b>")
        for file in files:
            CAPTION = settings['caption']
            f_caption = CAPTION.format(
                file_name=file['file_name'],
                file_size=get_size(file['file_size']),
                file_caption=file['caption']
            )      
            if IS_STREAM:
                btn = [[
                    InlineKeyboardButton("⚡ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ ⚡", callback_data=f"stream#{file['_id']}", style=enums.ButtonStyle.PRIMARY)
                ],[
                    InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇs', url=UPDATES_LINK),
                    InlineKeyboardButton('🛠️ sᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
                ],[
                    InlineKeyboardButton('⁉️ ᴄʟᴏsᴇ ⁉️', callback_data='close_data', style=enums.ButtonStyle.DANGER)
                ]]
            else:
                btn = [[
                    InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇs', url=UPDATES_LINK),
                    InlineKeyboardButton(' 🛠️ sᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
                ],[
                    InlineKeyboardButton('⁉️ ᴄʟᴏsᴇ ⁉️', callback_data='close_data', style=enums.ButtonStyle.DANGER)
                ]]

            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file['_id'],
                caption=f_caption,
                protect_content=False,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            file_ids.append(msg.id)
            await asyncio.sleep(0.5)
        await asyncio.sleep(1.5)

        time_str = get_readable_time(PM_FILE_DELETE_TIME)
        vp = await message.reply(f"<b>⚠️ ɴᴏᴛᴇ:</b> ᴛʜᴇsᴇ ꜰɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ <b>{time_str}</b> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛs. ᴘʟᴇᴀsᴇ ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ sᴏᴍᴇᴡʜᴇʀᴇ ᴇʟsᴇ.")
        
        await asyncio.sleep(PM_FILE_DELETE_TIME)
        buttons = [[InlineKeyboardButton('ɢᴇᴛ ꜰɪʟᴇs ᴀɢᴀɪɴ', callback_data=f"get_del_send_all_files#{grp_id}#{key}")]] 
        await client.delete_messages(
            chat_id=message.chat.id,
            message_ids=file_ids + [total_files.id]
        )
        await vp.edit("<b>❌ ᴛʜᴇ ꜰɪʟᴇs ʜᴀᴠᴇ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ!</b>\nᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ᴛʜᴇᴍ ᴀɢᴀɪɴ.", reply_markup=InlineKeyboardMarkup(buttons))
        return

    parts = mc.split("_", 2)
    type_ = parts[0]
    grp_id = parts[1] if len(parts) == 3 else 0
    file_id = parts[-1]
    files_ = await get_file_details(file_id)
    if not files_:
        return await message.reply('ɴᴏ sᴜᴄʜ ꜰɪʟᴇ ᴇxɪsᴛs!')
    files = files_
    settings = await get_settings(int(grp_id))
    if type_ != 'shortlink' and settings['shortlink'] and not await is_premium(message.from_user.id, client):
        link = await get_shortlink(settings['url'], settings['api'], f"https://t.me/{temp.U_NAME}?start=shortlink_{grp_id}_{file_id}")
        btn = [[
            InlineKeyboardButton("💎 ɢᴇᴛ ꜰɪʟᴇ(s)", url=link, style=enums.ButtonStyle.SUCCESS)
        ],[
            InlineKeyboardButton("🚀 ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ 🚀", url=settings['tutorial'], style=enums.ButtonStyle.PRIMARY)
        ]]
        await message.reply(f"[{get_size(files['file_size'])}] {files['file_name']}\n\nYour file is ready, Please get using this link. 👍", reply_markup=InlineKeyboardMarkup(btn), protect_content=True)
        return
            
    CAPTION = settings['caption']
    f_caption = CAPTION.format(
        file_name = files['file_name'],
        file_size = get_size(files['file_size']),
        file_caption=files['caption']
    )
    if IS_STREAM:
        btn = [[
            InlineKeyboardButton("⚡ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ ⚡", callback_data=f"stream#{file_id}", style=enums.ButtonStyle.PRIMARY)
        ],[
            InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇs', url=UPDATES_LINK),
            InlineKeyboardButton('🛠️ sᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
        ],[
            InlineKeyboardButton('⁉️ ᴄʟᴏsᴇ ⁉️', callback_data='close_data', style=enums.ButtonStyle.DANGER)
        ]]
    else:
        btn = [[
            InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇs', url=UPDATES_LINK),
            InlineKeyboardButton('🛠️ sᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
        ],[
            InlineKeyboardButton('⁉️ ᴄʟᴏsᴇ ⁉️', callback_data='close_data', style=enums.ButtonStyle.DANGER)
        ]]
        
    vp = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=False,
        reply_markup=InlineKeyboardMarkup(btn)
    )
    await asyncio.sleep(1.0)
    
    time_str = get_readable_time(PM_FILE_DELETE_TIME)
    msg = await vp.reply(f"<b>⚠️ ɴᴏᴛᴇ:</b> ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ <b>{time_str}</b> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛs. ᴘʟᴇᴀsᴇ ꜰᴏʀᴡᴀʀᴅ ɪᴛ sᴏᴍᴇᴡʜᴇʀᴇ ᴇʟsᴇ.")
    
    await asyncio.sleep(PM_FILE_DELETE_TIME)
    btns = [[
        InlineKeyboardButton('ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ', callback_data=f"get_del_file#{grp_id}#{file_id}", style=enums.ButtonStyle.SUCCESS)
    ]]
    await msg.delete()
    await vp.delete()
    await vp.reply("<b>❌ ᴛʜᴇ ꜰɪʟᴇ ʜᴀs ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ!</b>\nᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ɪᴛ ᴀɢᴀɪɴ.", reply_markup=InlineKeyboardMarkup(btns))


@Client.on_message(filters.command('link'))
async def link(bot, message):
    msg = message.reply_to_message
    if not msg:
        return await message.reply('<b>⚠️ ᴀʟᴇʀᴛ: ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇᴅɪᴀ ꜰɪʟᴇ.</b>')
    
    try:
        media = getattr(msg, msg.media.value)
        file_name = getattr(media, 'file_name', 'Streaming File')
        bin_msg = await bot.send_cached_media(chat_id=BIN_CHANNEL, file_id=media.file_id)
        watch = f"{URL}watch/{bin_msg.id}"
        download = f"{URL}download/{bin_msg.id}"

        btn = [[
                InlineKeyboardButton("🎬 ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ", url=watch, style=enums.ButtonStyle.PRIMARY),
                InlineKeyboardButton("🚀 ꜰᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ", url=download, style=enums.ButtonStyle.PRIMARY)
            ],[
                InlineKeyboardButton('🚫 ᴄʟᴏsᴇ ᴍᴇɴᴜ 🚫', callback_data='close_data', style=enums.ButtonStyle.DANGER)
            ]]
        
        caption_text = (
            f"✅ <b>ʏᴏᴜʀ ʟɪɴᴋs ᴀʀᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ!</b>\n\n"
            f"📦 <b>ꜰɪʟᴇ:</b> <code>{file_name}</code>\n\n"
            f"🌍 <b><a href='https://t.me/infinity_botzz'>@ɪɴꜰɪɴɪᴛʏ_ʙᴏᴛᴢᴢ</a></b>"
        )
        await message.reply_text(
            text=caption_text,
            reply_markup=InlineKeyboardMarkup(btn),
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply(f'<b>❌ ᴇʀʀᴏʀ: {e}</b>')

@Client.on_message(filters.command('index_channels'))
async def channels_info(bot, message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.delete()
        return
    ids = INDEX_CHANNELS
    if not ids:
        return await message.reply("Not set INDEX_CHANNELS")
    text = '**Indexed Channels:**\n\n'
    for id in ids:
        chat = await bot.get_chat(id)
        text += f'{chat.title}\n'
    text += f'\n**Total:** {len(ids)}'
    await message.reply(text)

@Client.on_message(filters.command('stats') & filters.user(ADMINS))
async def stats(bot, message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.delete()
        return

    files = db_count_documents()
    users = await db.total_users_count()
    chats = await db.total_chat_count()
    prm = db.get_premium_count()
    used_files_db_size = get_size(await db.get_files_db_size())
    used_data_db_size = get_size(await db.get_data_db_size())  # Added this back!

    if SECOND_FILES_DATABASE_URL:
        secnd_files_db_used_size = get_size(await db.get_second_files_db_size())
        secnd_files = second_db_count_documents()
    else:
        secnd_files_db_used_size = '-'
        secnd_files = '-'

    uptime = get_readable_time(time_now() - temp.START_TIME)
    await message.reply_text(
        script.STATUS_TXT.format(
            users, 
            prm, 
            chats, 
            used_data_db_size, 
            files, 
            used_files_db_size, 
            secnd_files, 
            secnd_files_db_used_size, 
            uptime
        )
    )

async def get_grp_stg(group_id):
    settings = await get_settings(group_id)
    btn = [[
        InlineKeyboardButton('ᴇᴅɪᴛ ɪᴍᴅʙ ᴛᴇᴍᴘʟᴀᴛᴇ', callback_data=f'imdb_setgs#{group_id}')
    ],[
        InlineKeyboardButton('ᴇᴅɪᴛ sʜᴏʀᴛʟɪɴᴋ', callback_data=f'shortlink_setgs#{group_id}')
    ],[
        InlineKeyboardButton('ᴇᴅɪᴛ ꜰɪʟᴇ ᴄᴀᴘᴛɪᴏɴ', callback_data=f'caption_setgs#{group_id}')
    ],[
        InlineKeyboardButton('ᴇᴅɪᴛ ᴡᴇʟᴄᴏᴍᴇ', callback_data=f'welcome_setgs#{group_id}')
    ],[
        InlineKeyboardButton('ᴇᴅɪᴛ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ', callback_data=f'tutorial_setgs#{group_id}')
    ],[
        InlineKeyboardButton(f'ɪᴍᴅʙ ᴘᴏsᴛᴇʀ {"✅" if settings["imdb"] else "❌"}', callback_data=f'bool_setgs#imdb#{settings["imdb"]}#{group_id}')
    ],[
        InlineKeyboardButton(f'sᴘᴇʟʟɪɴɢ ᴄʜᴇᴄᴋ {"✅" if settings["spell_check"] else "❌"}', callback_data=f'bool_setgs#spell_check#{settings["spell_check"]}#{group_id}')
    ],[
        InlineKeyboardButton(f"ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ - {get_readable_time(DELETE_TIME)}" if settings["auto_delete"] else "ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ❌", callback_data=f'bool_setgs#auto_delete#{settings["auto_delete"]}#{group_id}')
    ],[
        InlineKeyboardButton(f'ᴡᴇʟᴄᴏᴍᴇ {"✅" if settings["welcome"] else "❌"}', callback_data=f'bool_setgs#welcome#{settings["welcome"]}#{group_id}')
    ],[
        InlineKeyboardButton(f'sʜᴏʀᴛʟɪɴᴋ {"✅" if settings["shortlink"] else "❌"}', callback_data=f'bool_setgs#shortlink#{settings["shortlink"]}#{group_id}')
    ],[
        InlineKeyboardButton(f"ʀᴇsᴜʟᴛ ᴘᴀɢᴇ - ʟɪɴᴋ" if settings["links"] else "ʀᴇsᴜʟᴛ ᴘᴀɢᴇ - ʙᴜᴛᴛᴏɴ", callback_data=f'bool_setgs#links#{settings["links"]}#{group_id}')
    ]]
    return btn
    
@Client.on_message(filters.command('settings'))
async def settings(client, message):
    group_id = message.chat.id
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        if not await is_check_admin(client, group_id, message.from_user.id):
            return await message.reply_text('⚠️ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.')
        
        btn = [[
            InlineKeyboardButton("ᴏᴘᴇɴ ʜᴇʀᴇ 🔽", callback_data='open_group_settings')
        ],[
            InlineKeyboardButton("ᴏᴘᴇɴ ɪɴ ᴘᴍ 👤", callback_data='open_pm_settings')
        ]]
        await message.reply_text('⚙️ ᴡʜᴇʀᴇ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴏᴘᴇɴ ᴛʜᴇ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ?', reply_markup=InlineKeyboardMarkup(btn))
        
    elif message.chat.type == enums.ChatType.PRIVATE:
        cons = db.get_connections(message.from_user.id)
        if not cons:
            return await message.reply_text("❌ ɴᴏ ɢʀᴏᴜᴘs ꜰᴏᴜɴᴅ! ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ sᴇʟᴇᴄᴛ <b>'ᴏᴘᴇɴ ɪɴ ᴘᴍ'</b>.")
            
        buttons = []
        for con in cons:
            try:
                chat = await client.get_chat(con)
                buttons.append(
                    [InlineKeyboardButton(text=chat.title, callback_data=f'back_setgs#{chat.id}')]
                )
            except:
                pass
                
        await message.reply_text(
            text="""⚙️ sᴇʟᴇᴄᴛ ᴛʜᴇ ɢʀᴏᴜᴘ ᴡʜᴏsᴇ sᴇᴛᴛɪɴɢs ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄʜᴀɴɢᴇ.
        
        💡 <i>ɪꜰ ʏᴏᴜʀ ɢʀᴏᴜᴘ ɪs ɴᴏᴛ sʜᴏᴡɪɴɢ ʜᴇʀᴇ:</i> ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ sᴇʟᴇᴄᴛ <b>'ᴏᴘᴇɴ ɪɴ ᴘᴍ'</b>, ᴏʀ sᴇɴᴅ <code>/connect</code> ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ.""", 
            reply_markup=InlineKeyboardMarkup(buttons)
        )

@Client.on_message(filters.command('connect'))
async def connect(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id
        db.add_connect(group_id, message.from_user.id)
        await message.reply_text('Successfully connected this group to PM, now you can manage your group using /settings inside your PM')
    elif message.chat.type == enums.ChatType.PRIVATE:
        if len(message.command) > 1:
            group_id = message.command[1]
            if not await is_check_admin(client, int(group_id), message.from_user.id):
                return await message.reply_text('You not admin in this group.')
            chat = await client.get_chat(int(group_id))
            db.add_connect(int(group_id), message.from_user.id)
            await message.reply_text(f'Successfully connected {chat.title} group to PM')
        else:
            await message.reply_text('Usage: /connect group_id\nor use /connect in group')


@Client.on_message(filters.command('delete'))
async def delete_file(bot, message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.delete()
        return

    try:
        query = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("<b>💡 ᴜsᴀɢᴇ: <code>/delete query</code></b>")

    btn = [
        [
            InlineKeyboardButton("✅ ʏᴇs, ᴅᴇʟᴇᴛᴇ ᴀʟʟ", callback_data=f"delete_{query}", style=enums.ButtonStyle.DANGER)
        ],
        [
            InlineKeyboardButton("❌ ᴄʟᴏsᴇ / ᴄᴀɴᴄᴇʟ", callback_data="close_data", style=enums.ButtonStyle.SUCCESS)
        ]
    ]

    await message.reply_text(
        f"<b>🗑 ᴅᴇʟᴇᴛɪᴏɴ ᴄᴏɴꜰɪʀᴍᴀᴛɪᴏɴ\n\n"
        f"ᴅᴏ ʏᴏᴜ ʀᴇᴀʟʟʏ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ꜰɪʟᴇs ᴍᴀᴛᴄʜɪɴɢ:\n"
        f"🔍 ǫᴜᴇʀʏ ⠂<code>{query}</code>\n\n"
        f"⚠️ ᴛʜɪs ᴀᴄᴛɪᴏɴ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ!</b>",
        reply_markup=InlineKeyboardMarkup(btn)
    )


@Client.on_message(filters.command('img2link'))
async def img_2_link(bot, message):
    reply_to_message = message.reply_to_message
    if not reply_to_message or not reply_to_message.photo:
        return await message.reply('<b>⚠️ ᴀʟᴇʀᴛ: ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ʟɪɴᴋ.</b>')
    
    text = await message.reply_text(text="<b>⏳ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ɪᴍᴀɢᴇ....</b>")   
    
    try:
        path = await reply_to_message.download()  
        response = upload_image(path)
        
        if not response:
            return await text.edit_text(text="<b>❌ ᴜᴘʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ! ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>")

        await text.edit_text(
            f"<b>✅ ɪᴍᴀɢᴇ ᴜᴘʟᴏᴀᴅᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ\n\n"
            f"🔗 ʟɪɴᴋ ⠂<code>{response}</code>\n\n"
            f"✨ ᴘᴏᴡᴇʀᴇᴅ ʙʏ @ɪɴꜰɪɴɪᴛʏ_ʙᴏᴛᴢᴢ</b>",
            disable_web_page_preview=True
        )
        
        if os.path.exists(path):
            os.remove(path)
            
    except Exception as e:
        await text.edit_text(f"<b>❌ ᴇʀʀᴏʀ: {e}</b>")

@Client.on_message(filters.command('ping'))
async def ping(client, message):
    start_time = monotonic()
    msg = await message.reply("👀")
    end_time = monotonic()
    await msg.edit(f'{round((end_time - start_time) * 1000)} ms')
    

@Client.on_message(filters.command('myplan') & filters.private)
async def myplan(client, message):
    if not IS_PREMIUM:
        return await message.reply('<b>⚠️ ᴀʟᴇʀᴛ: ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇ ᴅɪsᴀʙʟᴇᴅ ʙʏ ᴀᴅᴍɪɴ.</b>')
    
    user_id = message.from_user.id
    mp = db.get_plan(user_id)
    
    if not await is_premium(user_id, client):
        btn = [[
            InlineKeyboardButton('🎁 ᴀᴄᴛɪᴠᴀᴛᴇ ᴛʀɪᴀʟ', callback_data='activate_trial'),
            InlineKeyboardButton('💎 ᴀᴄᴛɪᴠᴀᴛᴇ ᴘʟᴀɴ', callback_data='activate_plan')
        ]]
        return await message.reply(
            '<b>❌ ʏᴏᴜ ᴅᴏɴᴛ ʜᴀᴠᴇ ᴀɴʏ ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ.\n\nᴘʟᴇᴀsᴇ ᴜsᴇ /plan ᴛᴏ ᴠɪᴇᴡ ᴀʟʟ ᴇxᴄʟᴜsɪᴠᴇ ꜰᴇᴀᴛᴜʀᴇs.</b>', 
            reply_markup=InlineKeyboardMarkup(btn)
        )
    
    expire_str = mp['expire'].strftime('%d %b %Y, %I:%M %p')
    
    await message.reply(
        f"<b>💎 ɪɴꜰɪɴɪᴛʏ ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs\n\n"
        f"🚀 sᴛᴀᴛᴜs: ᴀᴄᴛɪᴠᴇ\n"
        f"⏳ ᴘʟᴀɴ: {mp['plan']}\n"
        f"📅 ᴇxᴘɪʀʏ: <code>{expire_str}</code>\n\n"
        f"✨ ᴇɴᴊᴏʏ ᴀʟʟ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇs!\n"
        f"🌍 @ɪɴꜰɪɴɪᴛʏ_ʙᴏᴛᴢᴢ</b>",
        disable_web_page_preview=True
    )

@Client.on_message(filters.command('plan') & filters.private)
async def plan(client, message):
    if not IS_PREMIUM:
        return await message.reply(
            '<b>⚠️ ᴀʟᴇʀᴛ: ᴘʀᴇᴍɪᴜᴍ sᴇʀᴠɪᴄᴇs ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ᴅɪsᴀʙʟᴇᴅ ʙʏ ᴀᴅᴍɪɴ.</b>',
            disable_web_page_preview=True
        )
    btn = [[
            InlineKeyboardButton('🎁 ᴀᴄᴛɪᴠᴀᴛᴇ ꜰʀᴇᴇ ᴛʀɪᴀʟ', callback_data='activate_trial')
        ],[
            InlineKeyboardButton('💳 ᴄʜᴏᴏsᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ', callback_data='activate_plan')
        ],[
            InlineKeyboardButton('🧑‍💻 ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ', url='https://t.me/talk_mrs_bot', style=enums.ButtonStyle.PRIMARY)
        ]]

    await message.reply(
        script.PLAN_TXT.format(PRE_DAY_AMOUNT, RECEIPT_SEND_USERNAME),
        reply_markup=InlineKeyboardMarkup(btn),
        disable_web_page_preview=True,
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command('add_prm'))
async def add_prm(bot, message):
    if not db.is_sudo(message.from_user.id):
        return
    if not IS_PREMIUM:
        return await message.reply('<b>⚠️ ᴀʟᴇʀᴛ: ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇ ᴅɪsᴀʙʟᴇᴅ.</b>')
    
    if len(message.command) == 3:
        try:
            user_id = int(message.command[1])
            duration = message.command[2]        
            seconds = await get_seconds(duration)
            
            if seconds > 0:
                expiry_time = datetime.now() + timedelta(seconds=seconds)
                status = {
                    'expire': expiry_time,
                    'plan': duration,
                    'premium': True,
                    'trial': True
                }
                db.update_plan(user_id, status)
                
                try:
                    target_user = await bot.get_users(user_id)
                    target_mention = target_user.mention
                    target_name = target_user.first_name
                except:
                    target_mention = f"<code>{user_id}</code>"
                    target_name = "User"

                adder = message.from_user
                is_owner = adder.id in ADMINS
                role = "ʙᴏᴛ ᴏᴡɴᴇʀ" if is_owner else "sᴜᴅᴏ ᴀᴅᴍɪɴ"
                expiry_str = expiry_time.strftime('%d %b %Y, %I:%M %p')

                if is_owner:
                    user_msg = (
                        "🎉 <b>ʜᴇʏ {},\n\n"
                        "ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘɢʀᴀᴅᴇᴅ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ!</b>\n\n"
                        "👤 <b>ɴᴀᴍᴇ:</b> {}\n"
                        "🆔 <b>ɪᴅ:</b> <code>{}</code>\n"
                        "⏳ <b>ᴘʟᴀɴ:</b> <code>{}</code>\n"
                        "📅 <b>ᴇxᴘɪʀʏ:</b> <code>{}</code>\n\n"
                        "✨ <b>ᴇɴᴊᴏʏ ᴀʟʟ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇs!</b>"
                    ).format(target_mention, target_name, user_id, duration, expiry_str)
                else:
                    user_msg = (
                        "🎉 <b>ʜᴇʏ {},\n\n"
                        "ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ɢɪᴠᴇɴ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ʙʏ {}!</b>\n\n"
                        "⏳ <b>ᴘʟᴀɴ:</b> <code>{}</code>\n"
                        "📅 <b>ᴇxᴘɪʀʏ:</b> <code>{}</code>\n\n"
                        "✨ <b>ᴇɴᴊᴏʏ ᴀʟʟ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇs!</b>"
                    ).format(target_mention, adder.first_name, duration, expiry_str)

                try:
                    await bot.send_message(chat_id=user_id, text=user_msg)
                except:
                    pass

                full_log = (
                    "✅ <b>#ᴘʀᴇᴍɪᴜᴍ_ᴀᴅᴅᴇᴅ_sᴜᴄᴄᴇssꜰᴜʟʟʏ</b>\n\n"
                    f"👤 <b>ᴜsᴇʀ:</b> {target_mention}\n"
                    f"🆔 <b>ᴜsᴇʀ ɪᴅ:</b> <code>{user_id}</code>\n"
                    f"⏳ <b>ᴘʟᴀɴ:</b> <code>{duration}</code>\n"
                    f"📅 <b>ᴇxᴘɪʀʏ:</b> <code>{expiry_str}</code>\n"
                    f"👮 <b>ᴀᴅᴅᴇᴅ ʙʏ:</b> {adder.mention}\n"
                    f"🆔 <b>ᴀᴅᴅᴇʀ ɪᴅ:</b> <code>{adder.id}</code>\n"
                    f"🎖️ <b>ʀᴏʟᴇ:</b> <code>{role}</code>"
                )
                await message.reply_text(full_log)

                if PREMIUM_NOTIFY_CHANNEL:
                    try:
                        await bot.send_message(PREMIUM_NOTIFY_CHANNEL, full_log)
                    except:
                        pass

                if not is_owner:
                    sudo_alert = f"⚠️ <b>sᴜᴅᴏ ᴀᴄᴛɪᴠɪᴛʏ ᴀʟᴇʀᴛ!</b>\n\n{full_log}"
                    for admin_id in ADMINS:
                        try:
                            await bot.send_message(admin_id, sudo_alert)
                        except: pass
            else:
                await message.reply_text("❌ <b>ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ꜰᴏʀᴍᴀᴛ.</b>")
        except Exception as e:
            await message.reply_text(f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{e}</code>")
    else:
        await message.reply_text("📋 <b>ᴜsᴀɢᴇ:</b> <code>/add_prm user_id 7day</code>")



@Client.on_message(filters.command('rm_prm'))
async def rm_prm(bot, message):
    if not db.is_sudo(message.from_user.id):
        return
    if not IS_PREMIUM:
        return await message.reply('<b>⚠️ ᴀʟᴇʀᴛ: ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇ ᴅɪsᴀʙʟᴇᴅ.</b>')
    
    if len(message.command) == 2:
        try:
            user_id = int(message.command[1])
            try:
                target_user = await bot.get_users(user_id)
                target_mention = target_user.mention
            except:
                target_mention = f"<code>{user_id}</code>"

            adder = message.from_user
            is_owner = adder.id in ADMINS
            role = "ʙᴏᴛ ᴏᴡɴᴇʀ" if is_owner else "sᴜᴅᴏ ᴀᴅᴍɪɴ"
            
            status = {'expire': '', 'plan': '', 'premium': False, 'trial': True}
            db.update_plan(user_id, status)

            if is_owner:
                user_msg = "<b>⚠️ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ʙʏ ᴀᴅᴍɪɴ.</b>"
            else:
                user_msg = f"<b>⚠️ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ʙʏ {adder.first_name}.</b>"

            try:
                await bot.send_message(user_id, user_msg)
            except:
                pass

            report_text = (
                "🚫 <b>#ᴘʀᴇᴍɪᴜᴍ_ʀᴇᴍᴏᴠᴇᴅ</b>\n\n"
                f"👤 <b>ᴜsᴇʀ:</b> {target_mention}\n"
                f"🆔 <b>ᴜsᴇʀ ɪᴅ:</b> <code>{user_id}</code>\n"
                f"👮 <b>ʀᴇᴍᴏᴠᴇᴅ ʙʏ:</b> {adder.mention}\n"
                f"🆔 <b>ᴀᴅᴅᴇʀ ɪᴅ:</b> <code>{adder.id}</code>\n"
                f"🎖️ <b>ʀᴏʟᴇ:</b> {role}\n\n"
                f"✨ <b>sᴛᴀᴛᴜs:</b> ᴀᴄᴄᴇss ʀᴇᴠᴏᴋᴇᴅ"
            )
            await message.reply_text(report_text)

            if PREMIUM_NOTIFY_CHANNEL:
                try:
                    await bot.send_message(PREMIUM_NOTIFY_CHANNEL, report_text)
                except:
                    pass


            if not is_owner:
                sudo_alert = f"⚠️ <b>sᴜᴅᴏ ʀᴇᴍᴏᴠᴀʟ ᴀʟᴇʀᴛ!</b>\n\n{report_text}"
                for admin_id in ADMINS:
                    try:
                        await bot.send_message(admin_id, sudo_alert)
                    except: pass

        except Exception as e:
            await message.reply_text(f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{e}</code>")
    else:
        await message.reply_text("📋 <b>ᴜsᴀɢᴇ:</b> <code>/rm_prm user_id</code>")

@Client.on_message(filters.command('prm_list') & filters.user(ADMINS))
async def prm_list(bot, message):
    if not IS_PREMIUM:
        return await message.reply('<b>⚠️ ᴀʟᴇʀᴛ: ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇ ᴅɪsᴀʙʟᴇᴅ.</b>')
    
    tx = await message.reply('<b>🔍 ꜰᴇᴛᴄʜɪɴɢ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ʟɪsᴛ...</b>')
    
    premium_users = db.get_premium_users()
    pr = [i['id'] for i in premium_users if i.get('status', {}).get('premium')]
    
    if not pr:
        return await tx.edit_text('<b>❌ ɴᴏ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ꜰᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ.</b>')
    
    t = '<b>💎 ɪɴꜰɪɴɪᴛʏ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs\n\n'
    
    for count, p in enumerate(pr, 1):
        try:
            u = await bot.get_users(p)
            t += f"{count}. 👤 {u.mention} ⠂<code>{p}</code>\n"
        except:
            t += f"{count}. 🆔 <code>{p}</code>\n"
    
    t += f"\n📊 ᴛᴏᴛᴀʟ ᴜsᴇʀs: {len(pr)}</b>"

    await tx.edit_text(
        text=f"{t}\n\n🌍 <b><a href='https://t.me/infinity_botzz'>@ɪɴꜰɪɴɪᴛʏ_ʙᴏᴛᴢᴢ</a></b>",
        disable_web_page_preview=True
    )

@Client.on_message(filters.command('set_fsub') & filters.user(ADMINS))
async def set_fsub(bot, message):
    try:
        _, ids = message.text.split(' ', 1)
    except ValueError:
        return await message.reply('usage: /set_fsub -100xxx -100xxx')
    title = ""
    for id in ids.split(' '):
        try:
            chat = await bot.get_chat(int(id))
            title += f'{chat.title}\n'
        except Exception as e:
            return await message.reply(f'ERROR: {e}')
    db.update_bot_sttgs('FORCE_SUB_CHANNELS', ids)
    await message.reply(f'added force subscribe channels: {title}')

        

@Client.on_message(filters.command('set_req_fsub') & filters.user(ADMINS))
async def set_req_fsub(bot, message):
    try:
        _, id = message.text.split(' ', 1)
    except ValueError:
        return await message.reply('usage: /set_req_fsub -100xxx')
    try:
        chat = await bot.get_chat(int(id))
    except Exception as e:
        return await message.reply(f'ERROR: {e}')
    db.update_bot_sttgs('REQUEST_FORCE_SUB_CHANNELS', id)
    await message.reply(f'added request force subscribe channel: {chat.title}')

@Client.on_message(filters.command('resetallgroups') & filters.user(ADMINS))
async def reset_all_groups_cmd(client, message):
    msg = await message.reply("<b>⏳ ʀᴇsᴇᴛᴛɪɴɢ ᴀʟʟ ɢʀᴏᴜᴘs sᴇᴛᴛɪɴɢs ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ...</b>")
    try:
        modified_count = db.reset_all_groups_settings()
        
        await msg.edit(
            f"<b>✅ sᴜᴄᴄᴇss!</b>\n\n"
            f"<b>sᴇᴛᴛɪɴɢs ꜰᴏʀ <code>{modified_count}</code> ɢʀᴏᴜᴘs ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇsᴇᴛ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ.</b>"
        )
    except Exception as e:
        await msg.edit(f"<b>❌ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ:</b> <code>{e}</code>")

@Client.on_message(filters.command('off_auto_filter') & filters.user(ADMINS))
async def off_auto_filter(bot, message):
    db.update_bot_sttgs('AUTO_FILTER', False)
    await message.reply('<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴛᴜʀɴᴇᴅ ᴏꜰꜰ ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ ꜰᴏʀ ᴀʟʟ ɢʀᴏᴜᴘs</b>')


@Client.on_message(filters.command('on_auto_filter') & filters.user(ADMINS))
async def on_auto_filter(bot, message):
    db.update_bot_sttgs('AUTO_FILTER', True)
    await message.reply('<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴛᴜʀɴᴇᴅ ᴏɴ ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ ꜰᴏʀ ᴀʟʟ ɢʀᴏᴜᴘs</b>')


@Client.on_message(filters.command('off_pm_search') & filters.user(ADMINS))
async def off_pm_search(bot, message):
    db.update_bot_sttgs('PM_SEARCH', False)
    await message.reply('<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴛᴜʀɴᴇᴅ ᴏꜰꜰ ᴘᴍ sᴇᴀʀᴄʜ ꜰᴏʀ ᴀʟʟ ᴜsᴇʀs</b>')


@Client.on_message(filters.command('on_pm_search') & filters.user(ADMINS))
async def on_pm_search(bot, message):
    db.update_bot_sttgs('PM_SEARCH', True)
    await message.reply('<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴛᴜʀɴᴇᴅ ᴏɴ ᴘᴍ sᴇᴀʀᴄʜ ꜰᴏʀ ᴀʟʟ ᴜsᴇʀs</b>')

# ----------------------------- ADD SUDO -----------------------------
@Client.on_message(filters.command("addsudo") & filters.user(ADMINS))
async def add_sudo_cmd(bot, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>💡 ᴜsᴀɢᴇ: <code>/addsudo user_id</code></b>")
    try:
        user_id = int(message.command[1])
        if db.add_sudo(user_id):
            try:
                user = await bot.get_users(user_id)
                target_mention = user.mention
                target_name = user.first_name
            except:
                target_mention = f"<code>{user_id}</code>"
                target_name = "User"

            adder = message.from_user

            user_msg = (
                f"✨ <b>ʜᴇʏ {target_name},\n\n"
                f"ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs! ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴀᴘᴘᴏɪɴᴛᴇᴅ ᴀs ᴀɴ ᴀᴅᴍɪɴ (sᴜᴅᴏ ᴜsᴇʀ).\n"
                f"🆔 ɪᴅ: <code>{user_id}</code>\n\n"
                f"ɴᴏᴡ ʏᴏᴜ ʜᴀᴠᴇ ᴇxᴛᴇɴᴅᴇᴅ ᴘᴇʀᴍɪssɪᴏɴs.</b>"
            )
            try:
                await bot.send_message(chat_id=user_id, text=user_msg)
            except:
                pass

            log_msg = (
                "➕ <b>#sᴜᴅᴏ_ᴀᴅᴅᴇᴅ</b>\n\n"
                f"👤 <b>ᴜsᴇʀ:</b> {target_mention}\n"
                f"🆔 <b>ɪᴅ:</b> <code>{user_id}</code>\n"
                f"👮 <b>ᴀᴅᴅᴇᴅ ʙʏ:</b> {adder.mention}\n"
                f"🆔 <b>ᴀᴅᴅᴇʀ ɪᴅ:</b> <code>{adder.id}</code>\n"
                f"🎖️ <b>ʀᴏʟᴇ:</b> <code>ʙᴏᴛ ᴏᴡɴᴇʀ</code>"
            )
            await message.reply_text(log_msg)

            if PREMIUM_NOTIFY_CHANNEL:
                try:
                    await bot.send_message(PREMIUM_NOTIFY_CHANNEL, log_msg)
                except:
                    pass
        else:
            await message.reply_text("<b>⚠️ ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ɪɴ sᴜᴅᴏ ʟɪsᴛ.</b>")
    except ValueError:
        await message.reply_text("<b>❌ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍᴇʀɪᴄ ᴜsᴇʀ ɪᴅ.</b>")

# ---------------------------- REMOVE SUDO ----------------------------
@Client.on_message(filters.command("rmsudo") & filters.user(ADMINS))
async def rm_sudo_cmd(bot, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>💡 ᴜsᴀɢᴇ: <code>/rmsudo user_id</code></b>")
    try:
        user_id = int(message.command[1])
        if user_id in ADMINS:
            return await message.reply_text("<b>❌ ᴄᴀɴɴᴏᴛ ʀᴇᴍᴏᴠᴇ ᴍᴀɪɴ ᴀᴅᴍɪɴs ꜰʀᴏᴍ sᴜᴅᴏ!</b>")
            
        try:
            user = await bot.get_users(user_id)
            target_mention = user.mention
            target_name = user.first_name
        except:
            target_mention = f"<code>{user_id}</code>"
            target_name = "User"

        adder = message.from_user

        if db.remove_sudo(user_id):
            user_msg = (
                f"⚠️ <b>ʜᴇʏ {target_name},\n\n"
                f"ʏᴏᴜʀ ᴀᴅᴍɪɴ (sᴜᴅᴏ ᴜsᴇʀ) ᴘᴇʀᴍɪssɪᴏɴs ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ.\n"
                f"🆔 ɪᴅ: <code>{user_id}</code>\n\n"
                f"ʏᴏᴜ ɴᴏ ʟᴏɴɢᴇʀ ʜᴀᴠᴇ ᴇxᴛᴇɴᴅᴇᴅ ᴘᴇʀᴍɪssɪᴏɴs.\n\n"
                f"📞 ꜰᴏʀ ᴀɴʏ ǫᴜᴇʀɪᴇs, ᴄᴏɴᴛᴀᴄᴛ <a href='https://t.me/talk_mrs_bot'>ᴀᴅᴍɪɴ sᴜᴘᴘᴏʀᴛ</a>.</b>"
            )
            try:
                await bot.send_message(chat_id=user_id, text=user_msg, link_preview_options=LinkPreviewOptions(is_disabled=True))
            except:
                pass

            log_msg = (
                "➖ <b>#sᴜᴅᴏ_ʀᴇᴍᴏᴠᴇᴅ</b>\n\n"
                f"👤 <b>ᴜsᴇʀ:</b> {target_mention}\n"
                f"🆔 <b>ɪᴅ:</b> <code>{user_id}</code>\n"
                f"👮 <b>ʀᴇᴍᴏᴠᴇᴅ ʙʏ:</b> {adder.mention}\n"
                f"🆔 <b>ᴀᴅᴅᴇʀ ɪᴅ:</b> <code>{adder.id}</code>\n"
                f"🎖️ <b>ʀᴏʟᴇ:</b> <code>ʙᴏᴛ ᴏᴡɴᴇʀ</code>"
            )
            
            await message.reply_text(log_msg)

            if PREMIUM_NOTIFY_CHANNEL:
                try:
                    await bot.send_message(PREMIUM_NOTIFY_CHANNEL, log_msg)
                except:
                    pass
        else:
            await message.reply_text("<b>⚠️ ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ sᴜᴅᴏ ʟɪsᴛ.</b>")
    except ValueError:
        await message.reply_text("<b>❌ ᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ ʀᴇǫᴜɪʀᴇᴅ.</b>")

@Client.on_message(filters.command("sudolist") & filters.user(ADMINS))
async def sudo_list_cmd(bot, message):
    sudoers = db.get_sudo_list()
    if not sudoers:
        return await message.reply_text("<b>❌ ɴᴏ sᴜᴅᴏ ᴜsᴇʀs ꜰᴏᴜɴᴅ.</b>")
    
    out = "<b>✨ ɪɴꜰɪɴɪᴛʏ sᴜᴅᴏ ᴜsᴇʀs ʟɪsᴛ\n\n"
    for i, user_id in enumerate(sudoers, 1):
        try:
            user = await bot.get_users(user_id)
            name = user.first_name
            out += f"{i}. 👤 <a href='tg://user?id={user_id}'>{name}</a> ⠂<code>{user_id}</code>\n"
        except:
            out += f"{i}. 🆔 <code>{user_id}</code>\n"
            
    out += f"\n📊 ᴛᴏᴛᴀʟ sᴜᴅᴏᴇʀs: {len(sudoers)}</b>"
    await message.reply_text(out, disable_web_page_preview=True)