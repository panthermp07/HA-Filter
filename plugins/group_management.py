import asyncio
from pyrogram import Client, filters
from utils import is_check_admin
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.command('manage') & filters.group)
async def members_management(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text('<b>❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>')
    btn = [[
        InlineKeyboardButton('🔊 ᴜɴᴍᴜᴛᴇ ᴀʟʟ', callback_data='unmute_all_members'),
        InlineKeyboardButton('🔓 ᴜɴʙᴀɴ ᴀʟʟ', callback_data='unban_all_members')
    ],[
        InlineKeyboardButton('🚷 ᴋɪᴄᴋ ᴍᴜᴛᴇᴅ ᴜsᴇʀs', callback_data='kick_muted_members'),
        InlineKeyboardButton('👻 ᴋɪᴄᴋ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs', callback_data='kick_deleted_accounts_members')
    ]]
    await message.reply_text("<b>⚙️ sᴇʟᴇᴄᴛ ᴏɴᴇ ꜰᴜɴᴄᴛɪᴏɴ ᴛᴏ ᴍᴀɴᴀɢᴇ ᴍᴇᴍʙᴇʀs.</b>", reply_markup=InlineKeyboardMarkup(btn))
  
@Client.on_message(filters.command('ban') & filters.group)
async def ban_chat_user(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text('<b>❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>')
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.username or message.reply_to_message.from_user.id
    else:
        try:
            user_id = message.text.split(" ", 1)[1]
        except IndexError:
            return await message.reply_text("<b>⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴜsᴇʀ ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴜsᴇʀ ɪᴅ/ᴜsᴇʀɴᴀᴍᴇ.</b>")
    try:
        user_id = int(user_id)
    except ValueError:
        pass
    try:
        user = (await client.get_chat_member(message.chat.id, user_id)).user
    except:
        return await message.reply_text("<b>❌ ᴄᴀɴ'ᴛ ꜰɪɴᴅ ᴛʜᴇ ɢɪᴠᴇɴ ᴜsᴇʀ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>")
    try:
        await client.ban_chat_member(message.chat.id, user_id)
    except:
        return await message.reply_text("<b>⚠️ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴄᴄᴇss ᴛᴏ ʙᴀɴ ᴜsᴇʀs.</b>")
    await message.reply_text(f'<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ʙᴀɴɴᴇᴅ {user.mention} ꜰʀᴏᴍ {message.chat.title}</b>')

@Client.on_message(filters.command('kick') & filters.group)
async def kick_chat_user(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text('<b>❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>')
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.username or message.reply_to_message.from_user.id
    else:
        try:
            user_id = message.text.split(" ", 1)[1]
        except IndexError:
            return await message.reply_text("<b>⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴜsᴇʀ ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴜsᴇʀ ɪᴅ/ᴜsᴇʀɴᴀᴍᴇ.</b>")
    try:
        user_id = int(user_id)
    except ValueError:
        pass
    try:
        user = (await client.get_chat_member(message.chat.id, user_id)).user
    except:
        return await message.reply_text("<b>❌ ᴄᴀɴ'ᴛ ꜰɪɴᴅ ᴛʜᴇ ɢɪᴠᴇɴ ᴜsᴇʀ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>")
    try:
        await client.ban_chat_member(message.chat.id, user_id)
        await client.unban_chat_member(message.chat.id, user_id)
    except:
        return await message.reply_text("<b>⚠️ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴄᴄᴇss ᴛᴏ ᴋɪᴄᴋ ᴜsᴇʀs.</b>")
    await message.reply_text(f'<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴋɪᴄᴋᴇᴅ {user.mention} ꜰʀᴏᴍ {message.chat.title}</b>')

@Client.on_message(filters.command('mute') & filters.group)
async def mute_chat_user(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text('<b>❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>')
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.username or message.reply_to_message.from_user.id
    else:
        try:
            user_id = message.text.split(" ", 1)[1]
        except IndexError:
            return await message.reply_text("<b>⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴜsᴇʀ ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴜsᴇʀ ɪᴅ/ᴜsᴇʀɴᴀᴍᴇ.</b>")
    try:
        user_id = int(user_id)
    except ValueError:
        pass
    try:
        user = (await client.get_chat_member(message.chat.id, user_id)).user
    except:
        return await message.reply_text("<b>❌ ᴄᴀɴ'ᴛ ꜰɪɴᴅ ᴛʜᴇ ɢɪᴠᴇɴ ᴜsᴇʀ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>")
    try:
        await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions())
    except:
        return await message.reply_text("<b>⚠️ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴄᴄᴇss ᴛᴏ ᴍᴜᴛᴇ ᴜsᴇʀs.</b>")
    await message.reply_text(f'<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴍᴜᴛᴇᴅ {user.mention} ɪɴ {message.chat.title}</b>')

@Client.on_message(filters.command(["unban", "unmute"]) & filters.group)
async def unban_chat_user(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text('<b>❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>')
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.username or message.reply_to_message.from_user.id
    else:
        try:
            user_id = message.text.split(" ", 1)[1]
        except IndexError:
            return await message.reply_text("<b>⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴜsᴇʀ ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴜsᴇʀ ɪᴅ/ᴜsᴇʀɴᴀᴍᴇ.</b>")
    try:
        user_id = int(user_id)
    except ValueError:
        pass
    try:
        user = (await client.get_chat_member(message.chat.id, user_id)).user
    except:
        return await message.reply_text("<b>❌ ᴄᴀɴ'ᴛ ꜰɪɴᴅ ᴛʜᴇ ɢɪᴠᴇɴ ᴜsᴇʀ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>")
    try:
        await client.unban_chat_member(message.chat.id, user_id)
    except:
        return await message.reply_text(f"<b>⚠️ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴄᴄᴇss ᴛᴏ {message.command[0].upper()} ᴜsᴇʀs.</b>")
    
    action = "ᴜɴʙᴀɴɴᴇᴅ" if message.command[0] == "unban" else "ᴜɴᴍᴜᴛᴇᴅ"
    await message.reply_text(f'<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ {action} {user.mention} ɪɴ {message.chat.title}</b>')

@Client.on_message(filters.command('pin') & filters.group)
async def pin_message(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text('<b>❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>')
    if not message.reply_to_message:
        return await message.reply_text("<b>⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴘɪɴ ɪᴛ.</b>")
    try:
        await message.reply_to_message.pin(disable_notification=True)
        await message.reply_text("<b>📌 ᴍᴇssᴀɢᴇ ᴘɪɴɴᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ.</b>")
    except:
        await message.reply_text("<b>⚠️ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴄᴄᴇss ᴛᴏ ᴘɪɴ ᴍᴇssᴀɢᴇs.</b>")

@Client.on_message(filters.command('unpin') & filters.group)
async def unpin_message(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text('<b>❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>')
    if not message.reply_to_message:
        return await message.reply_text("<b>⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴜɴᴘɪɴ ɪᴛ.</b>")
    try:
        await message.reply_to_message.unpin()
        await message.reply_text("<b>📌 ᴍᴇssᴀɢᴇ ᴜɴᴘɪɴɴᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ.</b>")
    except:
        await message.reply_text("<b>⚠️ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴄᴄᴇss ᴛᴏ ᴜɴᴘɪɴ ᴍᴇssᴀɢᴇs.</b>")

@Client.on_message(filters.command('purge') & filters.group)
async def purge_messages(client, message):
    if not await is_check_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text('<b>❌ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>')
    if not message.reply_to_message:
        return await message.reply_text("<b>⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ sᴛᴀʀᴛ ᴘᴜʀɢɪɴɢ ꜰʀᴏᴍ ᴛʜᴇʀᴇ.</b>")
    
    status_msg = await message.reply_text("<b>🗑 ᴘᴜʀɢɪɴɢ ᴍᴇssᴀɢᴇs...</b>")
    message_ids = []
    
    for message_id in range(message.reply_to_message.id, message.id):
        message_ids.append(message_id)
        if len(message_ids) == 100:
            try:
                await client.delete_messages(message.chat.id, message_ids)
            except:
                pass
            message_ids = []
            await asyncio.sleep(1) 
            
    if message_ids:
        try:
            await client.delete_messages(message.chat.id, message_ids)
        except:
            pass
            
    await client.delete_messages(message.chat.id, message.id)
    await status_msg.edit_text("<b>✅ ᴍᴇssᴀɢᴇs ᴘᴜʀɢᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ.</b>")
    await asyncio.sleep(3)
    await status_msg.delete()