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

dp = Dispatcher()

# ============================================
# COMMANDS
# ============================================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    owner_mention = format_user_mention(OWNER_ID, "L ɪ ɢ ʜ ᴛ")
    user_mention = format_user_mention(user.id, user.first_name)
    
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

main_bot = Bot(token=MAIN_BOT_TOKEN)

bot_info = await main_bot.get_me()

print(f"✅ Bot connected: @{bot_info.username}")
print("📋 Available Commands:")
print("   /start")
