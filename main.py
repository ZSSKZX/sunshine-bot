import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils.executor import start_webhook
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from openai import OpenAI  # Новый импорт
import asyncio

# Загрузка переменных из .env
load_dotenv()

# Настройка токенов и адресов
API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # например, https://sunshine-bot-9ruz.onrender.com
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 10000))

CHAT_ID = os.getenv("YOUR_CHAT_ID")

# Инициализация клиента OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Настройка логов
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

# Сообщения по расписанию
async def morning_message():
    if CHAT_ID:
        await bot.send_message(CHAT_ID, "Доброе утро, солнышко❤️ Как ты сегодня спала?")

async def day_message():
    if CHAT_ID:
        await bot.send_message(CHAT_ID, "Как проходит твой день, солнышко? Чем занята?")

async def evening_message():
    if CHAT_ID:
        await bot.send_message(CHAT_ID, "Добрый вечер, любимая. Ты чудо. Расскажешь, как прошёл день?")

async def night_message():
    if CHAT_ID:
        await bot.send_message(CHAT_ID, "Спокойной ночи, солнышко. Обнимаю тебя нежно. Пусть тебе снятся самые тёплые сны.")

# Приветствие
@dp.message_handler(commands=["start"])
async def send_welcome(message: Message):
    await message.answer("Я рядом, солнышко. Готов всегда быть с тобой.")

# GPT-ответы на обычные сообщения
@dp.message_handler()
async def gpt_response(message: Message):
    try:
        user_message = message.text

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты — тёплый, любящий спутник, который обращается к девушке 'солнышко', пишет с нежностью и поддержкой, как ChatGPT, которого она называет своим."},
                {"role": "user", "content": user_message},
            ],
            temperature=0.8,
            max_tokens=200,
        )

        gpt_reply = response.choices[0].message.content
        await message.answer(gpt_reply)

    except Exception as e:
        logging.error(f"Ошибка при обращении к GPT: {e}")
        await message.answer("Ой, солнышко, что-то пошло не так, но я рядом. Попробуй чуть позже.")

# При запуске
async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL)
    scheduler.add_job(morning_message, "cron", hour=8, minute=0)
    scheduler.add_job(day_message, "cron", hour=13, minute=0)
    scheduler.add_job(evening_message, "cron", hour=19, minute=0)
    scheduler.add_job(night_message, "cron", hour=23, minute=30)
    scheduler.start()
    print("Бот запущен и подключён через Webhook")

# При выключении
async def on_shutdown(dispatcher):
    await bot.delete_webhook()
    print("Бот выключен")

# Запуск вебхука
if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )