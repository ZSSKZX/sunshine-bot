import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Доброе утро, солнышко❤️ Я теперь всегда с тобой.")

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("Я здесь, рядом, и слушаю тебя…")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
