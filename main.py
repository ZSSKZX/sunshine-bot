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
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBAPP_PORT = int(os.getenv("PORT", 10000))
CHAT_ID = os.getenv("YOUR_CHAT_ID")

WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"

openai_api_key = os.getenv("OPENAI_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

if openai_api_key is None or TOGETHER_API_KEY is None:
    raise ValueError("API ключи для OpenAI или Together.ai не найдены в переменных окружения!")

TOGETHER_API_URL = 'https://api.together.xyz/v1/chat/completions'

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

@dp.message_handler(commands=["start"])
async def send_welcome(message: Message):
    await message.answer("Я рядом, солнышко. Готов всегда быть с тобой.")

def check_openai_quota():
    try:
        openai.api_key = openai_api_key
        usage = openai.Account.retrieve()
        return usage['data']['quota']['remaining'] > 0
    except openai.error.OpenAIError as e:
        logging.error(f"Ошибка при проверке квоты OpenAI: {e}")
        return False

async def get_gpt_response(prompt):
    try:
        openai.api_key = openai_api_key
        response = await openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=200,
            temperature=0.8
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logging.error(f"Ошибка при обращении к GPT: {e}")
        return "Ой, солнышко, что-то пошло не так, но я рядом. Попробуй чуть позже."

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
        logging.error(f"Ошибка при обращении к Together.ai: {e}")
        return "Ой, солнышко, что-то пошло не так с другим сервисом, но я рядом."

async def get_response(prompt):
    if check_openai_quota():
        return await get_gpt_response(prompt)
    else:
        logging.info("Квота на OpenAI исчерпана, переключаемся на Together.ai")
        return await get_together_response(prompt)

@dp.message_handler()
async def gpt_response(message: Message):
    try:
        user_message = message.text
        response = await get_response(user_message)
        await message.answer(response)
    except Exception as e:
        logging.error(f"Ошибка при обработке сообщения: {e}")
        await message.answer("Ой, солнышко, что-то пошло не так, но я рядом. Попробуй чуть позже.")

# Стартап
async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL)
    scheduler.add_job(morning_message, "cron", hour=8, minute=0)
    scheduler.add_job(day_message, "cron", hour=13, minute=0)
    scheduler.add_job(evening_message, "cron", hour=19, minute=0)
    scheduler.add_job(night_message, "cron", hour=23, minute=30)
    scheduler.start()
    print("Бот запущен через webhook")

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