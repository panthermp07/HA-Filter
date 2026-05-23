import os
import time
import asyncio
import logging
from aiohttp import web
from datetime import datetime, timedelta
from typing import Union, Optional, AsyncGenerator
from pyrogram import types, Client, StopPropagation
from pyrogram.handlers import MessageHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from web import web_app
from database.users_chats_db import db
from database.ia_filterdb import setup_database
from utils import temp, check_premium
from info import (
    URL, LOG_CHANNEL, API_ID, API_HASH, BOT_TOKEN, 
    PORT, ADMINS, TIME_ZONE, VERIFICATION_NOTIFY_CHANNEL, BOT_ID
)

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logging.getLogger('pyrogram').setLevel(logging.ERROR)
logging.getLogger('aiohttp').setLevel(logging.WARNING)
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
            workers=50,             # Faster updates processing
            sleep_threshold=30      # Auto-handle flood waits up to 30s
        )
        self.listeners = {}
        self.add_handler(MessageHandler(self._listener_handler), group=-1)

    async def _listener_handler(self, client: Client, message: types.Message):
        if not message.chat or not message.from_user:
            return
        
        listener_id = (message.chat.id, message.from_user.id)
        if listener_id in self.listeners:
            future = self.listeners[listener_id]
            if not future.done():
                future.set_result(message)
                raise StopPropagation

    async def listen(self, chat_id: int, user_id: int, timeout: int = 60) -> Optional[types.Message]:
        future = asyncio.get_event_loop().create_future()
        listener_id = (chat_id, user_id)
        
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
        logger.info('sᴇᴛᴛɪɴɢ ᴜᴘ ʏᴏᴜʀ ᴅᴀᴛᴀʙᴀsᴇ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ...')
        await setup_database()
        logger.info('sᴜᴄᴄᴇssꜰᴜʟʟʏ sᴇᴛᴜᴘ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ! ✅')
        
        await super().start()
        temp.START_TIME = time.time()
        
        try:
            b_users, b_chats = await db.get_banned()
            temp.BANNED_USERS = b_users
            temp.BANNED_CHATS = b_chats
        except Exception as e:
            logger.error(f"Error loading banned list: {e}")

        if os.path.exists('restart.txt'):
            try:
                with open("restart.txt") as file:
                    chat_id, msg_id = map(int, file.read().split())
                await self.edit_message_text(chat_id=chat_id, message_id=msg_id, text='<b>ʀᴇsᴛᴀʀᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ! ✅</b>')
                os.remove('restart.txt')
            except Exception as e:
                logger.debug(f"Restart file error: {e}")

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

        # Premium check Background Task
        asyncio.create_task(check_premium(self))
        
        # --- ELITE AUTOMATION SCHEDULER ---
        scheduler = AsyncIOScheduler(timezone=TIME_ZONE)
        
        # 1. Midnight Report (11:59 PM)
        scheduler.add_job(self.send_daily_report, "cron", hour=23, minute=59)
        
        # 2. Automated Analytics Cleanup (Weekly on Sunday)
        scheduler.add_job(self.cleanup_old_analytics, "cron", day_of_week='sun', hour=0, minute=0)
        
        scheduler.start()
        logger.info("ᴇʟɪᴛᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴏɴ sᴄʜᴇᴅᴜʟᴇʀ sᴛᴀʀᴛᴇᴅ ✓")

        try:
            await self.send_message(chat_id=LOG_CHANNEL, text=f"<b>{me.mention} ɪs ᴏɴʟɪɴᴇ ɴᴏᴡ! 🚀</b>")
        except Exception as e:
            logger.error("Make sure bot is admin in LOG_CHANNEL, exiting now.")
            exit()

        for admin in ADMINS:
            try:
                await self.send_message(admin, "<b>๏[-ิ_•ิ]๏ sʏsᴛᴇᴍ ʀᴇsᴛᴀʀᴛᴇᴅ ✅</b>")
            except:
                continue

        logger.info(f"Bot [@{me.username}] and webapp [{URL}] started successfully ✓")

    async def stop(self, **kwargs):
        await super().stop()
        logger.info("ʙᴏᴛ sᴛᴏᴘᴘᴇᴅ! ʙʏᴇ...")

    async def send_daily_report(self):
        all_sh = await db.get_all_shorteners()
        today = datetime.now().strftime("%Y-%m-%d")
        
        report = f"<b>🌙 ᴅᴀɪʟʏ ɴᴇᴛᴡᴏʀᴋ sᴜᴍᴍᴀʀʏ ({today})</b>\n"
        report += "<code>━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        
        total_clicks = 0
        for sh in all_sh:
            clicks = sh.get(f'clicks_{today}', 0)
            total_clicks += clicks
            report += f"🌐 <b>{sh['site']}</b>: <code>{clicks}</code>\n"
        
        report += f"\n📊 <b>ᴛᴏᴛᴀʟ ᴅᴀɪʟʏ ᴄʟɪᴄᴋs:</b> <code>{total_clicks}</code>\n"
        report += "<code>━━━━━━━━━━━━━━━━━━━━━━━</code>"

        for admin in ADMINS:
            try:
                await self.send_message(admin, report)
            except:
                pass
        if VERIFICATION_NOTIFY_CHANNEL:
            try:
                await self.send_message(VERIFICATION_NOTIFY_CHANNEL, report)
            except:
                pass

    async def cleanup_old_analytics(self):
        old_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        try:
            await db.stg.update_many(
                {'id': BOT_ID},
                {'$unset': {f'shortener_list.$.clicks_{old_date}': ""}}
            )
            logger.info(f"Cleaned up analytics for {old_date}")
        except Exception as e:
            logger.error(f"Cleanup Error: {e}")

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