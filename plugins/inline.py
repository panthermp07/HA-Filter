from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument, InlineQuery
from utils import get_size, temp, get_verify_status, is_subscribed, is_premium, handle_next_back
from database.ia_filterdb import get_search_results
from info import CACHE_TIME, SUPPORT_LINK, UPDATES_LINK, FILE_CAPTION, IS_VERIFY, MAX_BTN

cache_time = CACHE_TIME

def is_banned(query: InlineQuery):
    return query.from_user and query.from_user.id in temp.BANNED_USERS

@Client.on_inline_query()
async def inline_search(bot, query):
    """Show search results for given inline query"""

    # 1. Force Sub Check
    is_fsub = await is_subscribed(bot, query)
    if is_fsub:
        await query.answer(
            results=[],
            cache_time=0,
            switch_pm_text="⚠️ ᴊᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ꜰɪʀsᴛ",
            switch_pm_parameter="inline_fsub"
        )
        return

    # 2. Verification & Premium Check
    verify_status = await get_verify_status(query.from_user.id)
    if IS_VERIFY and not verify_status['is_verified'] and not await is_premium(query.from_user.id, bot):
        await query.answer(
            results=[],
            cache_time=0,
            switch_pm_text="🔒 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪꜰɪᴇᴅ ᴛᴏᴅᴀʏ",
            switch_pm_parameter="inline_verify"
        )
        return
    
    # 3. Banned User Check
    if is_banned(query):
        await query.answer(
            results=[],
            cache_time=0,
            switch_pm_text="🚫 ʏᴏᴜ ᴀʀᴇ ᴀ ʙᴀɴɴᴇᴅ ᴜsᴇʀ",
            switch_pm_parameter="start"
        )
        return

    # 4. Fetching Results
    results = []
    string = query.query
    offset = int(query.offset or 0)
    files = await get_search_results(string)
    files, next_offset, total = await handle_next_back(files, offset=offset, max_results=MAX_BTN)

    for file in files:
        reply_markup = get_reply_markup(string)
        f_caption = FILE_CAPTION.format(
            file_name=file['file_name'],
            file_size=get_size(file['file_size']),
            caption=file['caption']
        )
        results.append(
            InlineQueryResultCachedDocument(
                title=file['file_name'],
                document_file_id=file['_id'],
                caption=f_caption,
                description=f"sɪᴢᴇ ⠂{get_size(file['file_size'])}",
                reply_markup=reply_markup
            )
        )

    # 5. Displaying Results
    if results:
        switch_pm_text = f"🗂 ʀᴇsᴜʟᴛs ⠂{total}"
        if string:
            switch_pm_text += f" ꜰᴏʀ ⠂{string}"
            
        await query.answer(
            results=results,
            is_personal=True,
            cache_time=cache_time,
            switch_pm_text=switch_pm_text,
            switch_pm_parameter="start",
            next_offset=str(next_offset)
        )
    else:
        switch_pm_text = "❌ ɴᴏ ʀᴇsᴜʟᴛs ꜰᴏᴜɴᴅ"
        if string:
            switch_pm_text += f" ꜰᴏʀ ⠂{string}"
            
        await query.answer(
            results=[],
            is_personal=True,
            cache_time=cache_time,
            switch_pm_text=switch_pm_text,
            switch_pm_parameter="start"
        )

def get_reply_markup(s):
    buttons = [[
        InlineKeyboardButton('🔎 sᴇᴀʀᴄʜ ᴀɢᴀɪɴ 🔍', switch_inline_query_current_chat=s or '')
    ],[
        InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇs', url=UPDATES_LINK),
        InlineKeyboardButton('🛠️ sᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
    ]]
    return InlineKeyboardMarkup(buttons)