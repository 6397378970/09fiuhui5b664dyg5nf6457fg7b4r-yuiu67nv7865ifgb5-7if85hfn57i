import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# YAHAN APNA NAYA TOKEN DAALO
BOT_TOKEN = "8601344819:AAFSVHu6g0Vh1AhBudIPaM9hwoY-oqEmoGk"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

print("🚀 Bot starting...")

@dp.message(Command("start"))
async def start(msg: types.Message):
    print("✅ /start received!")
    await msg.reply("✅ Bot is working! Send /help")

@dp.message(Command("help"))
async def help(msg: types.Message):
    await msg.reply("Commands:\n/start - Check bot\n/help - This message")

@dp.message()
async def echo(msg: types.Message):
    await msg.reply(f"You said: {msg.text}")

async def main():
    bot_info = await bot.get_me()
    print(f"✅ Bot: @{bot_info.username}")
    print("✅ Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
