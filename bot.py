import asyncio
import json
import os
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.enums import ParseMode

print("🚀 Starting Midnight Manage Bot...")

# ============================================
# CONFIGURATION
# ============================================

OWNER_ID = 7676301555
OWNER_USERNAME = "light_speedy"

# Main bot token
MAIN_BOT_TOKEN = "8601344819:AAGcnxlnBWSFSbStwe6hrNro8jxD9NnX1T0"

# Extra bots tokens (11 bots)
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
spam_target_id = None
active_bots = []
main_bot = None
approved_users = set()
filters_data = {}
welcome_data = {}
current_spam_count = 0

dp = Dispatcher()


# ============================================
# FILE FUNCTIONS
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

def is_authorized(user_id):
    if user_id == OWNER_ID:
        return True
    if str(user_id) in approved_users:
        return True
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
        "{username}": f"@{user_name}" if user_name else "No username"
    }
    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)
    return text


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
    
    print(f"\n🎯 Total {len(bots)}/{TOTAL_BOTS} bots ready!\n")
    return bots

async def close_all_bots(bots):
    for bot in bots:
        try:
            await bot.close()
        except:
            pass

async def send_spam_messages(bots_list, target_id, message_text):
    global spam_active, current_spam_count
    
    current_spam_count = 0
    msg_index = 1
    
    while spam_active and current_spam_count < MAX_MESSAGES:
        for bot_id, bot in enumerate(bots_list, 1):
            if not spam_active or current_spam_count >= MAX_MESSAGES:
                break
            
            try:
                if bot_id == 1:
                    final_msg = f"🤖 [MAIN] {message_text} [{msg_index}]"
                else:
                    final_msg = f"🔄 [Bot-{bot_id-1}] {message_text} [{msg_index}]"
                
                await bot.send_message(chat_id=target_id, text=final_msg)
                current_spam_count += 1
                print(f"✅ Msg {current_spam_count}/{MAX_MESSAGES} - Bot {bot_id}")
                await asyncio.sleep(SPAM_DELAY)
            except Exception as e:
                print(f"❌ Bot {bot_id} error: {e}")
        
        msg_index += 1
    
    spam_active = False
    print(f"✅ Spam completed: {current_spam_count} messages sent")


# ============================================
# WELCOME SYSTEM
# ============================================

@dp.message(Command("setwelcome"))
async def set_welcome(message: types.Message):
    if not is_authorized(message.from_user.id):
        await message.reply("❌ Aap authorized nahi hain!")
        return
    
    if not message.reply_to_message:
        await message.reply("⚠️ Please reply to a message to set as welcome!\n\nExample: Reply to any message with `/setwelcome`", parse_mode=ParseMode.MARKDOWN)
        return
    
    chat_id = str(message.chat.id)
    replied = message.reply_to_message
    
    args = message.text.split(maxsplit=1)
    custom_text = args[1] if len(args) > 1 else None
    
    welcome_content = {}
    
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
        await message.reply("❌ Unsupported message type! You can set welcome from: text, photo, video, gif, sticker, document, voice, audio")
        return
    
    welcome_data[chat_id] = welcome_content
    save_welcome()
    
    await message.reply(
        f"✅ Welcome message set for this chat!\n\n"
        f"📊 Type: {welcome_content['type']}\n\n"
        f"📝 *Placeholders you can use:*\n"
        f"`{{mention}}` - User mention (blue)\n"
        f"`{{id}}` - User ID\n"
        f"`{{name}}` - Full name\n"
        f"`{{first_name}}` - First name only\n"
        f"`{{username}}` - Username",
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(Command("clearwelcome"))
async def clear_welcome(message: types.Message):
    if not is_authorized(message.from_user.id):
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
    if not is_authorized(message.from_user.id):
        await message.reply("❌ Aap authorized nahi hain!")
        return
    
    chat_id = str(message.chat.id)
    
    if chat_id not in welcome_data:
        await message.reply("ℹ️ No welcome message set for this chat!\n\nUse `/setwelcome` to set one.", parse_mode=ParseMode.MARKDOWN)
        return
    
    wc = welcome_data[chat_id]
    preview = f"✅ *Current Welcome Settings*\n\n📊 Type: {wc['type']}"
    
    if wc['type'] == 'text':
        preview += f"\n📝 Content: `{wc['content'][:100]}`"
    else:
        preview += f"\n📝 Caption: `{wc.get('caption', 'None')[:100]}`"
    
    await message.reply(preview, parse_mode=ParseMode.MARKDOWN)

# Auto welcome on new member join
@dp.message(F.new_chat_members)
async def welcome_new_member(message: types.Message):
    chat_id = str(message.chat.id)
    
    if chat_id not in welcome_data:
        return
    
    for new_member in message.new_chat_members:
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
            elif welcome_type == "document":
                caption = parse_welcome_text(welcome_content.get("caption", ""), user_id, user_name, user_mention)
                await message.reply_document(
                    document=welcome_content["file_id"],
                    caption=caption,
                    parse_mode=ParseMode.HTML
                )
            elif welcome_type == "voice":
                await message.reply_voice(voice=welcome_content["file_id"])
            elif welcome_type == "audio":
                caption = parse_welcome_text(welcome_content.get("caption", ""), user_id, user_name, user_mention)
                await message.reply_audio(
                    audio=welcome_content["file_id"],
                    caption=caption,
                    parse_mode=ParseMode.HTML
                )
        except Exception as e:
            print(f"Error sending welcome: {e}")


# ============================================
# FILTER SYSTEM
# ============================================

@dp.message(Command("filter"))
async def add_filter(message: types.Message):
    if not is_authorized(message.from_user.id):
        await message.reply("❌ Aap authorized nahi hain!")
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("⚠️ Usage: Reply to a message and type `/filter keyword`\n\nExample: `/filter hello`", parse_mode=ParseMode.MARKDOWN)
        return
    
    keyword = args[1].lower().strip()
    chat_id = str(message.chat.id)
    
    if not message.reply_to_message:
        await message.reply("⚠️ Please reply to a message to filter it!\n\n1. Reply to any message\n2. Type `/filter keyword`", parse_mode=ParseMode.MARKDOWN)
        return
    
    replied = message.reply_to_message
    
    if chat_id not in filters_data:
        filters_data[chat_id] = {}
    
    filter_content = {
        "type": "text",
        "content": replied.text or replied.caption or "No content"
    }
    
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
    
    await message.reply(f"✅ Filter added!\n🔑 Keyword: `{keyword}`\n📊 Type: {filter_content['type']}", parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("filters"))
async def list_filters(message: types.Message):
    if not is_authorized(message.from_user.id):
        await message.reply("❌ Aap authorized nahi hain!")
        return
    
    chat_id = str(message.chat.id)
    
    if chat_id not in filters_data or not filters_data[chat_id]:
        await message.reply("📋 No filters in this chat!\n\nUse `/filter keyword` to add one.", parse_mode=ParseMode.MARKDOWN)
        return
    
    filter_list = list(filters_data[chat_id].keys())
    filter_text = "\n".join([f"🔹 `{f}`" for f in filter_list])
    
    await message.reply(
        f"📋 *Filters in this chat:*\n\n{filter_text}\n\n📊 Total: {len(filter_list)} filters\n\n❌ Delete: `/dfilter keyword`",
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(Command("dfilter"))
async def delete_filter(message: types.Message):
    if not is_authorized(message.from_user.id):
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
    if not is_authorized(message.from_user.id):
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

# Auto trigger filters
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
# SPAM COMMANDS
# ============================================

@dp.message(Command("spam"))
async def cmd_spam(message: types.Message):
    global spam_active, spam_task, active_bots, spam_target_id, current_spam_count
    
    if not is_authorized(message.from_user.id):
        owner_mention = format_user_mention(OWNER_ID, "L ɪ ɢ ʜ ᴛ")
        await message.reply(f"{owner_mention} {EMOJI4} ko baap bana pehle!", parse_mode=ParseMode.HTML)
        return
    
    if spam_active:
        await message.reply("⚠️ Spam already running! Use /stopspam")
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(f"⚠️ Usage: `/spam message`\nExample: `/spam Hello`", parse_mode=ParseMode.MARKDOWN)
        return
    
    msg_text = args[1]
    
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        target_name = message.reply_to_message.from_user.first_name
    else:
        target_id = message.from_user.id
        target_name = message.from_user.first_name
    
    await message.reply(f"🚀 Starting {TOTAL_BOTS} bots spam to {target_name}...")
    
    active_bots = await create_all_bots()
    if len(active_bots) == 0:
        await message.reply("❌ No bots working!")
        return
    
    spam_active = True
    spam_target_id = target_id
    current_spam_count = 0
    
    spam_task = asyncio.create_task(send_spam_messages(active_bots, target_id, msg_text))
    
    await message.reply(
        f"✅ *SPAM STARTED!*\n\n👤 Target: {target_name}\n🤖 Bots: {len(active_bots)}/{TOTAL_BOTS}\n📨 Message: {msg_text[:50]}\n🛑 Use /stopspam to stop",
        parse_mode=ParseMode.MARKDOWN
    )


@dp.message(Command("stopspam"))
async def cmd_stopspam(message: types.Message):
    global spam_active, active_bots, spam_task
    
    if not is_authorized(message.from_user.id):
        await message.reply("❌ Aap spam stop nahi kar sakte!")
        return
    
    if not spam_active:
        await message.reply("ℹ️ No active spam running.")
        return
    
    owner_mention = format_user_mention(OWNER_ID, "L ɪ ɢ ʜ ᴛ")
    
    spam_active = False
    
    if spam_task and not spam_task.done():
        spam_task.cancel()
    
    await close_all_bots(active_bots)
    active_bots = []
    
    await message.reply(
        f"{owner_mention} {BHAGWAAN_EMOJI} bhagwaan aye!\n\n🛑 *SPAM STOPPED!*\n📊 Messages sent: {current_spam_count}/{MAX_MESSAGES}",
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    if not is_authorized(message.from_user.id):
        await message.reply("❌ Aap authorized nahi hain!")
        return
    
    if spam_active:
        await message.reply(
            f"🔴 *SPAM ACTIVE*\n📊 Progress: {current_spam_count}/{MAX_MESSAGES}\n🛑 Use /stopspam",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await message.reply(
            f"🟢 *NO SPAM*\n🤖 Total Bots: {TOTAL_BOTS}\n✅ Approved Users: {len(approved_users)}",
            parse_mode=ParseMode.MARKDOWN
        )


# ============================================
# ADMIN COMMANDS
# ============================================

@dp.message(Command("approve"))
async def cmd_approve(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ Sirf owner approve kar sakta hai!")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Usage: `/approve @username` or `/approve user_id`", parse_mode=ParseMode.MARKDOWN)
        return
    
    target = args[1]
    clean_target = target.replace('@', '').lower()
    
    approved_users.add(clean_target)
    save_approved_users()
    
    await message.reply(f"✅ APPROVED!\n👤 {target}", parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("dapprove"))
async def cmd_dapprove(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ Sirf owner dapprove kar sakta hai!")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Usage: `/dapprove @username`", parse_mode=ParseMode.MARKDOWN)
        return
    
    target = args[1]
    clean_target = target.replace('@', '').lower()
    
    if clean_target not in approved_users:
        await message.reply(f"❌ {target} approved nahi hai!")
        return
    
    approved_users.remove(clean_target)
    save_approved_users()
    
    await message.reply(f"✅ DAPPROVED!\n👤 {target}", parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("approved"))
async def cmd_approvedlist(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ Sirf owner dekh sakta hai!")
        return
    
    if not approved_users:
        await message.reply("📋 No approved users", parse_mode=ParseMode.MARKDOWN)
        return
    
    users = []
    for u in approved_users:
        if u.isdigit():
            users.append(f"🆔 `{u}`")
        else:
            users.append(f"👤 @{u}")
    
    await message.reply(f"✅ APPROVED USERS\n📋 Total: {len(approved_users)}\n\n" + "\n".join(users), parse_mode=ParseMode.MARKDOWN)


# ============================================
# START COMMAND
# ============================================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    owner_mention = format_user_mention(OWNER_ID, "L ɪ ɢ ʜ ᴛ")
    user_mention = format_user_mention(user.id, user.first_name)
    
    is_auth = is_authorized(user.id)
    auth_status = "Authorized" if is_auth else "Not Authorized"
    
    text = (
        f"Hey {user_mention} {EMOJI1}\n\n"
        f"{EMOJI2} this is midnight manage bot {EMOJI3}\n\n\n"
        f"{EMOJI4} powered by : {owner_mention} {POWERED_BY_EMOJI}\n\n"
        f"{BOT_STATUS_EMOJI} *Bot Status*\n"
        f"{TOTAL_BOTS_EMOJI} Total Bots: {TOTAL_BOTS}\n"
        f"{AUTHORIZED_EMOJI} {auth_status}\n\n"
        f"📋 *Commands:*\n"
        f"`/spam message` - Start spam (12 bots)\n"
        f"`/stopspam` - Stop spam\n"
        f"`/status` - Check status\n"
        f"`/filter word` - Add filter (reply to msg)\n"
        f"`/filters` - List all filters\n"
        f"`/dfilter word` - Delete filter\n"
        f"`/setwelcome` - Set welcome (reply to msg)\n"
        f"`/clearwelcome` - Clear welcome\n"
        f"`/viewwelcome` - View welcome\n"
        f"`/approve @user` - Approve user (owner)\n"
        f"`/dapprove @user` - Remove approval (owner)\n"
        f"`/approved` - List approved users (owner)"
    )
    
    bot_info = await main_bot.get_me()
    bot_username = bot_info.username
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ADD ME TO YOUR GROUP", url=f"https://t.me/{bot_username}?startgroup=botstart", style="primary", icon_custom_emoji_id=ADD_BTN_EMOJI_ID)],
        [InlineKeyboardButton(text="SUPPORT", url="https://t.me/midnight_supportt", style="success", icon_custom_emoji_id=SUPPORT_BTN_EMOJI_ID),
         InlineKeyboardButton(text="CHANNEL", url="https://t.me/midnight_chatclub", style="success", icon_custom_emoji_id=CHANNEL_BTN_EMOJI_ID)],
        [InlineKeyboardButton(text="OWNER", url="https://t.me/light_speedy", style="danger", icon_custom_emoji_id=OWNER_BTN_EMOJI_ID)]
    ])
    
    await message.reply(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)


# ============================================
# MAIN
# ============================================

async def main():
    global main_bot
    
    print("=" * 50)
    print("🤖 MIDNIGHT MANAGE BOT - COMPLETE")
    print("=" * 50)
    print(f"👑 Owner: @{OWNER_USERNAME} (ID: {OWNER_ID})")
    print(f"📊 Total Bots: {TOTAL_BOTS}")
    print("=" * 50)
    
    load_approved_users()
    load_filters()
    load_welcome()
    
    main_bot = Bot(token=MAIN_BOT_TOKEN)
    
    bot_info = await main_bot.get_me()
    print(f"\n✅ Bot connected: @{bot_info.username}")
    print(f"✅ Bot ID: {bot_info.id}")
    
    print("\n📋 Available Commands:")
    print("   🚀 /spam message - 12 bots spam")
    print("   🛑 /stopspam - Stop spam")
    print("   📊 /status - Check status")
    print("   🔍 /filter word - Add filter")
    print("   📋 /filters - List filters")
    print("   ❌ /dfilter word - Delete filter")
    print("   👋 /setwelcome - Set welcome message")
    print("   🗑️ /clearwelcome - Clear welcome")
    print("   👀 /viewwelcome - View welcome")
    print("   ✅ /approve @user - Approve user")
    print("   ❌ /dapprove @user - Remove approval")
    print("   📋 /approved - List approved users")
    print("=" * 50)
    
    print("\n🚀 Bot is running! Send /start on Telegram\n")
    
    await dp.start_polling(main_bot)


if __name__ == "__main__":
    asyncio.run(main())
