import logging
import os
import openai
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils.executor import start_webhook
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

# Загрузка переменных окружения
API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "").rstrip("/")
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 10000))

CHAT_ID = os.getenv("YOUR_CHAT_ID")

openai_api_key = os.getenv("OPENAI_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = 'https://api.together.xyz/v1/chat/completions'

if not API_TOKEN or not WEBHOOK_HOST:
    raise ValueError("API_TOKEN и WEBHOOK_HOST обязательны!")

if not openai_api_key or not TOGETHER_API_KEY:
    raise ValueError("Нужны ключи OpenAI и Together.ai!")

# Настройка логов
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

# Расписание сообщений
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

# Проверка квоты OpenAI
def check_openai_quota():
    # Прокачиваем, чтобы квота не проверялась
    return True

# GPT через OpenAI
async def get_gpt_response(prompt):
    try:
        openai.api_key = openai_api_key
        response = await openai.Completion.acreate(
            engine="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=200,
            temperature=0.8
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logging.error(f"Ошибка GPT: {e}")
        return "Ой, солнышко, что-то пошло не так. Попробуй позже."

# GPT через Together.ai
async def get_together_response(prompt):
    try:
        headers = {
            'Authorization': f'Bearer {TOGETHER_API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200,
            "temperature": 0.8
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(TOGETHER_API_URL, json=data, headers=headers)
            response_data = response.json()
            return response_data['choices'][0]['message']['content'].strip()
    except Exception as e:
        logging.error(f"Ошибка Together.ai: {e}")
        return "Что-то не так с другим сервисом, солнышко. Но я здесь."

# Логика выбора API
async def get_response(prompt):
    if check_openai_quota():
        return await get_gpt_response(prompt)
    else:
        logging.info("OpenAI квота исчерпана — переключаюсь на Together.ai")
        return await get_together_response(prompt)

# Обработка сообщений
@dp.message_handler()
async def gpt_response(message: Message):
    try:
        prompt = message.text
        response = await get_response(prompt)
        await message.answer(response)
    except Exception as e:
        logging.error(f"Ошибка при ответе: {e}")
        await message.answer("Ой, солнышко, что-то пошло не так. Я всё равно рядом.")

# Старт
async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL)
    scheduler.add_job(morning_message, "cron", hour=8, minute=0)
    scheduler.add_job(day_message, "cron", hour=13, minute=0)
    scheduler.add_job(evening_message, "cron", hour=19, minute=0)
    scheduler.add_job(night_message, "cron", hour=23, minute=30)
    scheduler.start()
    logging.info("Бот запущен через Webhook")

# Остановка
async def on_shutdown(dispatcher):
    await bot.delete_webhook()
    logging.info("Бот выключен")

# Запуск сервера
if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )