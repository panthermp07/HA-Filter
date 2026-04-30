import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from motor.motor_asyncio import AsyncIOMotorClient
from info import ADMINS

@Client.on_message(filters.command("clearmongo") & filters.user(ADMINS))
async def clear_mongo(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ.\nᴜsᴇ: `/clearmongo <mongourl>`")
    
    url = message.text.split(" ", 1)[1]
    msg = await message.reply_text("🔄 ᴘʀᴏᴄᴇssɪɴɢ...")
    
    try:
        mongo_client = AsyncIOMotorClient(url, serverSelectionTimeoutMS=5000)
        await mongo_client.server_info()
        
        db_names = await mongo_client.list_database_names()
        for db_name in db_names:
            if db_name not in ['admin', 'local', 'config']:
                await mongo_client.drop_database(db_name)
                
        await msg.edit_text("✅ ᴀʟʟ ᴍᴏɴɢᴏ ᴅᴀᴛᴀ ᴄʟᴇᴀʀᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.")
    except Exception as e:
        await msg.edit_text(f"❌ ᴇʀʀᴏʀ:\n`{e}`")


@Client.on_message(filters.command("clonemongo") & filters.user(ADMINS))
async def clone_mongo(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("⚠️ ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ.\nᴜsᴇ: `/clonemongo <oldurl> <newurl>`")
    
    args = message.text.split(" ")
    old_url = args[1]
    new_url = args[2]
    
    msg = await message.reply_text("🔄 ᴄʟᴏɴɪɴɢ ɪɴ ᴘʀᴏɢʀᴇss... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.")
    
    try:
        old_client = AsyncIOMotorClient(old_url, serverSelectionTimeoutMS=5000)
        new_client = AsyncIOMotorClient(new_url, serverSelectionTimeoutMS=5000)
        
        await old_client.server_info()
        await new_client.server_info()
        
        db_names = await old_client.list_database_names()
        for db_name in db_names:
            if db_name in ['admin', 'local', 'config']:
                continue
            
            db_old = old_client[db_name]
            db_new = new_client[db_name]
            
            collections = await db_old.list_collection_names()
            for col_name in collections:
                col_old = db_old[col_name]
                col_new = db_new[col_name]
                
                cursor = col_old.find({})
                batch = []
                async for doc in cursor:
                    batch.append(doc)
                    if len(batch) >= 500:
                        await col_new.insert_many(batch)
                        batch.clear()
                
                if batch:
                    await col_new.insert_many(batch)
                    
        await msg.edit_text("✅ ᴍᴏɴɢᴏᴅʙ ᴄʟᴏɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴛᴏ ɴᴇᴡ ᴜʀʟ.")
    except Exception as e:
        await msg.edit_text(f"❌ ᴇʀʀᴏʀ:\n`{e}`")


@Client.on_message(filters.command("mongoinfo") & filters.user(ADMINS))
async def mongo_info(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ.\nᴜsᴇ: `/mongoinfo <mongourl>`")
    
    url = message.text.split(" ", 1)[1]
    msg = await message.reply_text("🔄 ғᴇᴛᴄʜɪɴɢ ɪɴғᴏ...")
    
    try:
        mongo_client = AsyncIOMotorClient(url, serverSelectionTimeoutMS=5000)
        await mongo_client.server_info()
        
        info_text = "📊 **ᴍᴏɴɢᴏᴅʙ ɪɴғᴏʀᴍᴀᴛɪᴏɴ**\n\n"
        db_names = await mongo_client.list_database_names()
        
        for db_name in db_names:
            if db_name in ['admin', 'local', 'config']:
                continue
            
            info_text += f"📁 **{db_name}**\n"
            db = mongo_client[db_name]
            collections = await db.list_collection_names()
            
            for col_name in collections:
                count = await db[col_name].count_documents({})
                info_text += f"   └ 📄 `{col_name}` : {count} ᴅᴏᴄs\n"
                
        if info_text == "📊 **ᴍᴏɴɢᴏᴅʙ ɪɴғᴏʀᴍᴀᴛɪᴏɴ**\n\n":
            info_text += "ᴇᴍᴘᴛʏ ᴅᴀᴛᴀʙᴀsᴇ!"
            
        await msg.edit_text(info_text)
    except Exception as e:
        await msg.edit_text(f"❌ ᴇʀʀᴏʀ:\n`{e}`")


@Client.on_message(filters.command("delcol") & filters.user(ADMINS))
async def del_col(client: Client, message: Message):
    if len(message.command) < 4:
        return await message.reply_text("⚠️ <b>ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ.</b>\n💡 ᴜsᴇ: <code>/delcol [mongourl] [dbname] [collection]</code>")
    
    args = message.text.split(" ")
    url = args[1]
    db_name = args[2]
    col_name = args[3]
    
    msg = await message.reply_text("🔄 ᴘʀᴏᴄᴇssɪɴɢ...")
    
    try:
        mongo_client = AsyncIOMotorClient(url, serverSelectionTimeoutMS=5000)
        await mongo_client.server_info()
        
        db = mongo_client[db_name]
        await db.drop_collection(col_name)
        
        await msg.edit_text(f"✅ ᴄᴏʟʟᴇᴄᴛɪᴏɴ `{col_name}` ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ `{db_name}`.")
    except Exception as e:
        await msg.edit_text(f"❌ ᴇʀʀᴏʀ:\n`{e}`")