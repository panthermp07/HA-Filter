import os
import asyncio
from datetime import datetime
from speedtest import Speedtest, ConfigRetrievalError, SpeedtestBestServerFailure
import yt_dlp
import httpx

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyParameters
from pyrogram.errors import UserNotParticipant

from utils import get_size, temp
from info import ADMINS

@Client.on_message(filters.command('id'))
async def showid(client, message):
    chat_type = message.chat.type
    
    if message.reply_to_message:
        target = message.reply_to_message
        if target.forward_from_chat:
            return await message.reply_text(f"📢 <b>ꜰᴏʀᴡᴀʀᴅᴇᴅ ᴄʜᴀɴɴᴇʟ:</b> {target.forward_from_chat.title}\n🆔 <b>ɪᴅ:</b> <code>{target.forward_from_chat.id}</code>")
        elif target.from_user:
            return await message.reply_text(f"👤 <b>ᴜsᴇʀ:</b> {target.from_user.mention}\n🆔 <b>ɪᴅ:</b> <code>{target.from_user.id}</code>")

    # Case 2: Mention or Username (e.g., /id @username)
    elif len(message.command) > 1:
        try:
            input_data = message.command[1]
            user = await client.get_users(input_data)
            return await message.reply_text(f"👤 <b>ᴜsᴇʀ:</b> {user.mention}\n🆔 <b>ɪᴅ:</b> <code>{user.id}</code>")
        except Exception as e:
            return await message.reply_text(f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{e}</code>")

    # Case 3: Default (Chat IDs)
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        await message.reply_text(f'👤 <b>ʏᴏᴜʀ ɪᴅ:</b> <code>{message.from_user.id}</code>')
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await message.reply_text(f'👥 <b>ɢʀᴏᴜᴘ ɪᴅ:</b> <code>{message.chat.id}</code>')
    elif chat_type == enums.ChatType.CHANNEL:
        await message.reply_text(f'📢 <b>ᴄʜᴀɴɴᴇʟ ɪᴅ:</b> <code>{message.chat.id}</code>')

@Client.on_message(filters.command('speedtest'))
async def speedtest(client, message):
    msg = await message.reply_text("<b>🚀 ɪɴɪᴛɪᴀᴛɪɴɢ sᴘᴇᴇᴅᴛᴇsᴛ...</b>")
    try:
        speed = Speedtest()
        speed.get_best_server()
    except (ConfigRetrievalError, SpeedtestBestServerFailure):
        return await msg.edit("<b>❌ ᴄᴀɴ'ᴛ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ sᴇʀᴠᴇʀ ʀɪɢʜᴛ ɴᴏᴡ!</b>")

    speed.download()
    speed.upload()
    speed.results.share()
    result = speed.results.dict()
    photo = result['share']

    text = f'''✨ <b>ɪɴꜰɪɴɪᴛʏ sᴘᴇᴇᴅᴛᴇsᴛ ʀᴇsᴜʟᴛs</b>

➲ <b>sᴘᴇᴇᴅᴛᴇsᴛ ɪɴꜰᴏ</b>
┠ <b>ᴜᴘʟᴏᴀᴅ:</b> <code>{get_size(result['upload'])}/s</code>
┠ <b>ᴅᴏᴡɴʟᴏᴀᴅ:</b> <code>{get_size(result['download'])}/s</code>
┠ <b>ᴘɪɴɢ:</b> <code>{result['ping']} ᴍs</code>
┠ <b>ᴛɪᴍᴇ:</b> <code>{datetime.strptime(result['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")}</code>
┠ <b>ᴅᴀᴛᴀ sᴇɴᴛ:</b> <code>{get_size(int(result['bytes_sent']))}</code>
┖ <b>ᴅᴀᴛᴀ ʀᴇᴄᴇɪᴠᴇᴅ:</b> <code>{get_size(int(result['bytes_received']))}</code>

➲ <b>sᴘᴇᴇᴅᴛᴇsᴛ sᴇʀᴠᴇʀ</b>
┠ <b>ɴᴀᴍᴇ:</b> <code>{result['server']['name']}</code>
┠ <b>ᴄᴏᴜɴᴛʀʏ:</b> <code>{result['server']['country']}, {result['server']['cc']}</code>
┠ <b>sᴘᴏɴsᴏʀ:</b> <code>{result['server']['sponsor']}</code>
┠ <b>ʟᴀᴛᴇɴᴄʏ:</b> <code>{result['server']['latency']}</code>
┠ <b>ʟᴀᴛɪᴛᴜᴅᴇ:</b> <code>{result['server']['lat']}</code>
┖ <b>ʟᴏɴɢɪᴛᴜᴅᴇ:</b> <code>{result['server']['lon']}</code>

➲ <b>ᴄʟɪᴇɴᴛ ᴅᴇᴛᴀɪʟs</b>
┠ <b>ɪᴘ ᴀᴅᴅʀᴇss:</b> <code>{result['client']['ip']}</code>
┠ <b>ʟᴀᴛɪᴛᴜᴅᴇ:</b> <code>{result['client']['lat']}</code>
┠ <b>ʟᴏɴɢɪᴛᴜᴅᴇ:</b> <code>{result['client']['lon']}</code>
┠ <b>ᴄᴏᴜɴᴛʀʏ:</b> <code>{result['client']['country']}</code>
┠ <b>ɪsᴘ:</b> <code>{result['client']['isp']}</code>
┖ <b>ɪsᴘ ʀᴀᴛɪɴɢ:</b> <code>{result['client']['isprating']}</code>

🌍 <b><a href='https://t.me/infinity_botzz'>@ɪɴꜰɪɴɪᴛʏ_ʙᴏᴛᴢᴢ</a></b>'''

    await message.reply_photo(photo=photo, caption=text)
    await msg.delete()

@Client.on_message(filters.command("info"))
async def who_is(client, message):
    status_message = await message.reply_text("<b>🔍 ꜰᴇᴛᴄʜɪɴɢ ᴜsᴇʀ ᴅᴀᴛᴀ...</b>")

    if len(message.command) > 1:
        input_data = message.command[1]
        from_user_id = int(input_data) if input_data.isnumeric() else input_data
    elif message.reply_to_message:
        from_user_id = message.reply_to_message.from_user.id
    else:
        from_user_id = message.from_user.id

    try:
        from_user = await client.get_users(from_user_id)
    except Exception as error:
        return await status_message.edit(f'<b>❌ ᴇʀʀᴏʀ:</b> <code>{error}</code>')

    last_name = from_user.last_name or 'ɴᴏɴᴇ'
    username = f"@{from_user.username}" if from_user.username else 'ɴᴏɴᴇ'
    dc_id = from_user.dc_id or 'ɴ/ᴀ'
    
    message_out_str = (
        f"✨ <b>ᴜsᴇʀ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ</b>\n\n"
        f"➲ <b>ꜰɪʀsᴛ ɴᴀᴍᴇ:</b> {from_user.first_name}\n"
        f"➲ <b>ʟᴀsᴛ ɴᴀᴍᴇ:</b> {last_name}\n"
        f"➲ <b>ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ:</b> <code>{from_user.id}</code>\n"
        f"➲ <b>ᴜsᴇʀɴᴀᴍᴇ:</b> {username}\n"
        f"➲ <b>ᴅᴄ ɪᴅ:</b> <code>{dc_id}</code>\n"
        f"➲ <b>sᴛᴀᴛᴜs:</b> <code>{last_online(from_user)}</code>\n"
        f"➲ <b>ᴜsᴇʀ ʟɪɴᴋ:</b> <a href='tg://user?id={from_user.id}'><b>ᴄʟɪᴄᴋ ʜᴇʀᴇ</b></a>\n"
    )

    if message.chat.type in [enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]:
        try:
            chat_member = await message.chat.get_member(from_user.id)
            if chat_member.joined_date:
                joined_date = chat_member.joined_date.strftime('%Y-%m-%d %H:%M')
                message_out_str += f"➲ <b>ᴊᴏɪɴᴇᴅ ʜᴇʀᴇ:</b> <code>{joined_date}</code>\n"
        except Exception:
            pass

    if from_user.photo:
        local_user_photo = await client.download_media(message=from_user.photo.big_file_id)
        await message.reply_photo(photo=local_user_photo, caption=message_out_str, quote=True)
        if os.path.exists(local_user_photo):
            os.remove(local_user_photo)
    else:
        await message.reply_text(text=message_out_str, quote=True)
        
    await status_message.delete()

def last_online(from_user):
    if from_user.is_bot:
        return "🤖 ʙᴏᴛ"
    if from_user.status == enums.UserStatus.ONLINE:
        return "✅ ᴏɴʟɪɴᴇ"
    if from_user.status == enums.UserStatus.RECENTLY:
        return "🕒 ʀᴇᴄᴇɴᴛʟʏ"
    if from_user.status == enums.UserStatus.LAST_WEEK:
        return "📅 ᴡɪᴛʜɪɴ ᴀ ᴡᴇᴇᴋ"
    if from_user.status == enums.UserStatus.LAST_MONTH:
        return "📅 ᴡɪᴛʜɪɴ ᴀ ᴍᴏɴᴛʜ"
    if from_user.status == enums.UserStatus.LONG_AGO:
        return "💤 ᴀ ʟᴏɴɢ ᴛɪᴍᴇ ᴀɢᴏ"
    if from_user.status == enums.UserStatus.OFFLINE:
        if from_user.last_online_date:
            return from_user.last_online_date.strftime("%d %b, %H:%M")
    return "ᴜɴᴋɴᴏᴡɴ"

@Client.on_message(filters.command('download'))
async def download_video(client, message):
    if len(message.command) > 1:
        link = message.command[1]
    else:
        return await message.reply("<b>💡 ᴜsᴀɢᴇ:</b> <code>/download video-url</code>")

    status_msg = await message.reply("<b>⏳ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")

    user_id = message.from_user.id
    downloaded_file = None
    thumbnail_file = None

    try:
        os.makedirs("yt_dlp_downloads", exist_ok=True)

        ydl_opts = {
            'outtmpl': f'yt_dlp_downloads/{user_id}_%(title)s.%(ext)s',
            'format': 'best',
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            title = info.get('title', 'Video')
            duration = info.get('duration', 0)
            thumbnail_url = info.get('thumbnail', None)
            downloaded_file = ydl.prepare_filename(info)

        if thumbnail_url:
            thumbnail_file = f"yt_dlp_downloads/{user_id}_thumb.jpg"
            async with httpx.AsyncClient() as http:
                response = await http.get(thumbnail_url)
                with open(thumbnail_file, 'wb') as f:
                    f.write(response.content)

        await status_msg.edit("<b>📤 ᴜᴘʟᴏᴀᴅɪɴɢ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ...</b>")

        await client.send_video(
            chat_id=message.chat.id,
            video=downloaded_file,
            caption=f"🎬 <b>{title}</b>\n\n🌍 <b><a href='https://t.me/infinity_botzz'>@ɪɴꜰɪɴɪᴛʏ_ʙᴏᴛᴢᴢ</a></b>",
            duration=duration,
            thumb=thumbnail_file,
            reply_parameters=ReplyParameters(message_id=message.id),
        )

        await status_msg.delete()

    except yt_dlp.utils.DownloadError as e:
        await status_msg.edit(f"<b>❌ ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ:</b>\n<code>{str(e)}</code>")

    except Exception as e:
        await status_msg.edit(f"<b>❌ ᴇʀʀᴏʀ:</b>\n<code>{str(e)}</code>")

    finally:
        if downloaded_file and os.path.exists(downloaded_file):
            os.remove(downloaded_file)
        if thumbnail_file and os.path.exists(thumbnail_file):
            os.remove(thumbnail_file)