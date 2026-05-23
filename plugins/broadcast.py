import time
import asyncio
from pyrogram import Client, filters
from info import ADMINS
from database.users_chats_db import db
from utils import temp, get_readable_time, broadcast_messages, groups_broadcast_messages
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

lock = asyncio.Lock()

@Client.on_callback_query(filters.regex(r'^broadcast_cancel'))
async def broadcast_cancel(bot, query):
    _, ident = query.data.split("#")
    if ident == 'users':
        await query.message.edit("<b>⚠️ ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ᴜsᴇʀs ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...</b>")
        temp.USERS_CANCEL = True
    elif ident == 'groups':
        temp.GROUPS_CANCEL = True
        await query.message.edit("<b>⚠️ ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ɢʀᴏᴜᴘs ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...</b>")
                
@Client.on_message(filters.command(["broadcast", "pin_broadcast"]) & filters.user(ADMINS) & filters.reply)
async def users_broadcast(bot, message):
    if lock.locked():
        return await message.reply('<b>⏳ ᴄᴜʀʀᴇɴᴛʟʏ ʙʀᴏᴀᴅᴄᴀsᴛ ᴘʀᴏᴄᴇssɪɴɢ, ᴡᴀɪᴛ ꜰᴏʀ ᴄᴏᴍᴘʟᴇᴛᴇ...</b>')
    
    pin = message.command[0] == 'pin_broadcast'
    
    try:
        users = await db.get_all_users()
    except:
        users = db.get_all_users()

    b_msg = message.reply_to_message
    b_sts = await message.reply_text(text='<b>🚀 ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ʏᴏᴜʀ ᴜsᴇʀs ᴍᴇssᴀɢᴇs...</b>')
    
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0
    last_update = time.time()

    async with lock:
        tasks = []
        for user in users:
            if temp.USERS_CANCEL:
                temp.USERS_CANCEL = False
                time_taken = get_readable_time(time.time() - start_time)
                await b_sts.edit(f"<b>🚫 ᴜsᴇʀs ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>\n⏱ <b>ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ:</b> {time_taken}\n\n👥 <b>ᴛᴏᴛᴀʟ ᴜsᴇʀs:</b> <code>{total_users}</code>\n✅ <b>ᴄᴏᴍᴘʟᴇᴛᴇᴅ:</b> <code>{done} / {total_users}</code>\n🚀 <b>sᴜᴄᴄᴇss:</b> <code>{success}</code>\n❌ <b>ꜰᴀɪʟᴇᴅ:</b> <code>{failed}</code>")
                return

            # Batch me tasks add karo (FAST Speed)
            tasks.append(asyncio.create_task(broadcast_messages(int(user['id']), b_msg, pin)))
            done += 1
            
            # Ek baar mein 20 request fire karo aur 1 second ruko (Anti-FloodWait)
            if len(tasks) >= 20:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for sts in results:
                    # ✅ FIX: Ab yeh kisi bhi success value aur exception ko properly handle karega
                    if isinstance(sts, Exception) or sts in [False, 'Error', 'Failed', None]:
                        failed += 1
                    else:
                        success += 1
                tasks.clear()
                await asyncio.sleep(1) # Limit Bypass
                
                # Message har 10 seconds me edit karo taaki FloodWait na aaye
                if time.time() - last_update > 10:
                    btn = [[InlineKeyboardButton('🚫 ᴄᴀɴᴄᴇʟ', callback_data='broadcast_cancel#users')]]
                    try:
                        await b_sts.edit(f"<b>⚡ ᴜsᴇʀs ʙʀᴏᴀᴅᴄᴀsᴛ ɪɴ ᴘʀᴏɢʀᴇss...</b>\n\n👥 <b>ᴛᴏᴛᴀʟ ᴜsᴇʀs:</b> <code>{total_users}</code>\n✅ <b>ᴄᴏᴍᴘʟᴇᴛᴇᴅ:</b> <code>{done} / {total_users}</code>\n🚀 <b>sᴜᴄᴄᴇss:</b> <code>{success}</code>\n❌ <b>ꜰᴀɪʟᴇᴅ:</b> <code>{failed}</code>", reply_markup=InlineKeyboardMarkup(btn))
                        last_update = time.time()
                    except:
                        pass

        # Bachi hui requests (agar 20 se kam bachi ho)
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for sts in results:
                # ✅ FIX
                if isinstance(sts, Exception) or sts in [False, 'Error', 'Failed', None]:
                    failed += 1
                else:
                    success += 1

        time_taken = get_readable_time(time.time() - start_time)
        await b_sts.edit(f"<b>🎉 ᴜsᴇʀs ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n⏱ <b>ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ:</b> {time_taken}\n\n👥 <b>ᴛᴏᴛᴀʟ ᴜsᴇʀs:</b> <code>{total_users}</code>\n✅ <b>ᴄᴏᴍᴘʟᴇᴛᴇᴅ:</b> <code>{done} / {total_users}</code>\n🚀 <b>sᴜᴄᴄᴇss:</b> <code>{success}</code>\n❌ <b>ꜰᴀɪʟᴇᴅ:</b> <code>{failed}</code>")


@Client.on_message(filters.command(["grp_broadcast", "pin_grp_broadcast"]) & filters.user(ADMINS) & filters.reply)
async def groups_broadcast(bot, message):
    if lock.locked():
        return await message.reply('<b>⏳ ᴄᴜʀʀᴇɴᴛʟʏ ʙʀᴏᴀᴅᴄᴀsᴛ ᴘʀᴏᴄᴇssɪɴɢ, ᴡᴀɪᴛ ꜰᴏʀ ᴄᴏᴍᴘʟᴇᴛᴇ...</b>')
    
    pin = message.command[0] == 'pin_grp_broadcast'
    
    try:
        chats = await db.get_all_chats()
    except:
        chats = db.get_all_chats()

    b_msg = message.reply_to_message
    b_sts = await message.reply_text(text='<b>🚀 ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ʏᴏᴜʀ ɢʀᴏᴜᴘs ᴍᴇssᴀɢᴇs...</b>')
    
    start_time = time.time()
    total_chats = await db.total_chat_count()
    done = 0
    failed = 0
    success = 0
    last_update = time.time()

    async with lock:
        tasks = []
        for chat in chats:
            if temp.GROUPS_CANCEL:
                temp.GROUPS_CANCEL = False
                time_taken = get_readable_time(time.time() - start_time)
                await b_sts.edit(f"<b>🚫 ɢʀᴏᴜᴘs ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>\n⏱ <b>ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ:</b> {time_taken}\n\n👥 <b>ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘs:</b> <code>{total_chats}</code>\n✅ <b>ᴄᴏᴍᴘʟᴇᴛᴇᴅ:</b> <code>{done} / {total_chats}</code>\n🚀 <b>sᴜᴄᴄᴇss:</b> <code>{success}</code>\n❌ <b>ꜰᴀɪʟᴇᴅ:</b> <code>{failed}</code>")
                return

            tasks.append(asyncio.create_task(groups_broadcast_messages(int(chat['id']), b_msg, pin)))
            done += 1
            
            if len(tasks) >= 20:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for sts in results:
                    # ✅ FIX
                    if isinstance(sts, Exception) or sts in [False, 'Error', 'Failed', None]:
                        failed += 1
                    else:
                        success += 1
                tasks.clear()
                await asyncio.sleep(1)
                
                if time.time() - last_update > 10:
                    btn = [[InlineKeyboardButton('🚫 ᴄᴀɴᴄᴇʟ', callback_data='broadcast_cancel#groups')]]
                    try:
                        await b_sts.edit(f"<b>⚡ ɢʀᴏᴜᴘs ʙʀᴏᴀᴅᴄᴀsᴛ ɪɴ ᴘʀᴏɢʀᴇss...</b>\n\n👥 <b>ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘs:</b> <code>{total_chats}</code>\n✅ <b>ᴄᴏᴍᴘʟᴇᴛᴇᴅ:</b> <code>{done} / {total_chats}</code>\n🚀 <b>sᴜᴄᴄᴇss:</b> <code>{success}</code>\n❌ <b>ꜰᴀɪʟᴇᴅ:</b> <code>{failed}</code>", reply_markup=InlineKeyboardMarkup(btn))
                        last_update = time.time()
                    except:
                        pass
                    
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for sts in results:
                # ✅ FIX
                if isinstance(sts, Exception) or sts in [False, 'Error', 'Failed', None]:
                    failed += 1
                else:
                    success += 1

        time_taken = get_readable_time(time.time() - start_time)
        await b_sts.edit(f"<b>🎉 ɢʀᴏᴜᴘs ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n⏱ <b>ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ:</b> {time_taken}\n\n👥 <b>ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘs:</b> <code>{total_chats}</code>\n✅ <b>ᴄᴏᴍᴘʟᴇᴛᴇᴅ:</b> <code>{done} / {total_chats}</code>\n🚀 <b>sᴜᴄᴄᴇss:</b> <code>{success}</code>\n❌ <b>ꜰᴀɪʟᴇᴅ:</b> <code>{failed}</code>")