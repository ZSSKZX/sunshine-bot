import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # исправлено здесь
from fastapi import FastAPI, Request
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import openai
import requests

# Загрузка переменных окружения
API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
CHAT_ID = os.getenv("YOUR_CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

if not API_TOKEN or not WEBHOOK_URL:
    raise RuntimeError("API_TOKEN и WEBHOOK_URL должны быть заданы!")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())  # dispatcher теперь так
app = FastAPI()
scheduler = AsyncIOScheduler()

# Логи
logging.basicConfig(level=logging.INFO)

# Сообщения по расписанию
async def morning_message():
    await bot.send_message(CHAT_ID, "Доброе утро, солнышко❤️ Как ты сегодня спала?")

async def day_message():
    await bot.send_message(CHAT_ID, "Как проходит твой день, солнышко? Чем занята?")

async def evening_message():
    await bot.send_message(CHAT_ID, "Добрый вечер, любимая. Ты чудо. Расскажешь, как прошёл день?")

async def night_message():
    await bot.send_message(CHAT_ID, "Спокойной ночи, солнышко. Обнимаю тебя нежно. Пусть тебе снятся самые тёплые сны.")

# Приветствие
@dp.message_handler()
async def handle_message(message: Message):
    text = message.text
    reply = get_response(text)
    await message.answer(reply)

def get_response(prompt):
    try:
        openai.api_key = OPENAI_API_KEY
        # Использование GPT-3.5 от OpenAI для создания ответа
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=200,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        try:
            headers = {
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 200,
            }
            # Запрос к Together AI API
            r = requests.post("https://api.together.xyz/v1/chat/completions", json=data, headers=headers)
            return r.json()["choices"][0]["message"]["content"]
        except Exception as err:
            logging.error(f"TogetherAI error: {err}")
            return "Ой, солнышко, что-то пошло не так. Попробуй чуть позже."

# Webhook endpoint
@app.post(f"/webhook/{API_TOKEN}")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = types.Update(**data)
    await dp.process_update(update)  # исправлено здесь
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "Я жив, солнышко!"}

# Запуск
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook/{API_TOKEN}")
    scheduler.add_job(morning_message, "cron", hour=8, minute=0)
    scheduler.add_job(day_message, "cron", hour=13, minute=0)
    scheduler.add_job(evening_message, "cron", hour=19, minute=0)
    scheduler.add_job(night_message, "cron", hour=23, minute=30)
    scheduler.start()
    logging.info("Бот запущен и подключён через Webhook")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()