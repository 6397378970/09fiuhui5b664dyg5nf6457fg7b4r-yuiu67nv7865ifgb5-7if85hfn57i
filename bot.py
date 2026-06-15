import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode

# ============================================
# CONFIGURATION
# ============================================

OWNER_ID = 7676301555
OWNER_USERNAME = "light_speedy"

# Main bot token
MAIN_BOT_TOKEN = "8776304610:AAFpTm36X1c2wsYJVLnrzYjbEjeAi_dt3rc"

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
ADD_BTN_EMOJI_ID = "5253652327734192243"      # Add me to your group
SUPPORT_BTN_EMOJI_ID = "5443038326535759644"  # Support
CHANNEL_BTN_EMOJI_ID = "5771695636411847302"  # Channel
OWNER_BTN_EMOJI_ID = "6136204644625423818"    # Owner

# Message mein dikhne wale emojis (start command ke liye)
EMOJI1_ID = "5454390891466726015"    # Hey ke aage
EMOJI2_ID = "5355051922862653659"    # this is midnight ke aage
EMOJI3_ID = "5424766882823544746"    # manage bot ke baad
EMOJI4_ID = "6276090299232031662"    # powered by ke aage
BHAGWAAN_EMOJI_ID = "5285070644864628879"  # bhagwaan emoji

# ============================================
# NAYE EMOJI IDs (Tune diye)
# ============================================
POWERED_BY_EMOJI_ID = "5208727996315220567"      # powered by : LIGHT ke piche
BOT_STATUS_EMOJI_ID = "5231200819986047254"      # *Bot Status* ke aage
TOTAL_BOTS_EMOJI_ID = "5287684458881756303"      # Total Bots: 12 ke aage
AUTHORIZED_EMOJI_ID = "5330194932781050507"      # Authorized ke aage

# Premium emoji format
EMOJI1 = f'<tg-emoji emoji-id="{EMOJI1_ID}">⭐️</tg-emoji>'
EMOJI2 = f'<tg-emoji emoji-id="{EMOJI2_ID}">✨</tg-emoji>'
EMOJI3 = f'<tg-emoji emoji-id="{EMOJI3_ID}">💎</tg-emoji>'
EMOJI4 = f'<tg-emoji emoji-id="{EMOJI4_ID}">🔥</tg-emoji>'
BHAGWAAN_EMOJI = f'<tg-emoji emoji-id="{BHAGWAAN_EMOJI_ID}">👑</tg-emoji>'

# Naye emoji format
POWERED_BY_EMOJI = f'<tg-emoji emoji-id="{POWERED_BY_EMOJI_ID}">⚡</tg-emoji>'
BOT_STATUS_EMOJI = f'<tg-emoji emoji-id="{BOT_STATUS_EMOJI_ID}">📊</tg-emoji>'
TOTAL_BOTS_EMOJI = f'<tg-emoji emoji-id="{TOTAL_BOTS_EMOJI_ID}">🤖</tg-emoji>'
AUTHORIZED_EMOJI = f'<tg-emoji emoji-id="{AUTHORIZED_EMOJI_ID}">✅</tg-emoji>'

APPROVED_FILE = "approved_users.json"

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
current_spam_count = 0

dp = Dispatcher()


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


async def get_user_id(username: str):
    try:
        username = username.replace('@', '').strip()
        user = await main_bot.get_chat(f"@{username}")
        return user.id
    except Exception as e:
        print(f"Error: {e}")
        return None


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
# COMMAND HANDLERS
# ============================================

@dp.message(Command("approve"))
async def approve_user(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ Sirf owner users approve kar sakta hai!")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply("⚠️ Usage: `/approve @username`", parse_mode=ParseMode.MARKDOWN)
        return
    
    target = args[1]
    clean_target = target.replace('@', '').lower()
    
    approved_users.add(clean_target)
    save_approved_users()
    
    await message.reply(f"✅ USER APPROVED!\n👤 {target}", parse_mode=ParseMode.MARKDOWN)


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
    
    await message.reply(f"✅ USER DAPPROVED!\n👤 {target}", parse_mode=ParseMode.MARKDOWN)


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
    
    args = message.text.split(maxsplit=2)
    
    if len(args) < 3:
        await message.reply(
            f"⚠️ *USAGE:* `/spam @username message`\n\n"
            f"📌 *Example:* `/spam @light_speedy Hello`\n"
            f"🤖 *Bots:* {TOTAL_BOTS}\n"
            f"📊 *Max messages:* {MAX_MESSAGES}",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    target_username = args[1]
    msg_text = args[2]
    
    if not target_username.startswith('@'):
        target_username = '@' + target_username
    
    status_msg = await message.reply(f"🚀 *Starting spam to {target_username}* (Max: {MAX_MESSAGES} msgs)", parse_mode=ParseMode.MARKDOWN)
    
    target_user_id = await get_user_id(target_username)
    
    if not target_user_id:
        await status_msg.edit_text(f"❌ Target {target_username} not found!", parse_mode=ParseMode.MARKDOWN)
        return
    
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


@dp.message(Command("status"))
async def status_check(message: types.Message):
    if not is_authorized(message.from_user.id, message.from_user.username):
        await message.reply("❌ Aap authorized nahi hain!")
        return
    
    if spam_active:
        await message.reply(
            f"🔴 *SPAM ACTIVE*\n📊 *Progress:* {current_spam_count}/{MAX_MESSAGES}\n🛑 Use /stopspam",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await message.reply(
            f"🟢 *NO SPAM*\n🤖 *Bots:* {TOTAL_BOTS}\n✅ *Approved:* {len(approved_users)}",
            parse_mode=ParseMode.MARKDOWN
        )


# ============================================
# /START COMMAND - WITH ALL CUSTOM EMOJIS
# ============================================

@dp.message(Command("start"))
async def start_command(message: types.Message):
    user = message.from_user
    owner_mention = format_user_mention(OWNER_ID, "L ɪ ɢ ʜ ᴛ")
    user_mention = format_user_mention(user.id, user.first_name)
    
    is_auth = is_authorized(user.id, user.username)
    auth_status = "Authorized" if is_auth else "Not Authorized"
    
    # ============================================
    # MESSAGE WITH ALL CUSTOM EMOJIS (JESA TU NE BATAYA)
    # ============================================
    # Format: 
    # Hey @user 😂
    # ✨ this is midnight manage bot 💎
    # 🔥 powered by : LIGHT ⚡
    # 
    # 📊 *Bot Status*
    # 🤖 Total Bots: 12
    # ✅ Authorized
    # ============================================
    
    message_text = (
        f"Hey {user_mention} {EMOJI1}\n\n"
        f"{EMOJI2} this is midnight manage bot {EMOJI3}\n\n\n"
        f"{EMOJI4} powered by : {owner_mention} {POWERED_BY_EMOJI}\n\n"
        f"{BOT_STATUS_EMOJI} *Bot Status*\n"
        f"{TOTAL_BOTS_EMOJI} Total Bots: {TOTAL_BOTS}\n"
        f"{AUTHORIZED_EMOJI} {auth_status}"
    )
    
    bot_info = await main_bot.get_me()
    bot_username = bot_info.username
    
    # Buttons with icon custom emoji
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
    )


# ============================================
# MAIN
# ============================================

async def main():
    global main_bot
    
    load_approved_users()
    
    print("=" * 50)
    print("🤖 PREMIUM BOT - ALL CUSTOM EMOJIS")
    print("=" * 50)
    print(f"👑 Owner: @{OWNER_USERNAME}")
    print(f"📊 Total Bots: {TOTAL_BOTS}")
    print(f"✅ Approved Users: {len(approved_users)}")
    print("=" * 50)
    print("\n📋 Commands:")
    print("   /start - Welcome with custom emojis")
    print("   /spam @user message - Start spam")
    print("   /stopspam - Stop spam")
    print("   /approve @user - Approve user")
    print("   /dapprove @user - Remove approval")
    print("   /status - Check status")
    print("=" * 50)
    
    main_bot = Bot(token=MAIN_BOT_TOKEN)
    
    print("\n✅ Bot is running...\n")
    await dp.start_polling(main_bot)


if __name__ == "__main__":
    asyncio.run(main())
