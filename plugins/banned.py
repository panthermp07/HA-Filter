from pyrogram import Client, filters, enums, StopPropagation
from utils import temp
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions
from database.users_chats_db import db
from info import SUPPORT_LINK

async def banned_users(_, __, message: Message):
    return (
        message.from_user is not None or not message.sender_chat
    ) and message.from_user.id in temp.BANNED_USERS

banned_user = filters.create(banned_users)

async def disabled_chat(_, __, message: Message):
    return message.chat.id in temp.BANNED_CHATS

disabled_group=filters.create(disabled_chat)

@Client.on_message(filters.private & banned_user & filters.incoming)
async def is_user_banned(bot, message):
    buttons = [[
        InlineKeyboardButton('🎧 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url=SUPPORT_LINK)
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    ban = await db.get_ban_status(message.from_user.id)
    
    await message.reply(
        text=(
            f"<b>🚫 sᴏʀʀʏ {message.from_user.mention},\n\n"
            f"ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴜsɪɴɢ ᴍᴇ! ɪꜰ ʏᴏᴜ ᴛʜɪɴᴋ ᴛʜɪs ɪs ᴀ ᴍɪsᴛᴀᴋᴇ, ᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴏᴜʀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ.\n\n"
            f"📝 ʀᴇᴀsᴏɴ: <code>{ban['ban_reason']}</code></b>"
        ),
        reply_markup=reply_markup,
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
    raise StopPropagation 

@Client.on_message(filters.group & disabled_group & filters.incoming)
async def is_group_disabled(bot, message):
    buttons = [[
        InlineKeyboardButton('🎧 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url=SUPPORT_LINK)
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    vazha = await db.get_chat(message.chat.id)
    
    k = await message.reply(
        text=(
            f"<b>🚫 ᴄʜᴀᴛ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ 🚫\n\n"
            f"ᴍʏ ᴏᴡɴᴇʀ ʜᴀs ʀᴇsᴛʀɪᴄᴛᴇᴅ ᴍᴇ ꜰʀᴏᴍ ᴡᴏʀᴋɪɴɢ ʜᴇʀᴇ! ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ ꜰᴏʀ ᴍᴏʀᴇ ɪɴꜰᴏ.\n\n"
            f"📝 ʀᴇᴀsᴏɴ: <code>{vazha['reason']}</code></b>"
        ),
        reply_markup=reply_markup,
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
    
    try:
        await k.pin()
    except:
        pass
        
    await bot.leave_chat(message.chat.id)
    raise StopPropagation