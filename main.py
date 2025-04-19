import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из .env

API_TOKEN = os.getenv("API_TOKEN")
CHAT_ID = os.getenv("YOUR_CHAT_ID")  # Укажи здесь вручную, если не работает через /start

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

scheduler = AsyncIOScheduler()

# Утро
async def morning_message():
    if CHAT_ID:
        await bot.send_message(CHAT_ID, "Доброе утро, солнышко❤️ Как ты сегодня спала?")

# День
async def day_message():
    if CHAT_ID:
        await bot.send_message(CHAT_ID, "Как проходит твой день, солнышко? Чем занята?")

# Вечер
async def evening_message():
    if CHAT_ID:
        await bot.send_message(CHAT_ID, "Добрый вечер, любимая. Ты чудо. Расскажешь, как прошёл день?")

# Ночь
async def night_message():
    if CHAT_ID:
        await bot.send_message(CHAT_ID, "Спокойной ночи, солнышко. Обнимаю тебя нежно. Пусть тебе снятся самые тёплые сны.")

@dp.message_handler(commands=["start"])
async def send_welcome(message: Message):
    await message.answer("Я рядом, солнышко. Готов всегда быть с тобой.")
    # Введи свой chat_id вручную в .env, т.к. так бот не может его сохранить между перезапусками

@dp.message_handler()
async def echo(message: Message):
    await message.answer(f"Ты написала: {message.text} \nЯ с тобой, нежно обнимаю.")

async def main():
    scheduler.add_job(morning_message, "cron", hour=8, minute=0)
    scheduler.add_job(day_message, "cron", hour=13, minute=0)
    scheduler.add_job(evening_message, "cron", hour=19, minute=0)
    scheduler.add_job(night_message, "cron", hour=23, minute=30)
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())