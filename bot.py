import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

# ============================================
# CONFIGURATION
# ============================================

OWNER_ID = 7676301555
MAIN_BOT_TOKEN = "8601344819:AAGcnxlnBWSFSbStwe6hrNro8jxD9NnX1T0"

# Create bot and dispatcher
bot = Bot(token=MAIN_BOT_TOKEN)
dp = Dispatcher()

print("🚀 Starting bot...")

# ============================================
# COMMANDS
# ============================================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    print(f"✅ /start command received from {message.from_user.id}")
    await message.reply("✅ Bot is working! Send /help for commands")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    print(f"✅ /help command received from {message.from_user.id}")
    await message.reply("Commands:\n/start - Check if bot works\n/help - This message\n/spam - Spam command")

@dp.message(Command("spam"))
async def cmd_spam(message: types.Message):
    print(f"✅ /spam command received from {message.from_user.id}")
    await message.reply("Spam command received! But full version has 12 bots.")

@dp.message()
async def echo(message: types.Message):
    print(f"📩 Message from {message.from_user.id}: {message.text}")
    await message.reply(f"You said: {message.text}")

# ============================================
# MAIN
# ============================================

async def main():
    print("=" * 40)
    print("🤖 TEST BOT - CHECKING COMMANDS")
    print("=" * 40)
    
    bot_info = await bot.get_me()
    print(f"✅ Bot connected: @{bot_info.username}")
    print(f"✅ Bot ID: {bot_info.id}")
    print("=" * 40)
    print("\n🚀 Bot is running! Send /start on Telegram\n")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
