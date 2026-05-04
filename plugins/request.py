import re
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS, LOG_CHANNEL

@Client.on_message(filters.command("request"))
async def request_movie(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>🛸 ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴍᴏᴠɪᴇ ɴᴀᴍᴇ!\n\n➲ ᴇx:</b> <code>/request Avengers</code>")
    
    movie_name = message.text.split(None, 1)[1]
    user = message.from_user
    
    admin_log = (
        f"<b>🛰 ɴᴇᴡ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ</b>\n\n"
        f"➲ <b>ᴍᴏᴠɪᴇ:</b> <code>{movie_name}</code>\n"
        f"➲ <b>ᴜꜱᴇʀ:</b> {user.mention}\n"
        f"➲ <b>ɪᴅ:</b> <code>{user.id}</code>"
    )

    btn = [[
        InlineKeyboardButton("✅ ᴍᴀʀᴋ ᴀᴠᴀɪʟᴀʙʟᴇ", callback_data=f"reqdone_{user.id}")
    ]]
    
    try:
        await client.send_message(
            chat_id=LOG_CHANNEL, 
            text=admin_log, 
            reply_markup=InlineKeyboardMarkup(btn)
        )
        await message.reply_text(
            f"<b>✅ ᴅᴏɴᴇ {user.first_name}!\n\nʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ꜰᴏʀ '<code>{movie_name}</code>' ʜᴀꜱ ʙᴇᴇɴ ꜱᴇɴᴛ ᴛᴏ ᴏᴜʀ ᴀᴅᴍɪɴꜱ. ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ!</b>"
        )
    except Exception as e:
        logging.error(e)
        await message.reply_text("<b>❌ ᴀᴅᴍɪɴ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ɴᴏᴛ ꜰᴏᴜɴᴅ! ᴄᴏɴᴛᴀᴄᴛ ꜱᴜᴘᴘᴏʀᴛ.</b>")

@Client.on_callback_query(filters.regex(r"^reqdone_"))
async def handle_request_done(client, query):
    if query.from_user.id not in ADMINS:
        return await query.answer("⚠️ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴍᴀʀᴋ ʀᴇǫᴜᴇꜱᴛꜱ ᴀꜱ ᴅᴏɴᴇ!", show_alert=True)

    user_id = int(query.data.split("_")[1])
    
    try:
        movie = re.search(r"ᴍᴏᴠɪᴇ:\s+(.+)", query.message.text).group(1)
    except:
        movie = "ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ"

    try:
        await client.send_message(
            chat_id=user_id, 
            text=f"<b>✨ ʜᴇʏ! ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛᴇᴅ ᴍᴏᴠɪᴇ '<code>{movie}</code>' ɪꜱ ɴᴏᴡ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ᴛʜᴇ ʙᴏᴛ! 🚀\n\nꜱᴇᴀʀᴄʜ ɴᴏᴡ ᴀɴᴅ ᴇɴᴊᴏʏ!</b>"
        )
        await query.answer("✅ ᴜꜱᴇʀ ʜᴀꜱ ʙᴇᴇɴ ɴᴏᴛɪꜰɪᴇᴅ!", show_alert=True)
        await query.edit_message_text(
            text=f"{query.message.text.html}\n\n✅ <b>ꜱᴛᴀᴛᴜꜱ: ᴄᴏᴍᴘʟᴇᴛᴇᴅ ʙʏ {query.from_user.mention}</b>"
        )
    except Exception as e:
        await query.answer("⚠️ ᴇʀʀᴏʀ: ᴜꜱᴇʀ ʙʟᴏᴄᴋᴇᴅ ʙᴏᴛ ᴏʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!", show_alert=True)
        await query.edit_message_text(
            text=f"{query.message.text.html}\n\n❌ <b>ꜱᴛᴀᴛᴜꜱ: ꜰᴀɪʟᴇᴅ ᴛᴏ ɴᴏᴛɪꜰʏ (ʙʟᴏᴄᴋᴇᴅ)</b>"
        )