import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils.executor import start_webhook
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # https://sunshine-bot-9ruz.onrender.com
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 10000))

CHAT_ID = os.getenv("YOUR_CHAT_ID")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
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

@dp.message_handler()
async def echo(message: Message):
    await message.answer(f"Ты написала: {message.text} \nЯ с тобой, нежно обнимаю.")

async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL)
    scheduler.add_job(morning_message, "cron", hour=8, minute=0)
    scheduler.add_job(day_message, "cron", hour=13, minute=0)
    scheduler.add_job(evening_message, "cron", hour=19, minute=0)
    scheduler.add_job(night_message, "cron", hour=23, minute=30)
    scheduler.start()
    print("Бот запущен и подключён через Webhook")

async def on_shutdown(dispatcher):
    await bot.delete_webhook()
    print("Бот выключен")

if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )