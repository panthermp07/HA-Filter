import motor.motor_asyncio
from pyrogram import Client, filters
from info import ADMINS

@Client.on_message(filters.command("cleardb") & filters.private)
async def clear_database(client, message):
    # ⚠️ SECURITY CHECK: Sirf Admins is command ko use kar sakte hain
    if message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ!\n\nʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.</b>")

    if len(message.command) < 2:
        return await message.reply("<b>⚠️ ᴜsᴀɢᴇ:</b>\n<code>/cleardb [MONGODB_URL]</code>\n\n<i>Note: Message bhejte hi turant delete kar dena security ke liye!</i>")

    mongo_url = message.command[1]
    
    status_msg = await message.reply("<b>⏳ ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴅᴀᴛᴀʙᴀsᴇ...</b>")

    try:
        # Async connection banayein (Bot ko hang hone se bachane ke liye)
        db_client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
        
        # Connection test karein
        await db_client.server_info() 
        
        await status_msg.edit("<b>⚠️ ᴡᴀʀɴɪɴɢ: ᴅᴇʟᴇᴛɪɴɢ ᴀʟʟ ᴅᴀᴛᴀʙᴀsᴇs... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ!</b>")
        
        # Saare databases ki list nikalein
        db_names = await db_client.list_database_names()
        
        deleted_dbs = []
        for db_name in db_names:
            # System databases ko chod kar baaki sab uda dein
            if db_name not in ['admin', 'local', 'config']:
                await db_client.drop_database(db_name)
                deleted_dbs.append(db_name)
                
        if deleted_dbs:
            await status_msg.edit(
                f"<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ᴅᴀᴛᴀʙᴀsᴇs:</b>\n"
                f"<code>{', '.join(deleted_dbs)}</code>\n\n"
                f"🚀 <b>sᴀᴀʀᴀ ᴅᴀᴛᴀ sᴀᴀꜰ ʜᴏ ɢᴀʏᴀ ʜᴀɪ!</b>\n\n"
                f"<i>⚠️ P.S. Ab jaldi se apne '/cleardb' wale message ko Telegram se delete kar do!</i>"
            )
        else:
            await status_msg.edit("<b>✅ ɴᴏ ᴄᴜsᴛᴏᴍ ᴅᴀᴛᴀʙᴀsᴇs ꜰᴏᴜɴᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ.</b>")
            
    except Exception as e:
        await status_msg.edit(f"<b>❌ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ:</b>\n<code>{e}</code>\n\n<i>Check if your MongoDB URL and password are correct.</i>")