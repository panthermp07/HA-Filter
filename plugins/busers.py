from pyrogram.raw.types import UpdateBotStopped
from database.users_chats_db import db
import logging
from pyrogram import Client, ContinuePropagation

@Client.on_raw_update(group=-15)
async def blocked_user_handler(client, update, users, chats):
    if isinstance(update, UpdateBotStopped):
        user_id = update.user_id
        
        if update.stopped:
            await db.delete_user(user_id)
            logging.info(f"🚫 {user_id} - Removed from DB (User blocked the bot)")
        else:
            if not await db.is_user_exist(user_id):
                await db.add_user(user_id)
                logging.info(f"✅ {user_id} - Added back to DB (User unblocked the bot)")
    raise ContinuePropagation