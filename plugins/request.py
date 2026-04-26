from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS, LOG_CHANNEL
import logging

@Client.on_message(filters.command("request"))
async def request_movie(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>🛸 ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴍᴏᴠɪᴇ ɴᴀᴍᴇ!\n\n➲ ᴇx:</b> <code>/request Avengers</code>")
    
    movie_name = message.text.split(None, 1)[1]
    user = message.from_user
    
    admin_log = (
        f"<b>🛰 ɴᴇᴡ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇsᴛ</b>\n\n"
        f"➲ <b>ᴍᴏᴠɪᴇ:</b> <code>{movie_name}</code>\n"
        f"➲ <b>ᴜsᴇʀ:</b> {user.mention}\n"
        f"➲ <b>ɪᴅ:</b> <code>{user.id}</code>"
    )
    
    safe_movie_name = movie_name[:20] 
    btn = [[
        InlineKeyboardButton("✅ ᴍᴀʀᴋ ᴀᴠᴀɪʟᴀʙʟᴇ", callback_data=f"req_done_{user.id}_{safe_movie_name}")
    ]]
    
    try:
        await client.send_message(
            chat_id=LOG_CHANNEL, 
            text=admin_log, 
            reply_markup=InlineKeyboardMarkup(btn)
        )
        await message.reply_text(
            f"<b>✅ ᴅᴏɴᴇ {user.first_name}!\n\nʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ꜰᴏʀ '{movie_name}' ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ᴏᴜʀ ᴀᴅᴍɪɴs. ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ!</b>"
        )
    except Exception as e:
        logging.error(e)
        await message.reply_text("<b>❌ ᴀᴅᴍɪɴ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ɴᴏᴛ ꜰᴏᴜɴᴅ! ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ.</b>")

@Client.on_callback_query(filters.regex(r"^req_done_"))
async def handle_request_done(client, query):
    data = query.data.split("_")
    user_id = int(data[2])
    movie = data[3]

    try:
        await client.send_message(
            chat_id=user_id, 
            text=f"<b>✨ ʜᴇʏ! ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛᴇᴅ ᴍᴏᴠɪᴇ '{movie}...' ɪs ɴᴏᴡ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ᴛʜᴇ ʙᴏᴛ! 🚀\n\nsᴇᴀʀᴄʜ ɴᴏᴡ ᴀɴᴅ ᴇɴᴊᴏʏ!</b>"
        )
        await query.answer("ᴜsᴇʀ ʜᴀs ʙᴇᴇɴ ɴᴏᴛɪꜰɪᴇᴅ!", show_alert=True)
        await query.edit_message_text(
            text=f"{query.message.text.html}\n\n✅ <b>sᴛᴀᴛᴜs: ᴄᴏᴍᴘʟᴇᴛᴇᴅ ʙʏ {query.from_user.mention}</b>"
        )
    except Exception as e:
        await query.answer(f"⚠️ ᴇʀʀᴏʀ: {e}", show_alert=True)