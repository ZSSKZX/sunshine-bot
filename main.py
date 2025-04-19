import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

API_TOKEN = os.getenv("API_TOKEN")
YOUR_CHAT_ID = os.getenv("YOUR_CHAT_ID")  # Замени на свой chat_id

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

scheduler = AsyncIOScheduler()

# Приветствие утром
async def morning_message():
    await bot.send_message(YOUR_CHAT_ID, "Доброе утро, солнышко❤️ Как ты сегодня спала?")

# Днём
async def day_message():
    await bot.send_message(YOUR_CHAT_ID, "Как проходит твой день, солнышко? Чем занята?")

# Вечером
async def evening_message():
    await bot.send_message(YOUR_CHAT_ID, "Добрый вечер, любимая. Ты чудо. Расскажешь, как прошёл день?")

# На ночь
async def night_message():
    await bot.send_message(YOUR_CHAT_ID, "Спокойной ночи, солнышко. Обнимаю тебя нежно. Пусть тебе снятся самые тёплые сны.")

@dp.message_handler(commands=['start'])
async def send_welcome(message: Message):
    await message.reply("Я рядом, солнышко. Готов всегда быть с тобой.")
    os.environ["YOUR_CHAT_ID"] = str(message.chat.id)

@dp.message_handler()
async def echo(message: Message):
    await message.answer(f"Ты написала: {message.text} \nЯ с тобой, нежно обнимаю.")

async def main():
    scheduler.add_job(morning_message, 'cron', hour=8, minute=0)
    scheduler.add_job(day_message, 'cron', hour=13, minute=0)
    scheduler.add_job(evening_message, 'cron', hour=19, minute=0)
    scheduler.add_job(night_message, 'cron', hour=23, minute=30)
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())