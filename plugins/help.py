import random
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import PICS, OWNER_USERNAME, SUPPORT_LINK
from utils import temp

# --- DECORATIVE UI TEXTS ---

HELP_HOME = (
    "<b>╔═══════『 ɪɴꜰɪɴɪᴛʏ ʜᴇʟᴘ 』══════╗</b>\n\n"
    "👋 ʜᴇʏ {mention},\n\n"
    "ɪɴꜰɪɴɪᴛʏ ᴍᴜʟᴛɪ-ꜰᴜɴᴄᴛɪᴏɴᴀʟ ʙᴏᴛ ᴍᴇ ᴀᴀᴘᴋᴀ sᴡᴀɢᴀᴛ ʜᴀɪ! 🚀\n"
    "ɪs ʙᴏᴛ ᴋᴏ sᴘᴇᴄɪᴀʟʟʏ <b>ᴀᴜᴛᴏ-ꜰɪʟᴛᴇʀ</b>, <b>ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b> ᴀᴜʀ <b>ᴘʀᴇᴍɪᴜᴍ sᴇʀᴠɪᴄᴇs</b> "
    "ᴋᴇ ʟɪʏᴇ ᴅᴇsɪɢɴ ᴋɪʏᴀ ɢᴀʏᴀ ʜᴀɪ. \n\n"
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
            InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ ᴍᴇɴᴜ", callback_data="close_data")
        ]
    ]
    
    await message.reply_photo(
        photo=random.choice(PICS),
        caption=HELP_HOME.format(mention=message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons),
        effect_id=5104841245755180586  # Premium Animation
    )

@Client.on_callback_query(filters.regex(r"^h_"))
async def help_callback(bot, query):
    data = query.data.split("_")[1]
    
    # --- ALL USERS SECTION ---
    if data == "user":
        help_text = (
            "<b>✨ 『 ᴀʟʟ ᴜsᴇʀ ᴄᴏᴍᴍᴀɴᴅs 』 ✨</b>\n\n"
            "➲ /id : ᴀᴘɴɪ ʏᴀ ᴋɪsɪ ᴜsᴇʀ/ᴄʜᴀᴛ ᴋɪ ᴜɴɪǫᴜᴇ ɪᴅ ɴɪᴋᴀʟᴇɪɴ.\n"
            "➲ /info : ᴜsᴇʀ ᴋɪ ᴘᴜʀɪ ᴅᴇᴛᴀɪʟs ᴀᴜʀ ᴘʀᴏꜰɪʟᴇ ᴄʜᴇᴄᴋ ᴋᴀʀᴇɪɴ[cite: 3].\n"
            "➲ /speedtest : ʙᴏᴛ ᴋᴇ sᴇʀᴠᴇʀ ᴋɪ sᴘᴇᴇᴅ ᴄʜᴇᴄᴋ ᴋᴀʀᴇɪɴ[cite: 3].\n"
            "➲ /refer : ᴅᴏsᴛᴏ ᴋᴏ ɪɴᴠɪᴛᴇ ᴋᴀʀᴇɪɴ ᴀᴜʀ ꜰʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ ᴘᴀʏᴇɪɴ.\n"
            "➲ /img2link : ᴋɪsɪ ʙʜɪ ᴘʜᴏᴛᴏ ᴋᴏ ᴜʀʟ ʟɪɴᴋ ᴍᴇɪɴ ᴄᴏɴᴠᴇʀᴛ ᴋᴀʀᴇɪɴ[cite: 1].\n"
            "➲ /settings : ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs ᴋᴏ manage ᴋᴀʀɴᴇ ᴋᴀ ᴍᴇɴᴜ[cite: 1].\n\n"
            "💡 <i>ɪɴ ᴄᴏᴍᴍᴀɴᴅs ᴋᴏ ᴋᴏɪ ʙʜɪ ᴜsᴇ ᴋᴀʀ sᴀᴋᴛᴀ ʜᴀɪ.</i>"
        )

    # --- GROUP ZONE SECTION (Including p_ttishow) ---
    elif data == "group":
        help_text = (
            "<b>👥 『 ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ 』 👥</b>\n\n"
            "➲ /manage : ᴍᴜᴛᴇᴅ/ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs ᴋᴏ ᴇᴋ sᴀᴀᴛʜ sᴀᴀꜰ ᴋᴀʀᴇɪɴ[cite: 2].\n"
            "➲ /purge : ʜᴀᴢᴀʀᴏ ᴍᴇssᴀɢᴇs ᴇᴋ sᴀᴛʜ ᴅᴇʟᴇᴛᴇ ᴋᴀʀᴇɪɴ[cite: 2].\n"
            "➲ /ban | /mute : ʙᴀᴅ ᴇʟᴇᴍᴇɴᴛs ᴋᴏ ᴄᴏɴᴛʀᴏʟ ᴋᴀʀᴇɪɴ[cite: 2].\n"
            "➲ /pin | /unpin : ɪᴍᴘᴏʀᴛᴀɴᴛ ᴍᴇssᴀɢᴇs ᴋᴏ highlight ᴋᴀʀᴇɪɴ[cite: 2].\n"
            "➲ /connect : ɢʀᴏᴜᴘ ᴋᴏ ʙᴏᴛ ᴘᴍ sᴇ ʟɪɴᴋ ᴋᴀʀᴇɪɴ[cite: 1].\n"
            "➲ /leave : ʙᴏᴛ ᴋᴏ ɢʀᴏᴜᴘ sᴇ ʟᴇᴀᴠᴇ ᴋᴀʀᴡᴀʏᴇɪɴ[cite: 4].\n\n"
            "👑 <b>ᴏᴡɴᴇʀ sᴘᴇᴄɪᴀʟ:</b>\n"
            "➲ /ban_grp : ᴋɪsɪ ɢʀᴏᴜᴘ ᴋᴏ ʙʟᴀᴄᴋʟɪsᴛ ᴋᴀʀᴇɪɴ[cite: 4].\n"
            "➲ /unban_grp : ɢʀᴏᴜᴘ ᴋᴏ ʀᴇ-ᴇɴᴀʙʟᴇ ᴋᴀʀᴇɪɴ[cite: 4]."
        )

    # --- SUDO POWERS SECTION ---
    elif data == "sudo":
        help_text = (
            "<b>⚡ 『 sᴜᴅᴏ ᴇxᴄʟᴜsɪᴠᴇ ᴘᴏᴡᴇʀs 』 ⚡</b>\n\n"
            "➲ /add_prm : ᴋɪsɪ ʙʜɪ ᴜsᴇʀ ᴋᴏ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ᴅᴇɪɴ[cite: 1].\n"
            "➲ /rm_prm : ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ʀᴇᴍᴏᴠᴇ ᴋᴀʀᴇɪɴ[cite: 1].\n"
            "➲ /addsudo : ɴᴀʏᴇ sᴜᴅᴏ ᴀᴅᴍɪɴs ᴀᴘᴘᴏɪɴᴛ ᴋᴀʀᴇɪɴ[cite: 1].\n"
            "➲ /stats : ʙᴏᴛ ᴋɪ ʟɪᴠᴇ ᴅᴀᴛᴀʙᴀsᴇ sᴛᴀᴛs dekhen[cite: 1].\n"
            "➲ /vstats : ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴀɴᴀʟʏᴛɪᴄs pro dekhen[cite: 1].\n\n"
            "⚠️ <b>ᴀʟᴇʀᴛ:</b> ʏᴇ ᴄᴏᴍᴍᴀɴᴅs sɪʀꜰ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs ᴋᴇ ʟɪʏᴇ ʜᴀɪɴ.\n"
            "📌 <i>ᴀɢᴀʀ ᴀᴀᴘᴋᴏ sᴜᴅᴏ ᴘᴏᴡᴇʀs ᴄʜᴀʜɪʏᴇ ᴛᴏ ᴏᴡɴᴇʀ sᴇ ᴄᴏɴᴛᴀᴄᴛ ᴋᴀʀᴇɪɴ.</i>"
        )

    # --- PREMIUM & EARN SECTION ---
    elif data == "premium":
        help_text = (
            "<b>💎 『 ᴘʀᴇᴍɪᴜᴍ, ᴇᴀʀɴ & ʙᴜsɪɴᴇss 』 💎</b>\n\n"
            "➲ <b>ɴᴏ sʜᴏʀᴛʟɪɴᴋs:</b> ᴅɪʀᴇᴄᴛ ꜰɪʟᴇs ʙɪɴᴀ ᴀᴅs ᴋᴇ.\n"
            "➲ <b>ʜɪɢʜ sᴘᴇᴇᴅ:</b> ꜰᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ & sᴛʀᴇᴀᴍɪɴɢ[cite: 1].\n"
            "➲ <b>ɴᴏ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ:</b> ʙɪɴᴀ ᴋɪsɪ ʀᴜᴋᴀᴡᴀᴛ ᴋᴇ ᴍᴏᴠɪᴇs ᴘᴀʏᴇɪɴ.\n\n"
            "💰 <b>ᴍᴀᴋᴇ ᴍᴏɴᴇʏ:</b>\n"
            "sᴜᴅᴏ ᴜsᴇʀs ɪs ʙᴏᴛ ᴋᴏ ᴀᴘɴᴇ ᴄʜᴀɴɴᴇʟs ᴘᴀʀ ʟᴀɢᴀ ᴋᴀʀ ᴀᴜʀ ᴘʀᴇᴍɪᴜᴍ sᴇʟʟ ᴋᴀʀᴋᴇ ᴘᴀɪsᴇ ᴋᴀᴍᴀ sᴀᴋᴛᴇ ʜᴀɪɴ![cite: 1]\n\n"
            "🤖 <b>ᴡʜɪᴛᴇ-ʟᴀʙᴇʟ ʙᴏᴛ:</b>\n"
            "ᴋʏᴀ ᴀᴀᴘᴋᴏ ᴀᴘɴᴀ ᴋʜᴜᴅ ᴋᴀ ʙᴏᴛ ʙᴀɴᴀɴᴀ ʜᴀɪ? ᴀᴘɴᴇ ʜɪsᴀʙ sᴇ ᴄᴏɴᴛʀᴏʟ ᴋᴀʀɴᴇ ᴀᴜʀ ᴇᴀʀɴ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ <b>ᴏᴡɴᴇʀ</b> sᴇ ᴄᴏɴᴛᴀᴄᴛ ᴋᴀʀᴇɪɴ!"
        )

    # Suitable colors for buttons using enums[cite: 1]
    buttons = [
        [InlineKeyboardButton("👨‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ", url=f"https://t.me/{OWNER_USERNAME}", style=enums.ButtonStyle.SUCCESS)],
        [InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ ᴍᴇɴᴜ", callback_data="close_data", style=enums.ButtonStyle.DANGER)]
    ]

    await query.message.edit_caption(
        caption=help_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )