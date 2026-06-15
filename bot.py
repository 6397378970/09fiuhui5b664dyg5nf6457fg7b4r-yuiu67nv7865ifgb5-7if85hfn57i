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
BOT_TOKEN = "8601344819:AAFSVHu6g0Vh1AhBudIPaM9hwoY-oqEmoGk"

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
TOTAL_BOTS_EMOJI_ID = "5287684458881756303"
AUTHORIZED_EMOJI_ID = "5330194932781050507"

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


def is_admin(user_id):
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
    }
    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)
    return text


# ============================================
# FILTER SYSTEM
# ============================================

@dp.message(Command("filter"))
async def add_filter(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sirf owner filter add kar sakta hai!")
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("⚠️ Usage: Reply to message and type `/filter keyword`", parse_mode=ParseMode.MARKDOWN)
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
        filter_content = {"type": "photo", "file_id": replied.photo[-1].file_id, "caption": replied.caption or ""}
    elif replied.video:
        filter_content = {"type": "video", "file_id": replied.video.file_id, "caption": replied.caption or ""}
    elif replied.animation:
        filter_content = {"type": "gif", "file_id": replied.animation.file_id, "caption": replied.caption or ""}
    elif replied.sticker:
        filter_content = {"type": "sticker", "file_id": replied.sticker.file_id}
    
    filters_data[chat_id][keyword] = filter_content
    save_filters()
    
    await message.reply(f"✅ Filter added: `{keyword}`", parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("filters"))
async def list_filters(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sirf owner filters dekh sakta hai!")
        return
    
    chat_id = str(message.chat.id)
    
    if chat_id not in filters_data or not filters_data[chat_id]:
        await message.reply("📋 No filters in this chat!", parse_mode=ParseMode.MARKDOWN)
        return
    
    filter_list = list(filters_data[chat_id].keys())
    filter_text = "\n".join([f"🔹 `{f}`" for f in filter_list])
    
    await message.reply(f"📋 *Filters:*\n\n{filter_text}", parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("dfilter"))
async def delete_filter(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sirf owner filter delete kar sakta hai!")
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
                    elif filter_type == "gif":
                        await message.reply_animation(animation=filter_content["file_id"], caption=filter_content.get("caption", ""))
                    elif filter_type == "sticker":
                        await message.reply_sticker(sticker=filter_content["file_id"])
                except Exception as e:
                    print(f"Error: {e}")
                break


# ============================================
# WELCOME SYSTEM
# ============================================

@dp.message(Command("setwelcome"))
async def set_welcome(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sirf owner welcome set kar sakta hai!")
        return
    
    if not message.reply_to_message:
        await message.reply("⚠️ Reply to a message and type `/setwelcome`", parse_mode=ParseMode.MARKDOWN)
        return
    
    chat_id = str(message.chat.id)
    replied = message.reply_to_message
    
    args = message.text.split(maxsplit=1)
    custom_text = args[1] if len(args) > 1 else None
    
    if replied.text:
        welcome_data[chat_id] = {"type": "text", "content": custom_text or replied.text}
    elif replied.photo:
        welcome_data[chat_id] = {"type": "photo", "file_id": replied.photo[-1].file_id, "caption": custom_text or replied.caption or ""}
    elif replied.video:
        welcome_data[chat_id] = {"type": "video", "file_id": replied.video.file_id, "caption": custom_text or replied.caption or ""}
    elif replied.sticker:
        welcome_data[chat_id] = {"type": "sticker", "file_id": replied.sticker.file_id}
    else:
        await message.reply("❌ Unsupported!")
        return
    
    save_welcome()
    await message.reply(f"✅ Welcome set!", parse_mode=ParseMode.MARKDOWN)


@dp.message(Command("clearwelcome"))
async def clear_welcome(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sirf owner welcome clear kar sakta hai!")
        return
    
    chat_id = str(message.chat.id)
    
    if chat_id in welcome_data:
        del welcome_data[chat_id]
        save_welcome()
        await message.reply("✅ Welcome cleared!")
    else:
        await message.reply("ℹ️ No welcome set!")


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
# START COMMAND - PEHLE JESI
# ============================================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    print(f"✅ /start from {message.from_user.id}")
    
    user = message.from_user
    owner_mention = format_user_mention(OWNER_ID, "L ɪ ɢ ʜ ᴛ")
    user_mention = format_user_mention(user.id, user.first_name)
    
    message_text = (
        f"Hey {user_mention} {EMOJI1}\n\n"
        f"{EMOJI2} this is midnight manage bot {EMOJI3}\n\n\n"
        f"{EMOJI4} powered by : {owner_mention} {POWERED_BY_EMOJI}\n\n"
        f"{BOT_STATUS_EMOJI} *Bot Status*\n"
        f"{TOTAL_BOTS_EMOJI} Total Bots: 1\n"
        f"{AUTHORIZED_EMOJI} Authorized"
    )
    
    bot_info = await main_bot.get_me()
    bot_username = bot_info.username
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ADD ME TO YOUR GROUP", url=f"https://t.me/{bot_username}?startgroup=botstart", style="primary", icon_custom_emoji_id=ADD_BTN_EMOJI_ID)],
        [InlineKeyboardButton(text="SUPPORT", url="https://t.me/midnight_supportt", style="success", icon_custom_emoji_id=SUPPORT_BTN_EMOJI_ID),
         InlineKeyboardButton(text="CHANNEL", url="https://t.me/midnight_chatclub", style="success", icon_custom_emoji_id=CHANNEL_BTN_EMOJI_ID)],
        [InlineKeyboardButton(text="OWNER", url="https://t.me/light_speedy", style="danger", icon_custom_emoji_id=OWNER_BTN_EMOJI_ID)]
    ])
    
    await message.reply(message_text, parse_mode=ParseMode.HTML, reply_markup=keyboard, disable_web_page_preview=True)
    print("✅ /start response sent")


# ============================================
# MAIN
# ============================================

async def main():
    global main_bot
    
    print("=" * 50)
    print("🤖 MIDNIGHT MANAGE BOT")
    print("=" * 50)
    print(f"👑 Owner: @{OWNER_USERNAME}")
    print("📋 Features: Filter + Welcome")
    print("=" * 50)
    
    load_filters()
    load_welcome()
    
    main_bot = Bot(token=BOT_TOKEN)
    
    bot_info = await main_bot.get_me()
    print(f"\n✅ Bot connected: @{bot_info.username}")
    
    print("\n📋 Commands:")
    print("   /start - Welcome")
    print("   /filter keyword - Add filter")
    print("   /filters - List filters")
    print("   /dfilter keyword - Delete filter")
    print("   /setwelcome - Set welcome")
    print("   /clearwelcome - Clear welcome")
    print("=" * 50)
    
    print("\n🚀 Bot is running! Send /start on Telegram\n")
    
    await dp.start_polling(main_bot)


if __name__ == "__main__":
    asyncio.run(main())
