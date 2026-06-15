import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode

print("🚀 Starting Midnight Manage Bot...")

# ============================================
# CONFIGURATION
# ============================================

OWNER_ID = 7676301555
OWNER_USERNAME = "light_speedy"

# Sirf ek main bot token (extra bots hata diye)
MAIN_BOT_TOKEN = "8601344819:AAFSVHu6g0Vh1AhBudIPaM9hwoY-oqEmoGk"

# Premium emoji IDs
ADD_BTN_EMOJI_ID = "5253652327734192243"
SUPPORT_BTN_EMOJI_ID = "5443038326535759644"
CHANNEL_BTN_EMOJI_ID = "5771695636411847302"
OWNER_BTN_EMOJI_ID = "6136204644625423818"

EMOJI1_ID = "5454390891466726015"
EMOJI2_ID = "5355051922862653659"
EMOJI3_ID = "5424766882823544746"
EMOJI4_ID = "6276090299232031662"
POWERED_BY_EMOJI_ID = "5208727996315220567"
BOT_STATUS_EMOJI_ID = "5231200819986047254"
AUTHORIZED_EMOJI_ID = "5330194932781050507"
EMOJI_WRONG = "5240241223632954241"
EMOJI_BOT = "5287684458881756303"
EMOJI_VERI = "5780463361175066565"
EMOJI_PRO = "5330194932781050507"

EMOJI1 = f'<tg-emoji emoji-id="{EMOJI1_ID}">⭐️</tg-emoji>'
EMOJI2 = f'<tg-emoji emoji-id="{EMOJI2_ID}">✨</tg-emoji>'
EMOJI3 = f'<tg-emoji emoji-id="{EMOJI3_ID}">💎</tg-emoji>'
EMOJI4 = f'<tg-emoji emoji-id="{EMOJI4_ID}">🔥</tg-emoji>'
POWERED_BY_EMOJI = f'<tg-emoji emoji-id="{POWERED_BY_EMOJI_ID}">⚡</tg-emoji>'
BOT_STATUS_EMOJI = f'<tg-emoji emoji-id="{BOT_STATUS_EMOJI_ID}">📊</tg-emoji>'
AUTHORIZED_EMOJI = f'<tg-emoji emoji-id="{AUTHORIZED_EMOJI_ID}">✅</tg-emoji>'
EMOW = f'<tg-emoji emoji-id="{EMOJI_WRONG}">🚫</tg-emoji>'
EMOB = f'<tg-emoji emoji-id="{EMOJI_BOT}">🤖</tg-emoji>'
EMOV = f'<tg-emoji emoji-id="{EMOJI_VERI}">✔️</tg-emoji>'
EMOP = f'<tg-emoji emoji-id="{EMOJI_PRO}">🌟</tg-emoji>'

# Files
FILTERS_FILE = "filters.json"
WELCOME_FILE = "welcome.json"

# Global variables
main_bot = None
filters_data = {}
welcome_data = {}

dp = Dispatcher()


# ============================================
# FILE FUNCTIONS
# ============================================

def load_filters():
    global filters_data
    if os.path.exists(FILTERS_FILE):
        with open(FILTERS_FILE, 'r') as f:
            filters_data = json.load(f)
    print(f"📋 Loaded {len(filters_data)} chat filters")

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


# ============================================
# HELPER FUNCTIONS
# ============================================

def is_admin(user_id: int) -> bool:
    """Check if user is owner (admin)"""
    return user_id == OWNER_ID

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
        "{username}": f"@{user_name}" if user_name else "No username"
    }
    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)
    return text


# ============================================
# FILTER SYSTEM
# ============================================

@dp.message(Command("filter"))
async def add_filter(message: types.Message):
    """Add a filter - reply to a message and type /filter keyword"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sirf owner filter add kar sakta hai!")
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "⚠️ *How to add filter:*\n\n"
            "1. Reply to any message (text, photo, video, sticker, gif)\n"
            "2. Type `/filter keyword`\n\n"
            "📌 *Example:* Reply to a message and type `/filter hello`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    keyword = args[1].lower().strip()
    chat_id = str(message.chat.id)
    
    if not message.reply_to_message:
        await message.reply("⚠️ Please reply to a message to filter it!", parse_mode=ParseMode.MARKDOWN)
        return
    
    replied = message.reply_to_message
    
    if chat_id not in filters_data:
        filters_data[chat_id] = {}
    
    # Detect message type and save content
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
    elif replied.animation:
        filter_content = {
            "type": "gif",
            "file_id": replied.animation.file_id,
            "caption": replied.caption or ""
        }
    elif replied.sticker:
        filter_content = {
            "type": "sticker",
            "file_id": replied.sticker.file_id
        }
    elif replied.document:
        filter_content = {
            "type": "document",
            "file_id": replied.document.file_id,
            "caption": replied.caption or ""
        }
    elif replied.voice:
        filter_content = {
            "type": "voice",
            "file_id": replied.voice.file_id
        }
    elif replied.audio:
        filter_content = {
            "type": "audio",
            "file_id": replied.audio.file_id,
            "caption": replied.caption or ""
        }
    
    filters_data[chat_id][keyword] = filter_content
    save_filters()
    
    await message.reply(
        f"✅ *Filter added!*\n\n🔑 Keyword: `{keyword}`\n📊 Type: {filter_content['type']}",
        parse_mode=ParseMode.MARKDOWN
    )


@dp.message(Command("filters"))
async def list_filters(message: types.Message):
    """List all filters in current chat"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sirf owner filters dekh sakta hai!")
        return
    
    chat_id = str(message.chat.id)
    
    if chat_id not in filters_data or not filters_data[chat_id]:
        await message.reply(
            "📋 *No filters in this chat!*\n\nUse `/filter keyword` to add one.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    filter_list = list(filters_data[chat_id].keys())
    filter_text = "\n".join([f"🔹 `{f}`" for f in filter_list])
    
    await message.reply(
        f"📋 *Filters in this chat:*\n\n{filter_text}\n\n📊 Total: {len(filter_list)} filters\n\n"
        f"❌ Delete: `/dfilter keyword`",
        parse_mode=ParseMode.MARKDOWN
    )


@dp.message(Command("dfilter"))
async def delete_filter(message: types.Message):
    """Delete a filter"""
    if not is_admin(message.from_user.id):
        await message.reply("Sirf owner filter delete kar sakta hai!")
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


@dp.message(Command("delallfilters"))
async def delete_all_filters(message: types.Message):
    """Delete all filters in current chat"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sirf owner yeh command use kar sakta hai!")
        return
    
    chat_id = str(message.chat.id)
    
    if chat_id in filters_data:
        filters_data[chat_id] = {}
        save_filters()
        await message.reply("✅ All filters deleted from this chat!")
    else:
        await message.reply("📋 No filters found in this chat!")


# Auto trigger filters on text messages
@dp.message(F.text)
async def check_filters(message: types.Message):
    """Auto reply when filter keyword is triggered"""
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
                        await message.reply_photo(
                            photo=filter_content["file_id"],
                            caption=filter_content.get("caption", "")
                        )
                    elif filter_type == "video":
                        await message.reply_video(
                            video=filter_content["file_id"],
                            caption=filter_content.get("caption", "")
                        )
                    elif filter_type == "gif":
                        await message.reply_animation(
                            animation=filter_content["file_id"],
                            caption=filter_content.get("caption", "")
                        )
                    elif filter_type == "sticker":
                        await message.reply_sticker(sticker=filter_content["file_id"])
                    elif filter_type == "document":
                        await message.reply_document(
                            document=filter_content["file_id"],
                            caption=filter_content.get("caption", "")
                        )
                    elif filter_type == "voice":
                        await message.reply_voice(voice=filter_content["file_id"])
                    elif filter_type == "audio":
                        await message.reply_audio(
                            audio=filter_content["file_id"],
                            caption=filter_content.get("caption", "")
                        )
                except Exception as e:
                    print(f"Error sending filter: {e}")
                break


# ============================================
# WELCOME SYSTEM
# ============================================

@dp.message(Command("setwelcome"))
async def set_welcome(message: types.Message):
    """Set welcome message - reply to a message and type /setwelcome"""
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sirf owner welcome set kar sakta hai!")
        return
    
    if not message.reply_to_message:
        await message.reply(
            "⚠️ *How to set welcome:*\n\n"
            "1. Reply to any message (text, photo, video, sticker, gif)\n"
            "2. Type `/setwelcome`\n\n"
            "You can also add custom text: `/setwelcome Welcome {mention}!`\n\n"
            "📝 *Placeholders:*\n"
            "`{mention}` - User mention (blue)\n"
            "`{id}` - User ID\n"
            "`{name}` - Full name\n"
            "`{first_name}` - First name only",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    chat_id = str(message.chat.id)
    replied = message.reply_to_message
    
    args = message.text.split(maxsplit=1)
    custom_text = args[1] if len(args) > 1 else None
    
    welcome_content = {}
    
    if replied.text:
        welcome_content = {
            "type": "text",
            "content": custom_text or replied.text
        }
    elif replied.photo:
        welcome_content = {
            "type": "photo",
            "file_id": replied.photo[-1].file_id,
            "caption": custom_text or replied.caption or ""
        }
    elif replied.video:
        welcome_content = {
            "type": "video",
            "file_id": replied.video.file_id,
            "caption": custom_text or replied.caption or ""
        }
    elif replied.animation:
        welcome_content = {
            "type": "gif",
            "file_id": replied.animation.file_id,
            "caption": custom_text or replied.caption or ""
        }
    elif replied.sticker:
        welcome_content = {
            "type": "sticker",
            "file_id": replied.sticker.file_id
        }
    else:
        await message.reply("❌ Unsupported message type! Supported: text, photo, video, gif, sticker")
        return
    
    welcome_data[chat_id] = welcome_content
    save_welcome()
    
    await message.reply(
        f"✅ *Welcome message set!*\n\n📊 Type: {welcome_content['type']}\n\n"
        f"📝 Use `/viewwelcome` to see preview",
        parse_mode=ParseMode.MARKDOWN
    )


@dp.message(Command("clearwelcome"))
async def clear_welcome(message: types.Message):
    """Clear welcome message for current chat"""
    if not is_admin(message.from_user.id):
        await message.reply("{EMOW} only owner command")
        return
    
    chat_id = str(message.chat.id)
    
    if chat_id in welcome_data:
        del welcome_data[chat_id]
        save_welcome()
        await message.reply("✅ Welcome message cleared for this chat!")
    else:
        await message.reply("ℹ️ No welcome message set for this chat!")


@dp.message(Command("viewwelcome"))
async def view_welcome(message: types.Message):
    """View current welcome message"""
    if not is_admin(message.from_user.id):
        await message.reply("{EMOW} Sirf owner welcome dekh sakta hai!")
        return
    
    chat_id = str(message.chat.id)
    
    if chat_id not in welcome_data:
        await message.reply("ℹ️ No welcome message set!", parse_mode=ParseMode.MARKDOWN)
        return
    
    wc = welcome_data[chat_id]
    text = f"✅ *Welcome Settings*\n\n📊 Type: {wc['type']}\n"
    
    if wc['type'] == 'text':
        text += f"📝 Content: `{wc['content'][:200]}`"
    else:
        text += f"📝 Caption: `{wc.get('caption', 'None')[:200]}`"
    
    await message.reply(text, parse_mode=ParseMode.MARKDOWN)


# Auto welcome on new member join
@dp.message(F.new_chat_members)
async def welcome_new_member(message: types.Message):
    """Send welcome message when new member joins"""
    chat_id = str(message.chat.id)
    
    if chat_id not in welcome_data:
        return
    
    for new_member in message.new_chat_members:
        # Don't welcome the bot itself
        if new_member.id == (await main_bot.get_me()).id:
            continue
        
        user_id = new_member.id
        user_name = new_member.first_name or "User"
        user_mention = format_user_mention(user_id, user_name)
        
        welcome_content = welcome_data[chat_id]
        welcome_type = welcome_content.get("type", "text")
        
        try:
            if welcome_type == "text":
                text = parse_welcome_text(welcome_content["content"], user_id, user_name, user_mention)
                await message.reply(text, parse_mode=ParseMode.HTML)
            elif welcome_type == "photo":
                caption = parse_welcome_text(welcome_content.get("caption", ""), user_id, user_name, user_mention)
                await message.reply_photo(
                    photo=welcome_content["file_id"],
                    caption=caption,
                    parse_mode=ParseMode.HTML
                )
            elif welcome_type == "video":
                caption = parse_welcome_text(welcome_content.get("caption", ""), user_id, user_name, user_mention)
                await message.reply_video(
                    video=welcome_content["file_id"],
                    caption=caption,
                    parse_mode=ParseMode.HTML
                )
            elif welcome_type == "gif":
                caption = parse_welcome_text(welcome_content.get("caption", ""), user_id, user_name, user_mention)
                await message.reply_animation(
                    animation=welcome_content["file_id"],
                    caption=caption,
                    parse_mode=ParseMode.HTML
                )
            elif welcome_type == "sticker":
                await message.reply_sticker(sticker=welcome_content["file_id"])
        except Exception as e:
            print(f"Error sending welcome: {e}")


# ============================================
# START COMMAND
# ============================================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Welcome message with buttons"""
    user = message.from_user
    owner_mention = format_user_mention(OWNER_ID, "L ɪ ɢ ʜ ᴛ")
    user_mention = format_user_mention(user.id, user.first_name)
    
    is_auth = is_admin(user.id)
    auth_status = "Authorized" if is_auth else "Not Authorized"
    
    text = (
        f"{EMOJI1} Hey {user_mention}\n\n"
        f"{EMOJI2} This is MɪDɴIɢHᴛ MᴀNᴀGᴇ bot {EMOJI3}\n\n\n"
        f"{EMOJI4} powered by : {owner_mention} {POWERED_BY_EMOJI}\n\n"
    )
    
    bot_info = await main_bot.get_me()
    bot_username = bot_info.username
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ADD ME TO YOUR GROUP", url=f"https://t.me/{bot_username}?startgroup=botstart", style="primary", icon_custom_emoji_id=ADD_BTN_EMOJI_ID)],
        [InlineKeyboardButton(text="SUPPORT", url="https://t.me/midnight_chatclub", style="success", icon_custom_emoji_id=SUPPORT_BTN_EMOJI_ID),
         InlineKeyboardButton(text="CHANNEL", url="https://t.me/midnight_supportt", style="success", icon_custom_emoji_id=CHANNEL_BTN_EMOJI_ID)],
        [InlineKeyboardButton(text="OWNER", url="https://t.me/light_speedy", style="danger", icon_custom_emoji_id=OWNER_BTN_EMOJI_ID)]
    ])
    
    await message.reply(text, parse_mode=ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)


# ============================================
# MAIN
# ============================================

async def main():
    global main_bot
    
    print("=" * 50)
    print("🤖 MIDNIGHT MANAGE BOT")
    print("=" * 50)
    print(f"👑 Owner: @{OWNER_USERNAME} (ID: {OWNER_ID})")
    print("📋 Features: Filter System + Welcome System")
    print("=" * 50)
    
    # Load data
    load_filters()
    load_welcome()
    
    # Create bot
    main_bot = Bot(token=MAIN_BOT_TOKEN)
    
    bot_info = await main_bot.get_me()
    print(f"\n✅ Bot connected: @{bot_info.username}")
    print(f"✅ Bot ID: {bot_info.id}")
    
    # Print loaded data
    total_filters = sum(len(f) for f in filters_data.values())
    print(f"\n📋 Loaded: {total_filters} filters in {len(filters_data)} chats")
    print(f"👋 Loaded: {len(welcome_data)} welcome messages")
    
    print("\n📋 Commands:")
    print("   🔍 /filter keyword - Add filter")
    print("   📋 /filters - List filters")
    print("   ❌ /dfilter keyword - Delete filter")
    print("   🗑️ /delallfilters - Delete all filters")
    print("   👋 /setwelcome - Set welcome")
    print("   👀 /viewwelcome - View welcome")
    print("   🗑️ /clearwelcome - Clear welcome")
    print("   🏠 /start - Welcome message")
    print("=" * 50)
    
    print("\n🚀 Bot is running! Send /start on Telegram\n")
    
    await dp.start_polling(main_bot)


if __name__ == "__main__":
    asyncio.run(main())
