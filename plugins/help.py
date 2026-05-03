import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import PICS, OWNER_USERNAME, SUPPORT_LINK
from utils import temp

# --- SMART UI TEXTS ---

HELP_HOME = (
    "<b>👋 ʜᴇʏ {mention},</b>\n\n"
    "ɪɴꜰɪɴɪᴛʏ ᴍᴜʟᴛɪ-ꜰᴜɴᴄᴛɪᴏɴᴀʟ ʙᴏᴛ ᴍᴇ ᴀᴀᴘᴋᴀ sᴡᴀɢᴀᴛ ʜᴀɪ! 🚀\n\n"
    "ɪs ʙᴏᴛ ᴋᴏ sᴘᴇᴄɪᴀʟʟʏ <b>ᴀᴜᴛᴏ-ꜰɪʟᴛᴇʀ</b>, <b>ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b> ᴀᴜʀ <b>ᴘʀᴇᴍɪᴜᴍ sᴇʀᴠɪᴄᴇs</b> "
    "ᴋᴇ ʟɪʏᴇ ᴅᴇsɪɢɴ ᴋɪʏᴀ ɢᴀʏᴀ ʜᴀɪ. ɴɪᴄʜᴇ ᴅɪʏᴇ ɢᴀʏᴀ ʙᴜᴛᴛᴏɴs sᴇ ᴀᴀᴘ ᴍᴇʀɪ <b>sᴜᴘᴇʀᴘᴏᴡᴇʀs</b> ᴋᴏ ᴊᴀᴀɴ sᴀᴋᴛᴇ ʜᴀɪɴ:\n\n"
    "📊 <b>ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs:</b> <code>ᴏɴʟɪɴᴇ ✅</code>"
)

# --- HELP HANDLER ---

@Client.on_message(filters.command("help") & filters.incoming)
async def help_handler(bot, message):
    buttons = [
        [
            InlineKeyboardButton("✨ ᴀʟʟ ᴜsᴇʀs", callback_data="h_user"),
            InlineKeyboardButton("👥 ɢʀᴏᴜᴘ ᴄᴍᴅs", callback_data="h_group")
        ],
        [
            InlineKeyboardButton("👮 ᴀᴅᴍɪɴ ᴏɴʟʏ", callback_data="h_admin"),
            InlineKeyboardButton("⚡ sᴜᴅᴏ / ᴏᴡɴᴇʀ", callback_data="h_sudo")
        ],
        [
            InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ & ᴇᴀʀɴ", callback_data="h_premium")
        ],
        [
            InlineKeyboardButton("🏠 ʜᴏᴍᴇ", callback_data="h_back"),
            InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close_data")
        ]
    ]
    
    await message.reply_photo(
        photo=random.choice(PICS),
        caption=HELP_HOME.format(mention=message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons),
        effect_id=5104841245755180586  # Exclusive Telegram Animation
    )

# --- CALLBACK HANDLER ---

@Client.on_callback_query(filters.regex(r"^h_"))
async def help_callback(bot, query):
    data = query.data.split("_")[1]
    
    if data == "back":
        buttons = [
            [InlineKeyboardButton("✨ ᴀʟʟ ᴜsᴇʀs", callback_data="h_user"), InlineKeyboardButton("👥 ɢʀᴏᴜᴘ ᴄᴍᴅs", callback_data="h_group")],
            [InlineKeyboardButton("👮 ᴀᴅᴍɪɴ ᴏɴʟʏ", callback_data="h_admin"), InlineKeyboardButton("⚡ sᴜᴅᴏ / ᴏᴡɴᴇʀ", callback_data="h_sudo")],
            [InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ & ᴇᴀʀɴ", callback_data="h_premium")],
            [InlineKeyboardButton("🏠 ʜᴏᴍᴇ", callback_data="h_back"), InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close_data")]
        ]
        return await query.message.edit_caption(
            caption=HELP_HOME.format(mention=query.from_user.mention),
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    help_text = ""
    
    if data == "user":
        help_text = (
            "<b>✨ ᴀʟʟ ᴜsᴇʀ ᴄᴏᴍᴍᴀɴᴅs</b>\n"
            "<i>(ʏᴇ ᴄᴏᴍᴍᴀɴᴅs ᴋᴏɪ ʙʜɪ ᴜsᴇʀ ᴜsᴇ ᴋᴀʀ sᴀᴋᴛᴇ ʜᴀɪ)</i>\n\n"
            "➲ <code>/id</code> : ᴀᴘɴɪ ʏᴀ ᴋɪsɪ ᴜsᴇʀ/ᴄʜᴀᴛ ᴋɪ ᴜɴɪǫᴜᴇ ɪᴅ ɴɪᴋᴀʟᴇɪɴ[cite: 3].\n"
            "➲ <code>/info</code> : ᴜsᴇʀ ᴋɪ ᴘᴜʀɪ ᴅᴇᴛᴀɪʟs ᴀᴜʀ ᴘʀᴏꜰɪʟᴇ ᴄʜᴇᴄᴋ ᴋᴀʀᴇɪɴ[cite: 3].\n"
            "➲ <code>/speedtest</code> : ʙᴏᴛ ᴋᴇ sᴇʀᴠᴇʀ ᴋɪ sᴘᴇᴇᴅ ᴄʜᴇᴄᴋ ᴋᴀʀᴇɪɴ[cite: 3].\n"
            "➲ <code>/refer</code> : ᴅᴏsᴛᴏ ᴋᴏ ɪɴᴠɪᴛᴇ ᴋᴀʀᴇɪɴ ᴀᴜʀ <b>ꜰʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ</b> ᴘᴀʏᴇɪɴ[cite: 1].\n"
            "➲ <code>/img2link</code> : ᴋɪsɪ ʙʜɪ ᴘʜᴏᴛᴏ ᴋᴏ ᴜʀʟ ʟɪɴᴋ ᴍᴇɪɴ ᴄᴏɴᴠᴇʀᴛ ᴋᴀʀᴇɪɴ[cite: 1]."
        )

    elif data == "group":
        help_text = (
            "<b>👥 ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n"
            "<i>(ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ᴋᴇ ʟɪʏᴇ sᴍᴀʀᴛ ᴛᴏᴏʟs)</i>\n\n"
            "➲ <code>/settings</code> : ɢʀᴏᴜᴘ ᴋɪ ᴘᴜʀɪ sᴇᴛᴛɪɴɢs ᴘᴍ ᴍᴇɪɴ manage ᴋᴀʀᴇɪɴ[cite: 1].\n"
            "➲ <code>/manage</code> : ᴍᴜᴛᴇᴅ/ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs ᴋᴏ ᴇᴋ sᴀᴀᴛʜ sᴀᴀꜰ ᴋᴀʀᴇɪɴ[cite: 2].\n"
            "➲ <code>/purge</code> : hazaro messages ek sath delete karein[cite: 2].\n"
            "➲ <code>/ban</code> | <code>/mute</code> : bad elements ko control karein[cite: 2].\n"
            "➲ <code>/connect</code> : group ko bot PM se link karein[cite: 1]."
        )

    elif data == "admin":
        help_text = (
            "<b>👮 ᴀᴅᴍɪɴ ᴇxᴄʟᴜsɪᴠᴇ</b>\n"
            "<i>(sɪʀꜰ ʙᴏᴛ ᴀᴅᴍɪɴs ᴋᴇ ʟɪʏᴇ ᴘᴏᴡᴇʀꜰᴜʟ ᴄᴍᴅs)</i>\n\n"
            "➲ <code>/index_channels</code> : ɪɴᴅᴇxᴇᴅ ᴄʜᴀɴɴᴇʟs ᴋɪ ʟɪsᴛ ᴅᴇᴋʜᴇɪɴ[cite: 1].\n"
            "➲ <code>/stats</code> : ʙᴏᴛ ᴋɪ ʟɪᴠᴇ ᴘᴇʀꜰᴏʀᴍᴀɴᴄᴇ ᴀᴜʀ ᴅᴀᴛᴀʙᴀsᴇ dekhen[cite: 1].\n"
            "➲ <code>/leave</code> : kisi bhi group se bot ko leave karwayein[cite: 4].\n"
            "➲ <code>/ban_grp</code> : kisi group ko blacklist karein[cite: 4]."
        )

    elif data == "sudo":
        help_text = (
            "<b>⚡ sᴜᴅᴏ & ᴏᴡɴᴇʀ ᴘᴏᴡᴇʀs</b>\n"
            "<i>(ʙᴏᴛ ᴋᴇ ᴛʀᴜᴇ ᴄᴏɴᴛʀᴏʟʟᴇʀs)</i>\n\n"
            "➲ <code>/add_prm</code> : ᴋɪsɪ ʙʜɪ ᴜsᴇʀ ᴋᴏ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ᴅᴇɪɴ[cite: 1].\n"
            "➲ <code>/addsudo</code> : ɴᴀʏᴇ sᴜᴅᴏ ᴀᴅᴍɪɴs ᴀᴘᴘᴏɪɴᴛ ᴋᴀʀᴇɪɴ[cite: 1].\n"
            "➲ <code>/hyper_fsub</code> : global force-sub channels set karein[cite: 1].\n"
            "➲ <code>/vstats</code> : verification analytics pro dekhen[cite: 1]."
        )

    elif data == "premium":
        help_text = (
            "<b>💎 ᴘʀᴇᴍɪᴜᴍ, ᴇᴀʀɴ & ᴏᴡɴᴇʀsʜɪᴘ</b>\n\n"
            "➲ <b>ɴᴏ sʜᴏʀᴛʟɪɴᴋs:</b> direct files bina ads ke.\n"
            "➲ <b>ʜɪɢʜ sᴘᴇᴇᴅ:</b> fast downloading & streaming[cite: 1].\n"
            "➲ <b>ɴᴏ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ:</b> bina kisi rukawat ke movies payein.\n\n"
            "💰 <b>ᴇᴀʀɴ ᴍᴏɴᴇʏ:</b> ᴅᴏsᴛᴏ ᴋᴏ <code>/refer</code> ᴋᴀʀᴇɪɴ ᴀᴜʀ <b>ꜰʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ</b> ᴘᴀʏᴇɪɴ[cite: 1].\n\n"
            "🤖 <b>ᴍᴀᴋᴇ ʏᴏᴜʀ ᴏᴡɴ ʙᴏᴛ:</b> ᴋʏᴀ ᴀᴀᴘ ʙʜɪ ᴀɪsᴀ ʙᴏᴛ ʙᴀɴᴀɴᴀ ᴄʜᴀʜᴛᴇ ʜᴀɪɴ? ᴀᴘɴᴇ ʜɪsᴀʙ sᴇ ᴄᴏɴᴛʀᴏʟ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ ᴀᴜʀ ᴇᴀʀɴ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ <b>ᴏᴡɴᴇʀ</b> sᴇ ᴄᴏɴᴛᴀᴄᴛ ᴋᴀʀᴇɪɴ!"
        )

    await query.message.edit_caption(
        caption=help_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👨‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ", url=f"https://t.me/{OWNER_USERNAME}")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="h_back")]
        ])
    )