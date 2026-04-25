import os
import time
import asyncio
import logging
from aiohttp import web
from typing import Union, Optional, AsyncGenerator
from pyrogram import types, Client, StopPropagation
from pyrogram.handlers import MessageHandler

# Aapke existing imports
from web import web_app
from database.users_chats_db import db
from utils import temp, check_premium
from info import (
    URL, LOG_CHANNEL, API_ID, API_HASH, BOT_TOKEN, 
    PORT, ADMINS
)

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logging.getLogger('pyrogram').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

try:
    import uvloop
    uvloop.install()
except ImportError:
    pass

class Bot(Client):
    def __init__(self):
        super().__init__(
            name='Auto_Filter_Bot',
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins={"root": "plugins"},
            workers=50,             # Optimized for Koyeb
            sleep_threshold=30      # Floodwait handling
        )
        self.listeners = {}
        # Listener handler ko group -1 par rakha hai taaki ye sabse pehle chale
        self.add_handler(MessageHandler(self._listener_handler), group=-1)

    async def _listener_handler(self, client: Client, message: types.Message):
        # Basic checks to avoid crashes
        if not message.from_user:
            return
        
        listener_id = (message.chat.id, message.from_user.id)
        if listener_id in self.listeners:
            future = self.listeners[listener_id]
            if not future.done():
                future.set_result(message)
                # Sirf tab stop karein jab listener active ho
                raise StopPropagation

    async def listen(self, chat_id: int, user_id: int, timeout: int = 60) -> Optional[types.Message]:
        future = asyncio.get_event_loop().create_future()
        listener_id = (chat_id, user_id)
        
        # Purane pending listener ko hatayein
        if listener_id in self.listeners:
            old_future = self.listeners[listener_id]
            if not old_future.done():
                old_future.cancel()
                
        self.listeners[listener_id] = future
        
        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            return None
        finally:
            self.listeners.pop(listener_id, None)

    async def start(self, **kwargs):
        await super().start()
        temp.START_TIME = time.time()
        
        # Database loading with fallback
        try:
            b_users, b_chats = await db.get_banned()
            temp.BANNED_USERS = b_users
            temp.BANNED_CHATS = b_chats
        except Exception as e:
            logger.error(f"Error loading banned list: {e}")

        # Restart message handling
        if os.path.exists('restart.txt'):
            try:
                with open("restart.txt") as file:
                    chat_id, msg_id = map(int, file.read().split())
                await self.edit_message_text(chat_id=chat_id, message_id=msg_id, text='**Restarted Successfully! ✅**')
                os.remove('restart.txt')
            except Exception as e:
                logger.debug(f"Restart file error: {e}")

        # Bot Info Setup
        temp.BOT = self
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        
        # --- Web Server Setup ---
        runner = web.AppRunner(web_app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()

        # Premium check & Background Tasks
        asyncio.create_task(check_premium(self))
        
        # Notification Log
        try:
            await self.send_message(chat_id=LOG_CHANNEL, text=f"<b>{me.mention} Is Online Now! 🚀</b>")
        except Exception as e:
            logger.warning(f"Could not send start message to LOG_CHANNEL: {e}")

        # Admin Notification
        for admin in ADMINS:
            try:
                await self.send_message(admin, "<b>๏[-ิ_•ิ]๏ sʏsᴛᴇᴍ ʀᴇsᴛᴀʀᴛᴇᴅ ✅</b>")
            except:
                continue

        logger.info(f"@{me.username} Started Successfully ✓")

    async def stop(self, **kwargs):
        await super().stop()
        logger.info("Bot Stopped! Bye...")

    async def iter_messages(self, chat_id: Union[int, str], limit: int, offset: int = 0) -> Optional[AsyncGenerator[types.Message, None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            try:
                messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
                for message in messages:
                    yield message
                    current += 1
            except Exception as e:
                logger.error(f"Error in iter_messages: {e}")
                break

app = Bot()
app.run()