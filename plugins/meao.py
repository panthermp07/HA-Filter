from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import BulkWriteError
from info import ADMINS  # Dekho, yahan se DATABASE_NAME hata diya gaya hai
import asyncio

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🟢 1. CLONE MONGO (OLD URL to NEW URL)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("clonemongo") & filters.user(ADMINS))
async def clone_mongo_cmd(bot, message):
    if len(message.command) != 3:
        return await message.reply("<b>💡 ᴜsᴀɢᴇ:</b> <code>/clonemongo [OLD_URL] [NEW_URL]</code>\n\n⚠️ <i>URL ke end mein DB name zaroor lagayein. Example: mongodb+srv://.../MyDatabase</i>")

    old_url = message.command[1]
    new_url = message.command[2]
    
    status_msg = await message.reply("<b>⏳ ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴅᴀᴛᴀʙᴀsᴇs...</b>")
    
    try:
        old_client = AsyncIOMotorClient(old_url)
        new_client = AsyncIOMotorClient(new_url)
        
        # 🟢 SMART LOGIC: URL se khud Database name nikalega
        try:
            old_db = old_client.get_default_database()
            new_db = new_client.get_default_database()
        except Exception:
            return await status_msg.edit("<b>❌ ᴇʀʀᴏʀ:</b> ᴘʟᴇᴀsᴇ ɪɴᴄʟᴜᴅᴇ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ ɴᴀᴍᴇ ɪɴ ʏᴏᴜʀ ᴜʀʟs!\nExample: <code>mongodb+srv://.../DB_NAME</code>")
        
        colls = await old_db.list_collection_names()
        if not colls:
            return await status_msg.edit("<b>❌ ɴᴏ ᴄᴏʟʟᴇᴄᴛɪᴏɴs ꜰᴏᴜɴᴅ ɪɴ ᴏʟᴅ ᴅᴀᴛᴀʙᴀsᴇ.</b>")
            
        report = f"<b>📂 ᴄʟᴏɴɪɴɢ sᴛᴀʀᴛᴇᴅ!</b>\nꜰᴏᴜɴᴅ {len(colls)} ᴄᴏʟʟᴇᴄᴛɪᴏɴs ɪɴ <code>{old_db.name}</code>.\n\n"
        await status_msg.edit(report)
        
        total_docs = 0
        for coll_name in colls:
            old_col = old_db[coll_name]
            new_col = new_db[coll_name]
            
            cursor = old_col.find({})
            batch = []
            coll_migrated = 0
            
            async for doc in cursor:
                batch.append(doc)
                if len(batch) >= 1500:
                    try:
                        await new_col.insert_many(batch, ordered=False)
                    except BulkWriteError:
                        pass
                    coll_migrated += len(batch)
                    batch = []
                    
            if batch:
                try:
                    await new_col.insert_many(batch, ordered=False)
                except BulkWriteError:
                    pass
                coll_migrated += len(batch)
                
            total_docs += coll_migrated
            report += f"✅ <code>{coll_name}</code>: {coll_migrated} ᴅᴏᴄs\n"
            try:
                await status_msg.edit(report + "\n<b>⏳ ᴘʀᴏᴄᴇssɪɴɢ ɴᴇxᴛ...</b>")
            except:
                pass
                
        await status_msg.edit(f"{report}\n<b>✅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴄʟᴏɴᴇᴅ {total_docs} ᴅᴏᴄᴜᴍᴇɴᴛs ᴛᴏ <code>{new_db.name}</code>!</b>\n\n⚠️ <i>ᴘʟᴇᴀsᴇ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴄᴏᴍᴍᴀɴᴅ ᴍᴇssᴀɢᴇ ᴛᴏ ʜɪᴅᴇ ᴜʀʟs.</i>")
        
    except Exception as e:
        await status_msg.edit(f"<b>❌ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ:</b>\n<code>{str(e)}</code>")
    finally:
        try:
            old_client.close()
            new_client.close()
        except: pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🟢 2. MONGO INFO (Check DB Stats)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("monginfo") & filters.user(ADMINS))
async def mongo_info_cmd(bot, message):
    if len(message.command) != 2:
        return await message.reply("<b>💡 ᴜsᴀɢᴇ:</b> <code>/monginfo [MONGO_URL]</code>")
        
    url = message.command[1]
    status_msg = await message.reply("<b>⏳ ꜰᴇᴛᴄʜɪɴɢ ᴅᴀᴛᴀʙᴀsᴇ ɪɴꜰᴏ...</b>")
    
    try:
        client = AsyncIOMotorClient(url, serverSelectionTimeoutMS=5000)
        try:
            db = client.get_default_database()
        except Exception:
            return await status_msg.edit("<b>❌ ᴇʀʀᴏʀ:</b> ᴘʟᴇᴀsᴇ ɪɴᴄʟᴜᴅᴇ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ ɴᴀᴍᴇ ɪɴ ʏᴏᴜʀ ᴜʀʟ!\nExample: <code>mongodb+srv://.../DB_NAME</code>")
        
        colls = await db.list_collection_names()
        if not colls:
            return await status_msg.edit(f"<b>⚠️ ᴅᴀᴛᴀʙᴀsᴇ <code>{db.name}</code> ɪs ᴇᴍᴘᴛʏ!</b>")
            
        report = f"<b>📊 ᴍᴏɴɢᴏᴅʙ sᴛᴀᴛɪsᴛɪᴄs ꜰᴏʀ <code>{db.name}</code>:</b>\n<code>━━━━━━━━━━━━━━━━━━</code>\n\n"
        total_docs = 0
        
        for coll_name in colls:
            count = await db[coll_name].count_documents({})
            total_docs += count
            report += f"⠂ <b>{coll_name}</b>: <code>{count}</code> ᴅᴏᴄs\n"
            
        report += f"\n<code>━━━━━━━━━━━━━━━━━━</code>\n<b>📈 ᴛᴏᴛᴀʟ ᴅᴏᴄᴜᴍᴇɴᴛs:</b> <code>{total_docs}</code>"
        
        await status_msg.edit(report)
    except Exception as e:
        await status_msg.edit(f"<b>❌ ᴇʀʀᴏʀ ᴄᴏɴɴᴇᴄᴛɪɴɢ:</b>\n<code>{str(e)}</code>")
    finally:
        try: client.close()
        except: pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🟢 3. DELETE MONGO COLLECTION (Remove Specific Col)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("delmongocol") & filters.user(ADMINS))
async def del_mongo_col_cmd(bot, message):
    if len(message.command) != 3:
        return await message.reply("<b>💡 ᴜsᴀɢᴇ:</b> <code>/delmongocol [MONGO_URL] [COLLECTION_NAME]</code>")
        
    url = message.command[1]
    col_name = message.command[2]
    
    status_msg = await message.reply(f"<b>⏳ ᴅᴇʟᴇᴛɪɴɢ ᴄᴏʟʟᴇᴄᴛɪᴏɴ '{col_name}'...</b>")
    
    try:
        client = AsyncIOMotorClient(url)
        try:
            db = client.get_default_database()
        except Exception:
            return await status_msg.edit("<b>❌ ᴇʀʀᴏʀ:</b> ᴘʟᴇᴀsᴇ ɪɴᴄʟᴜᴅᴇ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ ɴᴀᴍᴇ ɪɴ ʏᴏᴜʀ ᴜʀʟ!")
        
        colls = await db.list_collection_names()
        if col_name not in colls:
            return await status_msg.edit(f"<b>❌ ᴄᴏʟʟᴇᴄᴛɪᴏɴ '{col_name}' ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ <code>{db.name}</code>!</b>")
            
        await db.drop_collection(col_name)
        await status_msg.edit(f"<b>✅ ᴄᴏʟʟᴇᴄᴛɪᴏɴ '{col_name}' sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ꜰʀᴏᴍ <code>{db.name}</code>!</b>")
        
    except Exception as e:
        await status_msg.edit(f"<b>❌ ᴇʀʀᴏʀ:</b>\n<code>{str(e)}</code>")
    finally:
        try: client.close()
        except: pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🟢 4. CLEAR FULL DATABASE (DANGER ZONE)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@Client.on_message(filters.command("cleardb") & filters.user(ADMINS))
async def clear_db_cmd(bot, message):
    if len(message.command) != 2:
        return await message.reply("<b>💡 ᴜsᴀɢᴇ:</b> <code>/cleardb [MONGO_URL]</code>")
        
    url = message.command[1]
    status_msg = await message.reply("<b>⏳ ᴄʟᴇᴀʀɪɴɢ ᴇɴᴛɪʀᴇ ᴅᴀᴛᴀʙᴀsᴇ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>")
    
    try:
        client = AsyncIOMotorClient(url)
        try:
            db = client.get_default_database()
        except Exception:
            return await status_msg.edit("<b>❌ ᴇʀʀᴏʀ:</b> ᴘʟᴇᴀsᴇ ɪɴᴄʟᴜᴅᴇ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ ɴᴀᴍᴇ ɪɴ ʏᴏᴜʀ ᴜʀʟ!\nExample: <code>mongodb+srv://.../DB_NAME</code>")
        
        colls = await db.list_collection_names()
        if not colls:
            return await status_msg.edit(f"<b>⚠️ ᴅᴀᴛᴀʙᴀsᴇ <code>{db.name}</code> ɪs ᴀʟʀᴇᴀᴅʏ ᴇᴍᴘᴛʏ!</b>")
            
        for coll_name in colls:
            await db.drop_collection(coll_name)
            
        await status_msg.edit(f"<b>✅ ᴅᴀᴛᴀʙᴀsᴇ <code>{db.name}</code> sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴄʟᴇᴀʀᴇᴅ! ᴀʟʟ ᴄᴏʟʟᴇᴄᴛɪᴏɴs ᴅʀᴏᴘᴘᴇᴅ.</b>")
        
    except Exception as e:
        await status_msg.edit(f"<b>❌ ᴇʀʀᴏʀ:</b>\n<code>{str(e)}</code>")
    finally:
        try: client.close()
        except: pass