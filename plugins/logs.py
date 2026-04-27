import os
import psutil
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS
from utils import temp

@Client.on_message(filters.command("logs") & filters.user(ADMINS))
async def get_bot_logs(bot, message):
    log_file = "bot.log"

    if not os.path.exists(log_file):
        return await message.reply("<b>❌ ʟᴏɢ ғɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ!</b>")

    # --- System Metrics ---
    start_time = getattr(temp, 'START_TIME', None) or time.time()
    uptime_seconds = int(time.time() - start_time)
    uptime = time.strftime("%Hʜ %Mᴍ %Ss", time.gmtime(uptime_seconds))

    cpu  = psutil.cpu_percent(interval=0.5) 
    mem  = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    status_text = (
        "<b>📂 sʏsᴛᴇᴍ ʟᴏɢs ʀᴇᴘᴏʀᴛ</b>\n"
        "<code>" + "━" * 20 + "</code>\n"
        f"<b>🚀 ᴜᴘᴛɪᴍᴇ:</b> <code>{uptime}</code>\n"
        f"<b>🖥️ ᴄᴘᴜ:</b>    <code>{cpu}%</code>\n"
        f"<b>📊 ʀᴀᴍ:</b>    <code>{mem}%</code>\n"
        f"<b>💾 ᴅɪsᴋ:</b>   <code>{disk}%</code>\n"
        "<code>" + "━" * 20 + "</code>"
    )

    ms = await message.reply("<b>🔄 ᴘʀᴇᴘᴀʀɪɴɢ ᴅᴏᴄᴜᴍᴇɴᴛ...</b>")

    try:
        await message.reply_document(
            document=log_file,
            caption=status_text,
            file_name=f"Logs_Report_{int(time.time())}.txt",
        )
        await ms.delete()
    except Exception as e:
        print(f"[logs] Error: {e}")
        await ms.edit("<b>❌ ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ʟᴏɢ ғɪʟᴇ.</b>")


@Client.on_message(filters.command("clearlogs") & filters.user(ADMINS))
async def clear_logs(bot, message):
    log_file = "bot.log"

    if not os.path.exists(log_file):
        return await message.reply("<b>❌ ɴᴏ ʟᴏɢ ғɪʟᴇ ғᴏᴜɴᴅ ᴛᴏ ᴄʟᴇᴀʀ.</b>")

    # Confirmation Buttons
    confirm_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ ʏᴇs, ᴄʟᴇᴀʀ", callback_data="confirm_clearlogs"),
        InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ",     callback_data="cancel_clearlogs"),
    ]])
    
    await message.reply(
        "<b>⚠️ ᴀʀᴇ ʏᴏᴜ sᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄʟᴇᴀʀ ᴀʟʟ ʟᴏɢs?</b>",
        reply_markup=confirm_markup,
    )


@Client.on_callback_query(filters.regex("^confirm_clearlogs$") & filters.user(ADMINS))
async def confirm_clear_logs(bot, callback_query):
    log_file = "bot.log"
    try:
        with open(log_file, "w") as f:
            f.truncate(0)
        await callback_query.message.edit("<b>✅ ʟᴏɢs ᴄʟᴇᴀʀᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b>")
    except Exception as e:
        await callback_query.message.edit(f"<b>❌ ᴇʀʀᴏʀ:</b> <code>{e}</code>")


@Client.on_callback_query(filters.regex("^cancel_clearlogs$") & filters.user(ADMINS))
async def cancel_clear_logs(bot, callback_query):
    await callback_query.message.edit("<b>🚫 ᴏᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>")