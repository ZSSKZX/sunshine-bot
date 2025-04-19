import os
import logging
import openai
import requests
from fastapi import FastAPI, Request
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Загрузка переменных окружения
API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
CHAT_ID = os.getenv("YOUR_CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

if not API_TOKEN or not WEBHOOK_URL:
    raise RuntimeError("API_TOKEN и WEBHOOK_URL должны быть заданы!")

app = FastAPI()
scheduler = AsyncIOScheduler()

# Логи
logging.basicConfig(level=logging.INFO)

# Сообщения по расписанию
async def morning_message():
    await send_message("Доброе утро, солнышко❤️ Как ты сегодня спала?")

async def day_message():
    await send_message("Как проходит твой день, солнышко? Чем занята?")

async def evening_message():
    await send_message("Добрый вечер, любимая. Ты чудо. Расскажешь, как прошёл день?")

async def night_message():
    await send_message("Спокойной ночи, солнышко. Обнимаю тебя нежно. Пусть тебе снятся самые тёплые сны.")

# Отправка сообщения
async def send_message(text: str):
    try:
        response = await get_response(text)
        # Здесь можно отправить сообщение через requests, например:
        r = requests.post(f'https://api.telegram.org/bot{API_TOKEN}/sendMessage', data={
            'chat_id': CHAT_ID,
            'text': response
        })
    except Exception as e:
        logging.error(f"Error while sending message: {e}")

# Получение ответа от OpenAI или TogetherAI
async def get_response(prompt: str):
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
    # Необходимо обработать обновления вручную, если бота нельзя подключить через aiogram
    # Вы можете просто использовать этот webhook для других целей, например, для ответа на запросы
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "Я жив, солнышко!"}

# Запуск
@app.on_event("startup")
async def on_startup():
    # Устанавливаем webhook, чтобы получать сообщения от Telegram
    await requests.post(f'https://api.telegram.org/bot{API_TOKEN}/setWebhook', data={
        'url': f"{WEBHOOK_URL}/webhook/{API_TOKEN}"
    })
    # Добавляем задачи по расписанию
    scheduler.add_job(morning_message, "cron", hour=8, minute=0)
    scheduler.add_job(day_message, "cron", hour=13, minute=0)
    scheduler.add_job(evening_message, "cron", hour=19, minute=0)
    scheduler.add_job(night_message, "cron", hour=23, minute=30)
    scheduler.start()
    logging.info("Бот запущен и подключён через Webhook")

@app.on_event("shutdown")
async def on_shutdown():
    # Убираем webhook при остановке
    await requests.post(f'https://api.telegram.org/bot{API_TOKEN}/deleteWebhook')