import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberUpdated
from aiogram.enums import ParseMode

print("🚀 Starting Midnight Manage Bot...")

# ============================================
# CONFIGURATION
# ============================================

OWNER_ID = 7676301555
OWNER_USERNAME = "light_speedy"
BOT_TOKEN = "8601344819:AAFSVHu6g0Vh1AhBudIPaM9hwoY-oqEmoGk"

# ============================================
# PREMIUM CUSTOM EMOJI IDs
# ============================================

# Button emojis
ADD_BTN_EMOJI_ID = "5253652327734192243"
SUPPORT_BTN_EMOJI_ID = "5443038326535759644"
CHANNEL_BTN_EMOJI_ID = "5771695636411847302"
OWNER_BTN_EMOJI_ID = "6136204644625423818"

# Message emojis (start command ke liye)
EMOJI1_ID = "5454390891466726015"
EMOJI2_ID = "5355051922862653659"
EMOJI3_ID = "5424766882823544746"
EMOJI4_ID = "6276090299232031662"
POWERED_BY_EMOJI_ID = "5208727996315220567"
BOT_STATUS_EMOJI_ID = "5231200819986047254"
TOTAL_BOTS_EMOJI_ID = "5287684458881756303"
AUTHORIZED_EMOJI_ID = "5330194932781050507"

# Premium emoji format
EMOJI1 = f'<tg-emoji emoji-id="{EMOJI1_ID}">⭐️</tg-emoji>'
EMOJI2 = f'<tg-emoji emoji-id="{EMOJI2_ID}">✨</tg-emoji>'
EMOJI3 = f'<tg-emoji emoji-id="{EMOJI3_ID}">💎</tg-emoji>'
EMOJI4 = f'<tg-emoji emoji-id="{EMOJI4_ID}">🔥</tg-emoji>'
POWERED_BY_EMOJI = f'<tg-emoji emoji-id="{POWERED_BY_EMOJI_ID}">⚡</tg-emoji>'
BOT_STATUS_EMOJI = f'<tg-emoji emoji-id="{BOT_STATUS_EMOJI_ID}">📊</tg-emoji>'
TOTAL_BOTS_EMOJI = f'<tg-emoji emoji-id="{TOTAL_BOTS_EMOJI_ID}">🤖</tg-emoji>'
AUTHORIZED_EMOJI = f'<tg-emoji emoji-id="{AUTHORIZED_EMOJI_ID}">✅</tg-emoji>'

# Files
FILTERS_FILE = "filters.json"
WELCOME_FILE = "welcome.json"
ADMINS_FILE = "admins.json"

# Global variables
filters_data = {}
welcome_data = {}
group_admins = set()  # Group admin user IDs

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ============================================
# FILE FUNCTIONS
# ============================================

def load_filters():
    global filters_data
    if os.path.exists(FILTERS_FILE):
        with open(FILTERS_FILE, 'r') as f:
            filters_data = json.load(f)
    print(f"📋 Loaded {len(filters_data)} filters")

def save_filters():
    with open(FILTERS_FILE, 'w') as f:
        json.dump(filters_data, f)

def load_welcome():
    global welcome_data
    if os.path.exists(WELCOME_FILE):
        with open(WELCOME_FILE, 'r') as f:
            welcome_data = json.load(f)
    print(f"📋 Loaded welcome for {len(welcome_data)} chats")

def save_welcome():
    with open(WELCOME_FILE, 'w') as f:
        json.dump(welcome_data, f)

def load_admins():
    global group_admins
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'r') as f:
            data = json.load(f)
            group_admins = set(data.get('admins', []))
    print(f"📋 Loaded {len(group_admins)} group admins")

def save_admins():
    with open(ADMINS_FILE, 'w') as f:
        json.dump({'admins': list(group_admins)}, f)


# ============================================
# ADMIN CHECK FUNCTIONS
# ============================================

async def is_admin_or_owner(user_id: int, chat_id: int = None) -> bool:
    """Check if user is owner, group admin, or approved"""
    # Owner is always admin
    if user_id == OWNER_ID:
        return True
    
    # Check if in group admins list
    if user_id in group_admins:
        return True
    
    # If chat_id provided, check if user is admin in that group
    if chat_id:
        try:
            member = await bot.get_chat_member(chat_id, user_id)
            if member.status in ['creator', 'administrator']:
                return True
        except:
            pass
    
    return False

def format_user_mention(user_id, name=None):
    if not name:
        name = "User"
    return f'<a href="tg://user?id={user_id}">{name}</a>'

def parse_welcome_text(text, user_id, user_name, user_mention):
    replacements = {
        "{mention}": user_mention,
        "{id}": str(user_id),
        "{name}": user_name,
        "{first_name}": user_name.split()[0] if user_name else "User",
    }
    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)
    return text


# ============================================
# FILTER SYSTEM (Sirf Admin use kar sakte hain)
# ============================================

@dp.message(Command("filter"))
async def add_filter(message: types.Message):
    if not await is_admin_or_owner(message.from_user.id, message.chat.id):
        await message.reply("❌ Sirf group admin filter add kar sakta hai!")
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "⚠️ *How to add filter:*\n\n"
            "1. Reply to any message\n"
            "2. Type `/filter keyword`\n\n"
            "📌 *Example:* Reply to a message and type `/filter hello`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    keyword = args[1].lower().strip()
    chat_id = str(message.chat.id)
    
    if not message.reply_to_message:
        await message.reply("⚠️ Please reply to a message to filter it!")
        return
    
    replied = message.reply_to_message
    
    if chat_id not in filters_data:
        filters_data[chat_id] = {}
    
    filter_content = {"type": "text", "content": replied.text or "No content"}
    
    if replied.photo:
        filter_content = {
            "type": "photo",
            "file_id": replied.photo[-1].file_id,
            "caption": replied.caption or ""
        }
    elif replied.video:
        filter_content = {
            "type": "video",
            "file_id": replied.video.file_id,
            "caption": replied.caption or ""
        }
    elif replied.sticker:
        filter_content = {
            "type": "sticker",
            "file_id": replied.sticker.file_id
        }
    
    filters_data[chat_id][keyword] = filter_content
    save_filters()
    
    await message.reply(f"✅ *Filter added!*\n🔑 Keyword: `{keyword}`", parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("filters"))
async def list_filters(message: types.Message):
    if not await is_admin_or_owner(message.from_user.id, message.chat.id):
        await message.reply("❌ Sirf group admin filters dekh sakta hai!")
        return
    
    chat_id = str(message.chat.id)
    
    if chat_id not in filters_data or not filters_data[chat_id]:
        await message.reply("📋 *No filters in this chat!*\n\nUse `/filter keyword` to add one.", parse_mode=ParseMode.MARKDOWN)
        return
    
    filter_list = list(filters_data[chat_id].keys())
    filter_text = "\n".join([f"🔹 `{f}`" for f in filter_list])
    
    await message.reply(
        f"📋 *Filters in this chat:*\n\n{filter_text}\n\n📊 Total: {len(filter_list)} filters\n\n❌ Delete: `/dfilter keyword`",
        parse_mode=ParseMode.MARKDOWN
    )


@dp.message(Command("dfilter"))
async def delete_filter(message: types.Message):
    if not await is_admin_or_owner(message.from_user.id, message.chat.id):
        await message.reply("❌ Sirf group admin filter delete kar sakta hai!")
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("⚠️ Usage: `/dfilter keyword`", parse_mode=ParseMode.MARKDOWN)
        return
    
    keyword = args[1].lower().strip()
    chat_id = str(message.chat.id)
    
    if chat_id in filters_data and keyword in filters_data[chat_id]:
        del filters_data[chat_id][keyword]
        save_filters()
        await message.reply(f"✅ Filter deleted: `{keyword}`", parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply(f"❌ Filter not found: `{keyword}`", parse_mode=ParseMode.MARKDOWN)


@dp.message(F.text)
async def check_filters(message: types.Message):
    if not message.text:
        return
    
    chat_id = str(message.chat.id)
    text = message.text.lower().strip()
    
    if chat_id in filters_data:
        for keyword, filter_content in filters_data[chat_id].items():
            if keyword in text:
                filter_type = filter_content.get("type", "text")
                try:
                    if filter_type == "text":
                        await message.reply(filter_content["content"])
                    elif filter_type == "photo":
                        await message.reply_photo(photo=filter_content["file_id"], caption=filter_content.get("caption", ""))
                    elif filter_type == "video":
                        await message.reply_video(video=filter_content["file_id"], caption=filter_content.get("caption", ""))
                    elif filter_type == "sticker":
                        await message.reply_sticker(sticker=filter_content["file_id"])
                except Exception as e:
                    print(f"Error: {e}")
                break


# ============================================
# WELCOME SYSTEM (Sirf Admin use kar sakte hain)
# ============================================

@dp.message(Command("setwelcome"))
async def set_welcome(message: types.Message):
    if not await is_admin_or_owner(message.from_user.id, message.chat.id):
        await message.reply("❌ Sirf group admin welcome set kar sakta hai!")
        return
    
    if not message.reply_to_message:
        await message.reply(
            "⚠️ *How to set welcome:*\n\n"
            "1. Reply to any message\n"
            "2. Type `/setwelcome`\n\n"
            "📝 *Placeholders:*\n"
            "`{mention}` - User mention\n"
            "`{id}` - User ID\n"
            "`{name}` - Full name\n"
            "`{first_name}` - First name only",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    chat_id = str(message.chat.id)
    replied = message.reply_to_message
    
    if replied.text:
        welcome_data[chat_id] = {"type": "text", "content": replied.text}
    elif replied.photo:
        welcome_data[chat_id] = {"type": "photo", "file_id": replied.photo[-1].file_id, "caption": replied.caption or ""}
    elif replied.video:
        welcome_data[chat_id] = {"type": "video", "file_id": replied.video.file_id, "caption": replied.caption or ""}
    elif replied.sticker:
        welcome_data[chat_id] = {"type": "sticker", "file_id": replied.sticker.file_id}
    else:
        await message.reply("❌ Unsupported message type! Supported: text, photo, video, sticker")
        return
    
    save_welcome()
    await message.reply(f"✅ *Welcome message set!*\n📊 Type: {welcome_data[chat_id]['type']}", parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("clearwelcome"))
async def clear_welcome(message: types.Message):
    if not await is_admin_or_owner(message.from_user.id, message.chat.id):
        await message.reply("❌ Sirf group admin welcome clear kar sakta hai!")
        return
    
    chat_id = str(message.chat.id)
    
    if chat_id in welcome_data:
        del welcome_data[chat_id]
        save_welcome()
        await message.reply("✅ Welcome message cleared!")
    else:
        await message.reply("ℹ️ No welcome message set!")


@dp.message(Command("viewwelcome"))
async def view_welcome(message: types.Message):
    if not await is_admin_or_owner(message.from_user.id, message.chat.id):
        await message.reply("❌ Sirf group admin welcome dekh sakta hai!")
        return
    
    chat_id = str(message.chat.id)
    
    if chat_id not in welcome_data:
        await message.reply("ℹ️ No welcome message set!", parse_mode=ParseMode.MARKDOWN)
        return
    
    wc = welcome_data[chat_id]
    text = f"✅ *Welcome Settings*\n📊 Type: {wc['type']}\n"
    
    if wc['type'] == 'text':
        text += f"📝 Content: `{wc['content'][:200]}`"
    else:
        text += f"📝 Caption: `{wc.get('caption', 'None')[:200]}`"
    
    await message.reply(text, parse_mode=ParseMode.MARKDOWN)


@dp.message(F.new_chat_members)
async def welcome_new_member(message: types.Message):
    chat_id = str(message.chat.id)
    
    if chat_id not in welcome_data:
        return
    
    for new_member in message.new_chat_members:
        if new_member.id == (await bot.get_me()).id:
            continue
        
        user_id = new_member.id
        user_name = new_member.first_name or "User"
        user_mention = format_user_mention(user_id, user_name)
        
        wc = welcome_data[chat_id]
        
        try:
            if wc["type"] == "text":
                text = parse_welcome_text(wc["content"], user_id, user_name, user_mention)
                await message.reply(text, parse_mode=ParseMode.HTML)
            elif wc["type"] == "photo":
                caption = parse_welcome_text(wc.get("caption", ""), user_id, user_name, user_mention)
                await message.reply_photo(photo=wc["file_id"], caption=caption, parse_mode=ParseMode.HTML)
            elif wc["type"] == "video":
                caption = parse_welcome_text(wc.get("caption", ""), user_id, user_name, user_mention)
                await message.reply_video(video=wc["file_id"], caption=caption, parse_mode=ParseMode.HTML)
            elif wc["type"] == "sticker":
                await message.reply_sticker(sticker=wc["file_id"])
        except Exception as e:
            print(f"Error: {e}")


# ============================================
# ADD GROUP ADMIN COMMAND (Owner only)
# ============================================

@dp.message(Command("addadmin"))
async def add_admin(message: types.Message):
    """Add a user as group admin (so they can use filter/welcome)"""
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ Sirf owner admin add kar sakta hai!")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply("⚠️ Usage: `/addadmin @username` or `/addadmin user_id`", parse_mode=ParseMode.MARKDOWN)
        return
    
    target = args[1]
    
    if target.startswith('@'):
        try:
            user = await bot.get_chat(target)
            user_id = user.id
        except:
            await message.reply(f"❌ User {target} not found!")
            return
    else:
        user_id = int(target)
    
    group_admins.add(user_id)
    save_admins()
    
    await message.reply(f"✅ User added as admin!\n👤 {target}\n🔓 Now can use filter/welcome commands", parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("removeadmin"))
async def remove_admin(message: types.Message):
    """Remove a user from group admins"""
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ Sirf owner admin remove kar sakta hai!")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply("⚠️ Usage: `/removeadmin @username` or `/removeadmin user_id`", parse_mode=ParseMode.MARKDOWN)
        return
    
    target = args[1]
    
    if target.startswith('@'):
        try:
            user = await bot.get_chat(target)
            user_id = user.id
        except:
            await message.reply(f"❌ User {target} not found!")
            return
    else:
        user_id = int(target)
    
    if user_id not in group_admins:
        await message.reply(f"❌ {target} is not an admin!")
        return
    
    group_admins.remove(user_id)
    save_admins()
    
    await message.reply(f"✅ User removed from admin!\n👤 {target}", parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("admins"))
async def list_admins(message: types.Message):
    """List all group admins"""
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ Sirf owner yeh command dekh sakta hai!")
        return
    
    if not group_admins:
        await message.reply("📋 No group admins added!\n\nUse `/addadmin @user` to add.", parse_mode=ParseMode.MARKDOWN)
        return
    
    admin_list = []
    for admin_id in group_admins:
        try:
            user = await bot.get_chat(admin_id)
            name = user.first_name or str(admin_id)
            admin_list.append(f"👤 {name} (`{admin_id}`)")
        except:
            admin_list.append(f"🆔 `{admin_id}`")
    
    await message.reply(f"✅ *Group Admins*\n\n" + "\n".join(admin_list), parse_mode=ParseMode.MARKDOWN)


# ============================================
# START COMMAND - PEHLE JESI (PREMIUM EMOJI KE SAATH)
# ============================================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    print(f"✅ /start from {message.from_user.id}")
    
    user = message.from_user
    owner_mention = format_user_mention(OWNER_ID, "L ɪ ɢ ʜ ᴛ")
    user_mention = format_user_mention(user.id, user.first_name)
    
    # Check if user is admin (owner or group admin)
    is_admin_user = await is_admin_or_owner(user.id, message.chat.id)
    auth_status = "Authorized" if is_admin_user else "Not Authorized"
    
    # Premium emoji message - BILKUL PEHLE JESA
    message_text = (
        f"Hey {user_mention} {EMOJI1}\n\n"
        f"{EMOJI2} this is midnight manage bot {EMOJI3}\n\n\n"
        f"{EMOJI4} powered by : {owner_mention} {POWERED_BY_EMOJI}\n\n"
        f"{BOT_STATUS_EMOJI} *Bot Status*\n"
        f"{TOTAL_BOTS_EMOJI} Total Bots: 1\n"
        f"{AUTHORIZED_EMOJI} {auth_status}"
    )
    
    bot_info = await bot.get_me()
    bot_username = bot_info.username
    
    # Premium emoji buttons - BILKUL PEHLE JESE
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="ADD ME TO YOUR GROUP",
                url=f"https://t.me/{bot_username}?startgroup=botstart",
                style="primary",
                icon_custom_emoji_id=ADD_BTN_EMOJI_ID
            )
        ],
        [
            InlineKeyboardButton(
                text="SUPPORT",
                url="https://t.me/midnight_supportt",
                style="success",
                icon_custom_emoji_id=SUPPORT_BTN_EMOJI_ID
            ),
            InlineKeyboardButton(
                text="CHANNEL",
                url="https://t.me/midnight_chatclub",
                style="success",
                icon_custom_emoji_id=CHANNEL_BTN_EMOJI_ID
            )
        ],
        [
            InlineKeyboardButton(
                text="OWNER",
                url="https://t.me/light_speedy",
                style="danger",
                icon_custom_emoji_id=OWNER_BTN_EMOJI_ID
            )
        ]
    ])
    
    await message.reply(
        message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
    print("✅ /start response sent")


# ============================================
# HELP COMMAND
# ============================================

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    is_admin_user = await is_admin_or_owner(message.from_user.id, message.chat.id)
    
    if is_admin_user:
        help_text = (
            "📋 *Available Commands (Admin):*\n\n"
            "🔍 *Filter System*\n"
            "   `/filter keyword` - Add filter (reply to msg)\n"
            "   `/filters` - List all filters\n"
            "   `/dfilter keyword` - Delete filter\n\n"
            "👋 *Welcome System*\n"
            "   `/setwelcome` - Set welcome (reply to msg)\n"
            "   `/viewwelcome` - View welcome\n"
            "   `/clearwelcome` - Clear welcome\n\n"
            "👑 *Owner Commands*\n"
            "   `/addadmin @user` - Add group admin\n"
            "   `/removeadmin @user` - Remove group admin\n"
            "   `/admins` - List group admins\n\n"
            "🏠 `/start` - Welcome message"
        )
    else:
        help_text = (
            "📋 *Available Commands:*\n\n"
            "🏠 `/start` - Welcome message\n"
            "❓ `/help` - This message\n\n"
            "*Note:* Filter and welcome commands are only for group admins."
        )
    
    await message.reply(help_text, parse_mode=ParseMode.MARKDOWN)


# ============================================
# MAIN
# ============================================

async def main():
    print("=" * 50)
    print("🤖 MIDNIGHT MANAGE BOT")
    print("=" * 50)
    print(f"👑 Owner: @{OWNER_USERNAME} (ID: {OWNER_ID})")
    print("📋 Features: Filter + Welcome + Admin System")
    print("=" * 50)
    
    load_filters()
    load_welcome()
    load_admins()
    
    bot_info = await bot.get_me()
    print(f"\n✅ Bot connected: @{bot_info.username}")
    print(f"✅ Bot ID: {bot_info.id}")
    
    total_filters = sum(len(f) for f in filters_data.values())
    print(f"\n📋 Loaded: {total_filters} filters")
    print(f"👋 Loaded: {len(welcome_data)} welcome messages")
    print(f"👑 Loaded: {len(group_admins)} group admins")
    
    print("\n📋 Commands:")
    print("   🏠 /start - Welcome message")
    print("   ❓ /help - Help")
    print("   🔍 /filter keyword - Add filter (admin)")
    print("   📋 /filters - List filters (admin)")
    print("   ❌ /dfilter keyword - Delete filter (admin)")
    print("   👋 /setwelcome - Set welcome (admin)")
    print("   👀 /viewwelcome - View welcome (admin)")
    print("   🗑️ /clearwelcome - Clear welcome (admin)")
    print("   👑 /addadmin @user - Add group admin (owner)")
    print("   👑 /removeadmin @user - Remove admin (owner)")
    print("   📋 /admins - List group admins (owner)")
    print("=" * 50)
    
    print("\n🚀 Bot is running! Send /start on Telegram\n")
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
