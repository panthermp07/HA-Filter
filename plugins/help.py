import random
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import PICS, OWNER_USERNAME, SUPPORT_LINK
from utils import temp

# --- PROFESSIONAL UI DECORATION ---
HELP_HOME = (
    "<b>╔═══════『 ɪɴꜰɪɴɪᴛʏ ᴍᴜʟᴛɪ-ʙᴏᴛ 』══════╗</b>\n\n"
    "👋 ʜᴇʏ {mention},\n\n"
    "ɪɴꜰɪɴɪᴛʏ ᴍᴜʟᴛɪ-ꜰᴜɴᴄᴛɪᴏɴᴀʟ ʙᴏᴛ ᴍᴇ ᴀᴀᴘᴋᴀ sᴡᴀɢᴀᴛ ʜᴀɪ! 🚀\n"
    "ɪs ʙᴏᴛ ᴋᴏ sᴘᴇᴄɪᴀʟʟʏ <b>ᴀᴜᴛᴏ-ꜰɪʟᴛᴇʀ</b>, <b>ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b> ᴀᴜʀ <b>ᴇᴀʀɴɪɴɢ</b> "
    "ᴋᴇ ʟɪʏᴇ ᴅᴇsɪɢɴ ᴋɪʏᴀ ɢᴀʏᴀ ʜᴀɪ.\n\n"
    "✨ ɴɪᴄʜᴇ ᴅɪʏᴇ ɢᴀʏᴀ ʙᴜᴛᴛᴏɴs sᴇ ᴍᴇʀɪ <b>sᴜᴘᴇʀᴘᴏᴡᴇʀs</b> ᴋᴏ ᴇxᴘʟᴏʀᴇ ᴋᴀʀᴇɪɴ:\n\n"
    "📊 <b>sʏsᴛᴇᴍ sᴛᴀᴛᴜs:</b> <code>ᴏɴʟɪɴᴇ ✅</code>\n"
    "<b>╚════════════════════════╝</b>"
)

@Client.on_message(filters.command("help") & filters.incoming)
async def help_handler(bot, message):
    buttons = [
        [
            InlineKeyboardButton("🌟 ᴀʟʟ ᴜsᴇʀs", callback_data="h_user"),
            InlineKeyboardButton("👥 ɢʀᴏᴜᴘ ᴢᴏɴᴇ", callback_data="h_group")
        ],
        [
            InlineKeyboardButton("⚡ sᴜᴅᴏ ᴘᴏᴡᴇʀs", callback_data="h_sudo"),
            InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ & ᴇᴀʀɴ", callback_data="h_premium")
        ],
        [
            InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ ᴍᴇɴᴜ", callback_data="close_data", style=enums.ButtonStyle.DANGER)
        ]
    ]
    
    await message.reply_photo(
        photo=random.choice(PICS),
        caption=HELP_HOME.format(mention=message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons),
        effect_id=5104841245755180586
    )

@Client.on_callback_query(filters.regex(r"^h_"))
async def help_callback(bot, query):
    data = query.data.split("_")[1]
    
    # --- 1. ALL USERS & SETTINGS (commands.py & misc.py) ---
    if data == "user":
        help_text = (
            "<b>✨ 『 ᴀʟʟ ᴜsᴇʀ ᴄᴏᴍᴍᴀɴᴅs 』 ✨</b>\n\n"
            "➲ /start : ʙᴏᴛ ᴋᴏ ɪɴɪᴛɪᴀʟɪᴢᴇ ᴋᴀʀᴇɪɴ.\n"
            "➲ /id : ᴀᴘɴɪ ʏᴀ ᴋɪsɪ ᴜsᴇʀ/ᴄʜᴀᴛ ᴋɪ ᴜɴɪǫᴜᴇ ɪᴅ ɴɪᴋᴀʟᴇɪɴ.\n"
            "➲ /info : ᴜsᴇʀ ᴋɪ ᴘᴜʀɪ ᴅᴇᴛᴀɪʟs ᴀᴜʀ ᴘʀᴏꜰɪʟᴇ ᴄʜᴇᴄᴋ ᴋᴀʀᴇɪɴ.\n"
            "➲ /speedtest : ʙᴏᴛ ᴋᴇ sᴇʀᴠᴇʀ ᴋɪ sᴘᴇᴇᴅ ᴄʜᴇᴄᴋ ᴋᴀʀᴇɪɴ.\n"
            "➲ /refer : ᴅᴏsᴛᴏ ᴋᴏ ɪɴᴠɪᴛᴇ ᴋᴀʀᴇɪɴ ᴀᴜʀ ꜰʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ ᴘᴀʏᴇɪɴ.\n"
            "➲ /img2link : ᴋɪsɪ ʙʜɪ ᴘʜᴏᴛᴏ ᴋᴏ ᴜʀʟ ʟɪɴᴋ ᴍᴇɪɴ ᴄᴏɴᴠᴇʀᴛ ᴋᴀʀᴇɪɴ.\n"
            "➲ /settings : ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs manage ᴋᴀʀɴᴇ ᴋᴀ ᴍᴇɴᴜ.\n"
            "➲ /ping : ʙᴏᴛ ᴋɪ ʟᴀᴛᴇɴᴄʏ ᴄʜᴇᴄᴋ ᴋᴀʀᴇɪɴ.\n"
            "➲ /link : ᴍᴇᴅɪᴀ ꜰɪʟᴇ sᴇ sᴛʀᴇᴀᴍ/ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ ʙᴀɴᴀʏᴇɪɴ.\n\n"
            "💡 <i>ʏᴇ ᴄᴏᴍᴍᴀɴᴅs ᴋᴏɪ ʙʜɪ ᴜsᴇ ᴋᴀʀ sᴀᴋᴛᴀ ʜᴀɪ.</i>"
        )

    # --- 2. GROUP ZONE (group_management.py & p_ttishow.py) ---
    elif data == "group":
        help_text = (
            "<b>👥 『 ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ 』 👥</b>\n\n"
            "➲ /manage : ᴍᴜᴛᴇᴅ/ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs ᴋᴏ ᴇᴋ sᴀᴀᴛʜ sᴀᴀꜰ ᴋᴀʀᴇɪɴ.\n"
            "➲ /purge : ʜᴀᴢᴀʀᴏ ᴍᴇssᴀɢᴇs ᴇᴋ sᴀᴛʜ ᴅᴇʟᴇᴛᴇ ᴋᴀʀᴇɪɴ.\n"
            "➲ /ban | /mute : ʙᴀᴅ ᴇʟᴇᴍᴇɴᴛs ᴋᴏ ᴄᴏɴᴛʀᴏʟ ᴋᴀʀᴇɪɴ.\n"
            "➲ /unban | /unmute : ʀᴇsᴛʀɪᴄᴛɪᴏɴs ʀᴇᴍᴏᴠᴇ ᴋᴀʀᴇɪɴ.\n"
            "➲ /pin | /unpin : ɪᴍᴘᴏʀᴛᴀɴᴛ ᴍᴇssᴀɢᴇs ᴋᴏ highlight ᴋᴀʀᴇɪɴ.\n"
            "➲ /connect : ɢʀᴏᴜᴘ ᴋᴏ ʙᴏᴛ ᴘᴍ sᴇ ʟɪɴᴋ ᴋᴀʀᴇɪɴ.\n"
            "➲ /leave : ʙᴏᴛ ᴋᴏ ɢʀᴏᴜᴘ sᴇ ʟᴇᴀᴠᴇ ᴋᴀʀᴡᴀʏᴇɪɴ.\n"
            "➲ /ban_grp : ᴋɪsɪ ɢʀᴏᴜᴘ ᴋᴏ ʙʟᴀᴄᴋʟɪsᴛ ᴋᴀʀᴇɪɴ.\n"
            "➲ /unban_grp : ɢʀᴏᴜᴘ ᴋᴏ ʀᴇ-ᴇɴᴀʙʟᴇ ᴋᴀʀᴇɪɴ.\n"
            "➲ /invite_link : chat id se invite link generate karein.\n\n"
            "📌 <i>ɢʀᴏᴜᴘ ᴄᴏᴍᴍᴀɴᴅs ᴋᴇ ʟɪʏᴇ ᴀᴅᴍɪɴ ʜᴏɴᴀ ᴢᴀʀᴏᴏʀɪ ʜᴀɪ.</i>"
        )

    # --- 3. SUDO & OWNER POWERS (commands.py & p_ttishow.py) ---
    elif data == "sudo":
        help_text = (
            "<b>⚡ 『 sᴜᴅᴏ ᴇxᴄʟᴜsɪᴠᴇ ᴘᴏᴡᴇʀs 』 ⚡</b>\n\n"
            "➲ /add_prm : ᴋɪsɪ ʙʜɪ ᴜsᴇʀ ᴋᴏ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ᴅᴇɪɴ.\n"
            "➲ /rm_prm : ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ʀᴇᴍᴏᴠᴇ ᴋᴀʀᴇɪɴ.\n"
            "➲ /addsudo | /rmsudo : sᴜᴅᴏ ʟɪsᴛ ᴍᴀɴᴀɢᴇ ᴋᴀʀᴇɪɴ.\n"
            "➲ /stats : ʙᴏᴛ ᴋɪ ʟɪᴠᴇ ᴅᴀᴛᴀʙᴀsᴇ sᴛᴀᴛs dekhen.\n"
            "➲ /vstats : ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴀɴᴀʟʏᴛɪᴄs pro dekhen.\n"
            "➲ /prm_list : saare premium users ki list dekhen.\n"
            "➲ /users | /chats : saare users/chats ki list export karein.\n"
            "➲ /restart : ʙᴏᴛ ᴋᴏ ʀᴇʙᴏᴏᴛ ᴋᴀʀᴇɪɴ.\n"
            "➲ /index_channels : ɪɴᴅᴇxᴇᴅ ᴄʜᴀɴɴᴇʟs ᴋɪ ʟɪsᴛ ᴅᴇᴋʜᴇɪɴ.\n"
            "➲ /delete : database se files delete karein.\n\n"
            "📌 <i>ᴀɢᴀʀ ᴀᴀᴘᴋᴏ sᴜᴅᴏ ᴘᴏᴡᴇʀs ᴄʜᴀʜɪʏᴇ ᴛᴏ ᴏᴡɴᴇʀ sᴇ ᴄᴏɴᴛᴀᴄᴛ ᴋᴀʀᴇɪɴ.</i>"
        )

    # --- 4. PREMIUM, EARN & BUSINESS ---
    elif data == "premium":
        help_text = (
            "<b>💎 『 ᴘʀᴇᴍɪᴜᴍ, ᴇᴀʀɴ & ʙᴜsɪɴᴇss 』 💎</b>\n\n"
            "➲ <b>ɴᴏ sʜᴏʀᴛʟɪɴᴋs:</b> ᴅɪʀᴇᴄᴛ ꜰɪʟᴇs ʙɪɴᴀ ᴀᴅs ᴋᴇ.\n"
            "➲ <b>ʜɪɢʜ sᴘᴇᴇᴅ:</b> ꜰᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ & sᴛʀᴇᴀᴍɪɴɢ.\n"
            "➲ <b>ɴᴏ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ:</b> ʙɪɴᴀ ᴋɪsɪ ʀᴜᴋᴀᴡᴀᴛ ᴋᴇ ᴍᴏᴠɪᴇs ᴘᴀʏᴇɪɴ.\n\n"
            "💰 <b>ᴍᴀᴋᴇ ᴍᴏɴᴇʏ:</b>\n"
            "sᴜᴅᴏ ᴜsᴇʀs ɪs ʙᴏᴛ ᴋᴏ ᴀᴘɴᴇ ᴄʜᴀɴɴᴇʟs ᴘᴀʀ ʟᴀɢᴀ ᴋᴀʀ ᴀᴜʀ ᴘʀᴇᴍɪᴜᴍ sᴇʟʟ ᴋᴀʀᴋᴇ ᴘᴀɪsᴇ ᴋᴀᴍᴀ sᴀᴋᴛᴇ ʜᴀɪɴ!\n\n"
            "🤖 <b>ᴡʜɪᴛᴇ-ʟᴀʙᴇʟ ʙᴏᴛ:</b>\n"
            "ᴋʏᴀ ᴀᴀᴘᴋᴏ ᴀᴘɴᴀ ᴋʜᴜᴅ ᴋᴀ ʙᴏᴛ ʙᴀɴᴀɴᴀ ʜᴀɪ? ᴀᴘɴᴇ ʜɪsᴀʙ sᴇ ᴄᴏɴᴛʀᴏʟ ᴋᴀʀɴᴇ ᴀᴜʀ ᴇᴀʀɴ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ <b>ᴏᴡɴᴇʀ</b> sᴇ ᴄᴏɴᴛᴀᴄᴛ ᴋᴀʀᴇɪɴ!"
        )

    buttons = [
        [InlineKeyboardButton("👨‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ", url=f"https://t.me/{OWNER_USERNAME}", style=enums.ButtonStyle.SUCCESS)],
        [InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ ᴍᴇɴᴜ", callback_data="close_data", style=enums.ButtonStyle.DANGER)]
    ]

    await query.message.edit_caption(
        caption=help_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )