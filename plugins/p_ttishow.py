import os
import sys
import random
from Script import script
from database.users_chats_db import db
from pyrogram import Client, filters, enums
from utils import temp, get_settings
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from info import ADMINS, LOG_CHANNEL, PICS, SUPPORT_LINK, UPDATES_LINK
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ChatJoinRequest

@Client.on_chat_member_updated()
async def welcome(bot, message):
    if message.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return
    
    if message.new_chat_member and not message.old_chat_member:
        if message.new_chat_member.user.id == temp.ME:
            buttons = [[
                InlineKeyboardButton('ᴜᴘᴅᴀᴛᴇ', url=UPDATES_LINK),
                InlineKeyboardButton('ꜱᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
            ]]
            reply_markup=InlineKeyboardMarkup(buttons)
            user = message.from_user.mention if message.from_user else "ᴅᴇᴀʀ"
            await bot.send_photo(
                chat_id=message.chat.id, 
                photo=random.choice(PICS), 
                caption=f"👋 ʜᴇʟʟᴏ {user},\n\nᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ᴛᴏ ᴛʜᴇ <b>'{message.chat.title}'</b> ɢʀᴏᴜᴘ! ᴅᴏɴ'ᴛ ꜰᴏʀɢᴇᴛ ᴛᴏ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ. ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ, ᴀsᴋ ɪɴ ᴛʜᴇ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ. 😘</b>", 
                reply_markup=reply_markup
            )
            
            if not await db.get_chat(message.chat.id):
                total = await bot.get_chat_members_count(message.chat.id)
                username = f'@{message.chat.username}' if message.chat.username else 'Private'
                await bot.send_message(LOG_CHANNEL, script.NEW_GROUP_TXT.format(message.chat.title, message.chat.id, username, total))       
                await db.add_chat(message.chat.id, message.chat.title)
            return

        settings = await get_settings(message.chat.id)
        if settings["welcome"]:
            WELCOME = settings['welcome_text']
            welcome_msg = WELCOME.format(
                mention = message.new_chat_member.user.mention,
                title = message.chat.title
            )
            await bot.send_message(
                chat_id=message.chat.id, 
                text=welcome_msg, 
                disable_web_page_preview=True
            )

@Client.on_message(filters.command('restart') & filters.user(ADMINS))
async def restart_bot(bot, message):
    msg = await message.reply("<b>⏳ ʀᴇsᴛᴀʀᴛɪɴɢ...</b>")
    with open('restart.txt', 'w+') as file:
        file.write(f"{msg.chat.id}\n{msg.id}")
    os.execl(sys.executable, sys.executable, "bot.py")

@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('<b>⚠️ ɢɪᴠᴇ ᴍᴇ ᴀ ᴄʜᴀᴛ ɪᴅ</b>')
    
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason provided."
    try:
        chat = int(chat)
    except:
        chat = chat
        
    try:
        buttons = [[
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url=SUPPORT_LINK)
        ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat,
            text=f"<b>👋 ʜᴇʟʟᴏ ꜰʀɪᴇɴᴅs,\n\nᴍʏ ᴏᴡɴᴇʀ ʜᴀs ᴛᴏʟᴅ ᴍᴇ ᴛᴏ ʟᴇᴀᴠᴇ ᴛʜɪs ɢʀᴏᴜᴘ, sᴏ ɪ ᴍᴜsᴛ ɢᴏ! ɪꜰ ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴀᴅᴅ ᴍᴇ ᴀɢᴀɪɴ, ᴄᴏɴᴛᴀᴄᴛ ᴍʏ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ.\n\nʀᴇᴀsᴏɴ: <code>{reason}</code></b>",
            reply_markup=reply_markup,
        )
        await bot.leave_chat(chat)
        await message.reply(f"<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ʟᴇꜰᴛ ꜰʀᴏᴍ ᴛʜɪs ɢʀᴏᴜᴘ: <code>{chat}</code></b>")
    except Exception as e:
        await message.reply(f'<b>❌ ᴇʀʀᴏʀ:</b> <code>{e}</code>')

@Client.on_message(filters.command('ban_grp') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('<b>⚠️ ɢɪᴠᴇ ᴍᴇ ᴀ ᴄʜᴀᴛ ɪᴅ</b>')
    
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason provided."
    try:
        chat_ = int(chat)
    except:
        return await message.reply('<b>❌ ɢɪᴠᴇ ᴍᴇ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ</b>')
        
    cha_t = await db.get_chat(int(chat_))
    if not cha_t:
        return await message.reply("<b>❌ ᴄʜᴀᴛ ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ</b>")
    if cha_t.get('is_disabled'):
        return await message.reply(f"<b>⚠️ ᴛʜɪs ᴄʜᴀᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ.\nʀᴇᴀsᴏɴ: <code>{cha_t.get('reason')}</code></b>")
        
    await db.disable_chat(int(chat_), reason)
    if int(chat_) not in temp.BANNED_CHATS:
        temp.BANNED_CHATS.append(int(chat_))
        
    await message.reply('<b>✅ ᴄʜᴀᴛ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅɪsᴀʙʟᴇᴅ</b>')
    try:
        buttons = [[
            InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url=SUPPORT_LINK)
        ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_, 
            text=f"<b>👋 ʜᴇʟʟᴏ ꜰʀɪᴇɴᴅs,\n\nᴍʏ ᴏᴡɴᴇʀ ʜᴀs ᴛᴏʟᴅ ᴍᴇ ᴛᴏ ʟᴇᴀᴠᴇ ᴛʜɪs ɢʀᴏᴜᴘ, sᴏ ɪ ᴍᴜsᴛ ɢᴏ! ɪꜰ ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴀᴅᴅ ᴍᴇ ᴀɢᴀɪɴ, ᴄᴏɴᴛᴀᴄᴛ ᴍʏ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ.\n\nʀᴇᴀsᴏɴ: <code>{reason}</code></b>",
            reply_markup=reply_markup
        )
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply(f"<b>❌ ᴇʀʀᴏʀ:</b> <code>{e}</code>")

@Client.on_message(filters.command('unban_grp') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('<b>⚠️ ɢɪᴠᴇ ᴍᴇ ᴀ ᴄʜᴀᴛ ɪᴅ</b>')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply('<b>❌ ɢɪᴠᴇ ᴍᴇ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ</b>')
        
    sts = await db.get_chat(int(chat))
    if not sts:
        return await message.reply("<b>❌ ᴄʜᴀᴛ ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ</b>")
    if not sts.get('is_disabled'):
        return await message.reply('<b>⚠️ ᴛʜɪs ᴄʜᴀᴛ ɪs ɴᴏᴛ ʏᴇᴛ ᴅɪsᴀʙʟᴇᴅ.</b>')
        
    await db.re_enable_chat(int(chat_))
    if int(chat_) in temp.BANNED_CHATS:
        temp.BANNED_CHATS.remove(int(chat_))
    await message.reply("<b>✅ ᴄʜᴀᴛ sᴜᴄᴄᴇssꜰᴜʟʟʏ ʀᴇ-ᴇɴᴀʙʟᴇᴅ</b>")

@Client.on_message(filters.command('invite_link') & filters.user(ADMINS))
async def gen_invite_link(bot, message):
    if len(message.command) == 1:
        return await message.reply('<b>⚠️ ɢɪᴠᴇ ᴍᴇ ᴀ ᴄʜᴀᴛ ɪᴅ</b>')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        return await message.reply('<b>❌ ɢɪᴠᴇ ᴍᴇ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ</b>')
        
    try:
        link = await bot.create_chat_invite_link(chat)
    except Exception as e:
        return await message.reply(f'<b>❌ ᴇʀʀᴏʀ:</b> <code>{e}</code>')
    await message.reply(f'<b>✅ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ɪɴᴠɪᴛᴇ ʟɪɴᴋ:</b>\n{link.invite_link}')

@Client.on_message(filters.command('ban_user') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('<b>⚠️ ɢɪᴠᴇ ᴍᴇ ᴀ ᴜsᴇʀ ɪᴅ ᴏʀ ᴜsᴇʀɴᴀᴍᴇ</b>')
        
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason provided."
    try:
        chat = int(chat)
    except:
        pass
        
    try:
        k = await bot.get_users(chat)
    except Exception as e:
        return await message.reply(f'<b>❌ ᴇʀʀᴏʀ:</b> <code>{e}</code>')
        
    if k.id in ADMINS:
        return await message.reply('<b>⚠️ ʏᴏᴜ ᴄᴀɴɴᴏᴛ ʙᴀɴ ᴀɴ ᴀᴅᴍɪɴ!</b>')
        
    jar = await db.get_ban_status(k.id)
    if jar.get('is_banned'):
        return await message.reply(f"<b>⚠️ {k.mention} ɪs ᴀʟʀᴇᴀᴅʏ ʙᴀɴɴᴇᴅ.\nʀᴇᴀsᴏɴ: <code>{jar.get('ban_reason')}</code></b>")
        
    await db.ban_user(k.id, reason)
    if k.id not in temp.BANNED_USERS:
        temp.BANNED_USERS.append(k.id)
    await message.reply(f"<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ʙᴀɴɴᴇᴅ {k.mention}</b>")
   
@Client.on_message(filters.command('unban_user') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('<b>⚠️ ɢɪᴠᴇ ᴍᴇ ᴀ ᴜsᴇʀ ɪᴅ ᴏʀ ᴜsᴇʀɴᴀᴍᴇ</b>')
        
    r = message.text.split(None)
    if len(r) > 2:
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
    try:
        chat = int(chat)
    except:
        pass
        
    try:
        k = await bot.get_users(chat)
    except Exception as e:
        return await message.reply(f'<b>❌ ᴇʀʀᴏʀ:</b> <code>{e}</code>')
        
    jar = await db.get_ban_status(k.id)
    if not jar.get('is_banned'):
        return await message.reply(f"<b>⚠️ {k.mention} ɪs ɴᴏᴛ ʏᴇᴛ ʙᴀɴɴᴇᴅ.</b>")
        
    await db.remove_ban(k.id)
    if k.id in temp.BANNED_USERS:
        temp.BANNED_USERS.remove(k.id)
    await message.reply(f"<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴜɴʙᴀɴɴᴇᴅ {k.mention}</b>")
    
@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    raju = await message.reply('<b>⏳ ɢᴇᴛᴛɪɴɢ ʟɪsᴛ ᴏꜰ ᴜsᴇʀs...</b>')
    users = await db.get_all_users()
    out = "<b>👥 ᴜsᴇʀs sᴀᴠᴇᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ:</b>\n\n"
    for user in users:
        out += f"👤 <b>ɴᴀᴍᴇ:</b> {user['name']}\n🆔 <b>ɪᴅ:</b> <code>{user['id']}</code>"
        if user.get('ban_status', {}).get('is_banned'):
            out += ' <b>(Banned)</b>'
        if user.get('verify_status', {}).get('is_verified'):
            out += ' <b>(Verified)</b>'
        out += '\n\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('users.txt', 'w+', encoding="utf-8") as outfile:
            outfile.write(out)
        await message.reply_document('users.txt', caption="<b>📋 ʟɪsᴛ ᴏꜰ ᴜsᴇʀs</b>")
        await raju.delete()
        os.remove('users.txt')

@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message):
    raju = await message.reply('<b>⏳ ɢᴇᴛᴛɪɴɢ ʟɪsᴛ ᴏꜰ ᴄʜᴀᴛs...</b>')
    chats = await db.get_all_chats()
    out = "<b>👥 ᴄʜᴀᴛs sᴀᴠᴇᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ:</b>\n\n"
    for chat in chats:
        out += f"🗣️ <b>ᴛɪᴛʟᴇ:</b> {chat['title']}\n🆔 <b>ɪᴅ:</b> <code>{chat['id']}</code>"
        if chat.get('chat_status', {}).get('is_disabled'):
            out += ' <b>(Disabled)</b>'
        out += '\n\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('chats.txt', 'w+', encoding="utf-8") as outfile:
            outfile.write(out)
        await message.reply_document('chats.txt', caption="<b>📋 ʟɪsᴛ ᴏꜰ ᴄʜᴀᴛs</b>")
        await raju.delete()
        os.remove('chats.txt')

@Client.on_chat_join_request()
async def join_reqs(client, message: ChatJoinRequest):
    stg = await db.get_bot_sttgs()
    if stg and stg.get('REQUEST_FORCE_SUB_CHANNELS'):
        try:
            req_channel_id = int(stg.get('REQUEST_FORCE_SUB_CHANNELS'))
            if message.chat.id == req_channel_id:
                # Need to use await since find_join_req is async
                if not await db.find_join_req(message.from_user.id):
                    await db.add_join_req(message.from_user.id)
        except Exception as e:
            print(f"Join Request Error: {e}")

@Client.on_message(filters.command("delreq") & filters.private & filters.user(ADMINS))
async def del_requests(client, message):
    await db.del_join_req()
    await message.reply('<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ᴀʟʟ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛs!</b>')