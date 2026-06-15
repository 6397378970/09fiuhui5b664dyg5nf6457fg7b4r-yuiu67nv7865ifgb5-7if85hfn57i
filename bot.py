import asyncio
import json
import os
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ============================================
# CONFIGURATION
# ============================================

OWNER_ID = 7676301555
OWNER_USERNAME = "light_speedy"

# Main bot token
MAIN_BOT_TOKEN = "8601344819:AAE1nBCUJt74qq3i44Dl0l4r4_SBzcN0VIc"

# Extra bots tokens (11 bots for spam)
EXTRA_BOTS_TOKEN = [
    "8443522015:AAHYBRq7_F80gNH0I9nAXpHHGoEfkj5NGxQ",
    "8939942502:AAFXxqWXoupIEn_Q0IAd7Vtrb2aLzT9jzC8",
    "8775011066:AAH_ZqYhh0JZMYhIUZ7NYeXCWzg5oQFpfUM",
    "8996094741:AAEmZGsRI767EhNXOqq1MIHvkOVrOKrQ1WI",
    "8667582125:AAFKGw7oavoUqQwUJwNreSGi9-XFbYc1nMg",
    "8768157775:AAG3PVB7pEK4_h31B78a25REqnjw8KXfECU",
    "8601323918:AAF-yIGxJAcJi8cixvkEU2NpBMzXeo50KqA",
    "8910586383:AAHA17IaaNJlyxA67n962WqWp6uaRNCgLlQ",
    "8529811233:AAFkxtMd7qwt60EokC1n3d48PxEHz11KqAE",
    "8935772171:AAHSzMVE5k2bkQXof2fXGJGsH5pGQEn43Ec",
    "8952225468:AAHN7IIJs_ytovSF-RNHdxETTMo9evxibLk",
]

ALL_BOTS_TOKEN = [MAIN_BOT_TOKEN] + EXTRA_BOTS_TOKEN
TOTAL_BOTS = len(ALL_BOTS_TOKEN)

# Spam settings
SPAM_DELAY = 0.5
MAX_MESSAGES = 100

# ============================================
# PREMIUM CUSTOM EMOJI IDs
# ============================================

# Button emojis
ADD_BTN_EMOJI_ID = "5253652327734192243"
SUPPORT_BTN_EMOJI_ID = "5443038326535759644"
CHANNEL_BTN_EMOJI_ID = "5771695636411847302"
OWNER_BTN_EMOJI_ID = "6136204644625423818"

# Message emojis
EMOJI1_ID = "5454390891466726015"
EMOJI2_ID = "5355051922862653659"
EMOJI3_ID = "5424766882823544746"
EMOJI4_ID = "6276090299232031662"
BHAGWAAN_EMOJI_ID = "5285070644864628879"
POWERED_BY_EMOJI_ID = "5208727996315220567"
BOT_STATUS_EMOJI_ID = "5231200819986047254"
TOTAL_BOTS_EMOJI_ID = "5287684458881756303"
AUTHORIZED_EMOJI_ID = "5330194932781050507"

# Premium emoji format
EMOJI1 = f'<tg-emoji emoji-id="{EMOJI1_ID}">⭐️</tg-emoji>'
EMOJI2 = f'<tg-emoji emoji-id="{EMOJI2_ID}">✨</tg-emoji>'
EMOJI3 = f'<tg-emoji emoji-id="{EMOJI3_ID}">💎</tg-emoji>'
EMOJI4 = f'<tg-emoji emoji-id="{EMOJI4_ID}">🔥</tg-emoji>'
BHAGWAAN_EMOJI = f'<tg-emoji emoji-id="{BHAGWAAN_EMOJI_ID}">👑</tg-emoji>'
POWERED_BY_EMOJI = f'<tg-emoji emoji-id="{POWERED_BY_EMOJI_ID}">⚡</tg-emoji>'
BOT_STATUS_EMOJI = f'<tg-emoji emoji-id="{BOT_STATUS_EMOJI_ID}">📊</tg-emoji>'
TOTAL_BOTS_EMOJI = f'<tg-emoji emoji-id="{TOTAL_BOTS_EMOJI_ID}">🤖</tg-emoji>'
AUTHORIZED_EMOJI = f'<tg-emoji emoji-id="{AUTHORIZED_EMOJI_ID}">✅</tg-emoji>'

# Files
APPROVED_FILE = "approved_users.json"
FILTERS_FILE = "filters.json"
WELCOME_FILE = "welcome.json"

# Global variables
spam_active = False
spam_task = None
spam_stop_requested = False
spam_target_username = None
spam_target_id = None
spam_message = None
spam_starter = None
active_bots = []
main_bot = None
approved_users = set()
filters_data = {}
welcome_data = {}
current_spam_count = 0

dp = Dispatcher()


# ============================================
# FILE HANDLING FUNCTIONS
# ============================================

def load_approved_users():
    global approved_users
    if os.path.exists(APPROVED_FILE):
        with open(APPROVED_FILE, 'r') as f:
            data = json.load(f)
            approved_users = set(data.get('users', []))
    print(f"📋 Loaded {len(approved_users)} approved users")

def save_approved_users():
    with open(APPROVED_FILE, 'w') as f:
        json.dump({'users': list(approved_users)}, f)

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
    print(f"📋 Loaded welcome settings for {len(welcome_data)} chats")

def save_welcome():
    with open(WELCOME_FILE, 'w') as f:
        json.dump(welcome_data, f)


# ============================================
# HELPER FUNCTIONS
# ============================================

def is_authorized(user_id: int, username: str = None) -> bool:
    if user_id == OWNER_ID:
        return True
    if str(user_id) in approved_users:
        return True
    if username:
        clean_username = username.replace('@', '').lower()
        if clean_username in approved_users:
            return True
    return False

def format_user_mention(user_id: int, name: str = None) -> str:
    if not name:
        name = "User"
    return f'<a href="tg://user?id={user_id}">{name}</a>'

def parse_welcome_text(text: str, user_id: int, user_name: str, user_mention: str) -> str:
    """Replace placeholders in welcome message"""
    replacements = {
        "{mention}": user_mention,
        "{id}": str(user_id),
        "{name}": user_name,
        "{first_name}": user_name.split()[0] if user_name else "User",
        "{username}" : f"@{user_name}" if user_name else "No username"
    }
    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)
    return text

async def get_user_id(username: str):
    try:
        username = username.replace('@', '').strip()
        user = await main_bot.get_chat(f"@{username}")
        return user.id
    except Exception as e:
        print(f"Error: {e}")
        return None


# ============================================
# SPAM FUNCTIONS
# ============================================

async def create_all_bots():
    bots = []
    print("\n📡 Connecting to all bots...")
    
    for i, token in enumerate(ALL_BOTS_TOKEN):
        try:
            bot = Bot(token=token)
            bot_info = await bot.get_me()
            bots.append(bot)
            if i == 0:
                print(f"✅ MAIN BOT: @{bot_info.username}")
            else:
                print(f"✅ Extra Bot {i}: @{bot_info.username}")
        except Exception as e:
            print(f"❌ Bot {i+1} failed: {str(e)}")
    
    print(f"\n🎯 Total {len(bots)}/{TOTAL_BOTS} bots connected!\n")
    return bots

async def close_all_bots(bots):
    for bot in bots:
        try:
            await bot.close()
        except:
            pass

async def send_spam_messages(bots_list, target_user_id, message_text, max_msgs=MAX_MESSAGES):
    global spam_active, current_spam_count, spam_stop_requested
    
    current_spam_count = 0
    msg_index = 1
    
    while spam_active and not spam_stop_requested and current_spam_count < max_msgs:
        for bot_id, bot in enumerate(bots_list, 1):
            if not spam_active or spam_stop_requested or current_spam_count >= max_msgs:
                break
            
            try:
                if bot_id == 1:
                    final_msg = f"🤖 [MAIN] {message_text} [{msg_index}]"
                else:
                    final_msg = f"🔄 [Bot-{bot_id-1}] {message_text} [{msg_index}]"
                
                await bot.send_message(chat_id=target_user_id, text=final_msg)
                current_spam_count += 1
                print(f"✅ Msg {current_spam_count}/{max_msgs} - Bot {bot_id}")
                await asyncio.sleep(SPAM_DELAY)
            except Exception as e:
                print(f"❌ Bot {bot_id} error: {e}")
        
        msg_index += 1
        
        if current_spam_count >= max_msgs:
            spam_active = False
            print(f"✅ Auto-stopped after {max_msgs} messages")
            break
    
    spam_active = False


# ============================================
# FILTER SYSTEM (Rose Bot Style)
# ============================================

@dp.message(Command("filter"))
async def add_filter(message: types.Message):
    """Add a filter - reply to a message and type /filter keyword"""
    if not is_authorized(message.from_user.id, message.from_user.username):
        await message.reply("❌ Aap authorized nahi hain!")
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("⚠️ Usage: Reply to a message and type `/filter keyword`", parse_mode=ParseMode.MARKDOWN)
        return
    
    keyword = args[1].lower().strip()
    chat_id = str(message.chat.id)
    
    # Check if replying to a message
    if not message.reply_to_message:
        await message.reply("⚠️ Please reply to a message to filter it!")
        return
    
    # Get the replied message
    replied = message.reply_to_message
    
    # Store filter data
    if chat_id not in filters_data:
        filters_data[chat_id] = {}
    
    # Save message type and content
    filter_content = {
        "type": "text",
        "content": replied.text or replied.caption or "No content"
    }
    
    # Check for media
    if replied.photo:
        filter_content["type"] = "photo"
        filter_content["file_id"] = replied.photo[-1].file_id
        filter_content["caption"] = replied.caption or ""
    elif replied.video:
        filter_content["type"] = "video"
        filter_content["file_id"] = replied.video.file_id
        filter_content["caption"] = replied.caption or ""
    elif replied.animation:
        filter_content["type"] = "gif"
        filter_content["file_id"] = replied.animation.file_id
        filter_content["caption"] = replied.caption or ""
    elif replied.sticker:
        filter_content["type"] = "sticker"
        filter_content["file_id"] = replied.sticker.file_id
    elif replied.document:
        filter_content["type"] = "document"
        filter_content["file_id"] = replied.document.file_id
        filter_content["caption"] = replied.caption or ""
    elif replied.voice:
        filter_content["type"] = "voice"
        filter_content["file_id"] = replied.voice.file_id
    elif replied.audio:
        filter_content["type"] = "audio"
        filter_content["file_id"] = replied.audio.file_id
        filter_content["caption"] = replied.caption or ""
    
    filters_data[chat_id][keyword] = filter_content
    save_filters()
    
    await message.reply(f"✅ Filter added!\nKeyword: `{keyword}`", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("filters"))
async def list_filters(message: types.Message):
    """List all filters in current chat"""
    if not is_authorized(message.from_user.id, message.from_user.username):
        await message.reply("❌ Aap authorized nahi hain!")
        return
    
    chat_id = str(message.chat.id)
    
    if chat_id not in filters_data or not filters_data[chat_id]:
        await message.reply("📋 No filters in this chat!\n\nUse `/filter keyword` to add one.", parse_mode=ParseMode.MARKDOWN)
        return
    
    filter_list = list(filters_data[chat_id].keys())
    filter_text = "\n".join([f"🔹 `{f}`" for f in filter_list])
    
    await message.reply(
        f"📋 *Filters in this chat:*\n\n{filter_text}\n\n"
        f"Total: {len(filter_list)} filters\n\n"
        f"Use `/dfilter keyword` to delete a filter.",
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(Command("dfilter"))
async def delete_filter(message: types.Message):
    """Delete a filter"""
    if not is_authorized(message.from_user.id, message.from_user.username):
        await message.reply("❌ Aap authorized nahi hain!")
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
    if not is_authorized(message.from_user.id, message.from_user.username):
        await message.reply("❌ Aap authorized nahi hain!")
        return
    
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ Sirf owner yeh command use kar sakta hai!")
        return
    
    chat_id = str(message.chat.id)
    
    if chat_id in filters_data:
        filters_data[chat_id] = {}
        save_filters()
        await message.reply("✅ All filters deleted from this chat!")
    else:
        await message.reply("📋 No filters found in this chat!")

# Auto filter trigger
@dp.message(F.text)
async def check_filters(message: types.Message):
    """Check if message triggers any filter"""
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
# WELCOME SYSTEM (Rose Bot Style)
# ============================================

@dp.message(Command("setwelcome"))
async def set_welcome(message: types.Message):
    """Set welcome message - reply to a message and type /setwelcome"""
    if not is_authorized(message.from_user.id, message.from_user.username):
        await message.reply("❌ Aap authorized nahi hain!")
        return
    
    if not message.reply_to_message:
        await message.reply("⚠️ Please reply to a message to set as welcome!\n\nYou can reply to text, photo, video, etc.")
        return
    
    chat_id = str(message.chat.id)
    replied = message.reply_to_message
    
    # Parse custom text if provided
    args = message.text.split(maxsplit=1)
    custom_text = args[1] if len(args) > 1 else None
    
    # Store welcome data
    welcome_content = {}
    
    # Save message type and content
    if replied.text:
        welcome_content["type"] = "text"
        welcome_content["content"] = custom_text or replied.text
    elif replied.photo:
        welcome_content["type"] = "photo"
        welcome_content["file_id"] = replied.photo[-1].file_id
        welcome_content["caption"] = custom_text or replied.caption or ""
    elif replied.video:
        welcome_content["type"] = "video"
        welcome_content["file_id"] = replied.video.file_id
        welcome_content["caption"] = custom_text or replied.caption or ""
    elif replied.animation:
        welcome_content["type"] = "gif"
        welcome_content["file_id"] = replied.animation.file_id
        welcome_content["caption"] = custom_text or replied.caption or ""
    elif replied.sticker:
        welcome_content["type"] = "sticker"
        welcome_content["file_id"] = replied.sticker.file_id
    elif replied.document:
        welcome_content["type"] = "document"
        welcome_content["file_id"] = replied.document.file_id
        welcome_content["caption"] = custom_text or replied.caption or ""
    elif replied.voice:
        welcome_content["type"] = "voice"
        welcome_content["file_id"] = replied.voice.file_id
    elif replied.audio:
        welcome_content["type"] = "audio"
        welcome_content["file_id"] = replied.audio.file_id
        welcome_content["caption"] = custom_text or replied.caption or ""
    else:
        await message.reply("❌ Unsupported message type!")
        return
    
    welcome_data[chat_id] = welcome_content
    save_welcome()
    
    await message.reply(f"✅ Welcome message set for this chat!\n\nUse placeholders:\n`{{mention}}` - User mention\n`{{id}}` - User ID\n`{{name}}` - Full name", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("clearwelcome"))
async def clear_welcome(message: types.Message):
    """Clear welcome message for current chat"""
    if not is_authorized(message.from_user.id, message.from_user.username):
        await message.reply("❌ Aap authorized nahi hain!")
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
    if not is_authorized(message.from_user.id, message.from_user.username):
        await message.reply("❌ Aap authorized nahi hain!")
        return
    
    chat_id = str(message.chat.id)
    
    if chat_id not in welcome_data:
        await message.reply("ℹ️ No welcome message set for this chat!\n\nUse `/setwelcome` to set one.", parse_mode=ParseMode.MARKDOWN)
        return
    
    await message.reply("📋 *Current welcome settings:*\nType: " + welcome_data[chat_id].get("type", "text"), parse_mode=ParseMode.MARKDOWN)

# Auto welcome on new member join
@dp.message(F.new_chat_members)
async def welcome_new_member(message: types.Message):
    """Send welcome message when new member joins"""
    chat_id = str(message.chat.id)
    
    if chat_id not in welcome_data:
        return
    
    for new_member in message.new_chat_members:
        if new_member.id == (await main_bot.get_me()).id:
            continue
        
        user_id = new_member.id
        user_name = new_member.first_name
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
            elif welcome_type == "document":
                caption = parse_welcome_text(welcome_content.get("caption", ""), user_id, user_name, user_mention)
                await message.reply_document(
                    document=welcome_content["file_id"],
                    caption=caption,
                    parse_mode=ParseMode.HTML
                )
        except Exception as e:
            print(f"Error sending welcome: {e}")


# ============================================
# SPAM COMMANDS
# ============================================

@dp.message(Command("spam"))
async def start_spam(message: types.Message):
    global spam_active, spam_task, spam_stop_requested, active_bots, current_spam_count
    global spam_target_username, spam_target_id, spam_message, spam_starter
    
    user_id = message.from_user.id
    username = message.from_user.username
    
    if not is_authorized(user_id, username):
        owner_mention = format_user_mention(OWNER_ID, "L ɪ ɢ ʜ ᴛ")
        await message.reply(f"{owner_mention} {EMOJI4} ko baap bana pehle!", parse_mode=ParseMode.HTML)
        return
    
    if spam_active:
        await message.reply(f"⚠️ Spam already running! {current_spam_count}/{MAX_MESSAGES} messages sent. Use /stopspam")
        return
    
    # Get everything after /spam command
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.reply(
            f"⚠️ *USAGE:* `/spam message`\n\n"
            f"📌 *Example:* `/spam Hello brother`\n"
            f"🤖 *Bots:* {TOTAL_BOTS}\n"
            f"📊 *Max messages:* {MAX_MESSAGES}\n\n"
            f"💡 *Tip:* Jo bhi message likhoge woh spam hoga!",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    msg_text = args[1]
    
    status_msg = await message.reply(f"🚀 *Starting spam with {TOTAL_BOTS} bots...*\n\n📨 Message: {msg_text[:100]}", parse_mode=ParseMode.MARKDOWN)
    
    # Get target - if replying to someone, target that person, else target the sender
    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
        target_username = f"@{message.reply_to_message.from_user.username}" if message.reply_to_message.from_user.username else "User"
    else:
        target_user_id = message.from_user.id
        target_username = message.from_user.username or "self"
    
    active_bots = await create_all_bots()
    
    if len(active_bots) == 0:
        await status_msg.edit_text("❌ No bots working!", parse_mode=ParseMode.MARKDOWN)
        return
    
    spam_active = True
    spam_stop_requested = False
    spam_target_username = target_username
    spam_target_id = target_user_id
    spam_message = msg_text
    spam_starter = message.from_user
    
    spam_task = asyncio.create_task(send_spam_messages(active_bots, target_user_id, msg_text, MAX_MESSAGES))
    
    await status_msg.edit_text(
        f"✅ *SPAM STARTED!*\n\n"
        f"👤 *Started by:* {format_user_mention(user_id, message.from_user.first_name)}\n"
        f"🤖 *Bots:* {len(active_bots)}/{TOTAL_BOTS}\n"
        f"👊 *Target:* {target_username}\n"
        f"📨 *Message:* {msg_text[:100]}\n"
        f"🛑 Use `/stopspam` to stop",
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("stopspam"))
async def stop_spam(message: types.Message):
    global spam_active, spam_stop_requested, active_bots, spam_task, current_spam_count
    
    user_id = message.from_user.id
    
    if not is_authorized(user_id, message.from_user.username):
        await message.reply("❌ Aap spam stop nahi kar sakte!")
        return
    
    if not spam_active:
        await message.reply("ℹ️ No active spam running.")
        return
    
    owner_mention = format_user_mention(OWNER_ID, "L ɪ ɢ ʜ ᴛ")
    
    spam_active = False
    spam_stop_requested = True
    
    if spam_task and not spam_task.done():
        spam_task.cancel()
        try:
            await spam_task
        except asyncio.CancelledError:
            pass
    
    await close_all_bots(active_bots)
    active_bots = []
    
    await message.reply(
        f"{owner_mention} {BHAGWAAN_EMOJI} bhagwaan aye!\n\n🛑 *SPAM STOPPED!*\n📊 *Messages sent:* {current_spam_count}/{MAX_MESSAGES}",
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("spamstatus"))
async def spam_status(message: types.Message):
    if not is_authorized(message.from_user.id, message.from_user.username):
        await message.reply("❌ Aap authorized nahi hain!")
        return
    
    if spam_active:
        await message.reply(
            f"🔴 *SPAM ACTIVE*\n"
            f"📊 *Progress:* {current_spam_count}/{MAX_MESSAGES}\n"
            f"👊 *Target:* {spam_target_username}\n"
            f"🛑 Use /stopspam",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await message.reply(f"🟢 *NO SPAM*\n🤖 *Bots:* {TOTAL_BOTS}", parse_mode=ParseMode.MARKDOWN)


# ============================================
# ADMIN COMMANDS
# ============================================

@dp.message(Command("approve"))
async def approve_user(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ Sirf owner users approve kar sakta hai!")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply("⚠️ Usage: `/approve @username` or `/approve user_id`", parse_mode=ParseMode.MARKDOWN)
        return
    
    target = args[1]
    clean_target = target.replace('@', '').lower()
    
    approved_users.add(clean_target)
    save_approved_users()
    
    await message.reply(f"✅ USER APPROVED!\n👤 {target}\n🔓 Now can use spam commands", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("dapprove"))
async def dapprove_user(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ Sirf owner users dapprove kar sakta hai!")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply("⚠️ Usage: `/dapprove @username`", parse_mode=ParseMode.MARKDOWN)
        return
    
    target = args[1]
    clean_target = target.replace('@', '').lower()
    
    if clean_target not in approved_users:
        await message.reply(f"❌ {target} approved nahi hai!")
        return
    
    approved_users.remove(clean_target)
    save_approved_users()
    
    await message.reply(f"✅ USER DAPPROVED!\n👤 {target}\n🔒 Cannot use spam commands", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("approved"))
async def list_approved(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ Sirf owner yeh command dekh sakta hai!")
        return
    
    if not approved_users:
        await message.reply("📋 No approved users yet", parse_mode=ParseMode.MARKDOWN)
        return
    
    user_list = []
    for user in approved_users:
        if user.isdigit():
            user_list.append(f"🆔 `{user}`")
        else:
            user_list.append(f"👤 @{user}")
    
    await message.reply(f"✅ APPROVED USERS\n📋 Total: {len(approved_users)}\n\n" + "\n".join(user_list), parse_mode=ParseMode.MARKDOWN)


# ============================================
# /START COMMAND
# ============================================

@dp.message(Command("start"))
async def start_command(message: types.Message):
    user = message.from_user
    owner_mention = format_user_mention(OWNER_ID, "L ɪ ɢ ʜ ᴛ")
    user_mention = format_user_mention(user.id, user.first_name)
    
    is_auth = is_authorized(user.id, user.username)
    auth_status = "Authorized" if is_auth else "Not Authorized"
    
    message_text = (
        f"Hey {user_mention} {EMOJI1}\n\n"
        f"{EMOJI2} this is midnight manage bot {EMOJI3}\n\n\n"
        f"{EMOJI4} powered by : {owner_mention} {POWERED_BY_EMOJI}\n\n"
        f"{BOT_STATUS_EMOJI} *Bot Status*\n"
        f"{TOTAL_BOTS_EMOJI} Total Bots: {TOTAL_BOTS}\n"
        f"{AUTHORIZED_EMOJI} {auth_status}\n\n"
        f"📋 *Available Commands:*\n"
        f"🎯 `/spam message` - Spam any message\n"
        f"🛑 `/stopspam` - Stop spam\n"
        f"🔍 `/filter keyword` - Add filter (reply to msg)\n"
        f"📋 `/filters` - List all filters\n"
        f"❌ `/dfilter keyword` - Delete filter\n"
        f"👋 `/setwelcome` - Set welcome (reply to msg)\n"
        f"🗑️ `/clearwelcome` - Clear welcome\n"
        f"✅ `/approve @user` - Approve user (owner only)\n"
        f"❌ `/dapprove @user` - Remove approval\n"
        f"📊 `/spamstatus` - Check spam status"
    )
    
    bot_info = await main_bot.get_me()
    bot_username = bot_info.username
    
    add_button = InlineKeyboardButton(
        text="ADD ME TO YOUR GROUP",
        url=f"https://t.me/{bot_username}?startgroup=botstart",
        style="primary",
        icon_custom_emoji_id=ADD_BTN_EMOJI_ID
    )
    
    support_button = InlineKeyboardButton(
        text="SUPPORT",
        url="https://t.me/midnight_supportt",
        style="success",
        icon_custom_emoji_id=SUPPORT_BTN_EMOJI_ID
    )
    
    channel_button = InlineKeyboardButton(
        text="CHANNEL",
        url="https://t.me/midnight_chatclub",
        style="success",
        icon_custom_emoji_id=CHANNEL_BTN_EMOJI_ID
    )
    
    owner_button = InlineKeyboardButton(
        text="OWNER",
        url="https://t.me/light_speedy",
        style="danger",
        icon_custom_emoji_id=OWNER_BTN_EMOJI_ID
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [add_button],
        [support_button, channel_button],
        [owner_button]
    ])
    
    await message.reply(
        message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
        disable_web_page_preview=True
