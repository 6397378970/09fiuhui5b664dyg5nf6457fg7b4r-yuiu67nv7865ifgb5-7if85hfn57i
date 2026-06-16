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
MAIN_BOT_TOKEN = "8601344819:AAETXDvfDAApnjO1LymXu7fD4Y9laNE_VSw"

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

# Premium emoji IDs
ADD_BTN_EMOJI_ID = "5253652327734192243"
SUPPORT_BTN_EMOJI_ID = "5443038326535759644"
CHANNEL_BTN_EMOJI_ID = "5771695636411847302"
OWNER_BTN_EMOJI_ID = "6136204644625423818"

EMOJI1_ID = "5454390891466726015"
EMOJI2_ID = "5355051922862653659"
EMOJI3_ID = "5287684458881756303"
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

APPROVED_FILE = "approved_users.json"

# Global variables
spam_active = False
spam_task = None
spam_target_id = None
active_bots = []
main_bot = None
approved_users = set()
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
# COMMANDS
# ============================================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    owner_mention = format_user_mention(OWNER_ID, "L ɪ ɢ ʜ ᴛ")
    user_mention = format_user_mention(user.id, user.first_name)
    
    is_auth = is_authorized(user.id)
    auth_status = "Authorized" if is_auth else "Not Authorized"
    
    text = (
        f"{EMOJI1} ʜᴇʏ {user_mention}\n\n"
        f"{EMOJI2} ᴛʜɪs ɪs ᴍɪᴅɴɪɢʜᴛ ᴍᴀɴᴀɢᴇ ʙᴏᴛ {EMOJI3}\n\n\n"
        f"{EMOJI4} Pᴏᴡᴇʀᴇᴅ Bʏ : {owner_mention} {POWERED_BY_EMOJI}\n\n"
    )
    
    bot_info = await main_bot.get_me()
    bot_username = bot_info.username
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ADD ME TO YOUR GROUP", url=f"https://t.me/{bot_username}?startgroup=botstart", style="primary", icon_custom_emoji_id=ADD_BTN_EMOJI_ID)],
        [InlineKeyboardButton(text="SUPPORT", url="https://t.me/midnight_chatclub", style="success", icon_custom_emoji_id=SUPPORT_BTN_EMOJI_ID),
         InlineKeyboardButton(text="CHANNEL", url="https://t.me/midnight_supportt", style="success", icon_custom_emoji_id=CHANNEL_BTN_EMOJI_ID)],
        [InlineKeyboardButton(text="OWNER", url="https://t.me/light_speedy", style="danger", icon_custom_emoji_id=OWNER_BTN_EMOJI_ID)]
    ])
    
    await message.reply(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)


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
    
    # Get target (reply to someone or self)
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
# MAIN
# ============================================

async def main():
    global main_bot
    
    print("=" * 50)
    print("🤖 MIDNIGHT MANAGE BOT")
    print("=" * 50)
    print(f"👑 Owner: @{OWNER_USERNAME} (ID: {OWNER_ID})")
    print(f"📊 Total Bots: {TOTAL_BOTS}")
    print("=" * 50)
    
    load_approved_users()
    
    main_bot = Bot(token=MAIN_BOT_TOKEN)
    
    bot_info = await main_bot.get_me()
    print(f"\n✅ Bot connected: @{bot_info.username}")
    print(f"✅ Bot ID: {bot_info.id}")
    
    print("\n📋 Available Commands:")
    print("   /start - Welcome message")
    print("   /spam message - Start spam (12 bots)")
    print("   /stopspam - Stop spam")
    print("   /status - Check status")
    print("   /approve @user - Approve user")
    print("   /dapprove @user - Remove approval")
    print("   /approved - List approved users")
    print("=" * 50)
    
    print("\n🚀 Bot is running! Send /start on Telegram\n")
    
    await dp.start_polling(main_bot)


if __name__ == "__main__":
    asyncio.run(main())
