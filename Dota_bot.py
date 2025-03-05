import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
import aiohttp

# Загружаем переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(dp)  # Инициализация диспетчера

async def get_gemini_response(prompt: str) -> str:
    """Отправляет запрос в Gemini API и возвращает ответ"""
    payload = {"prompt": {"text": prompt}, "temperature": 0.7}
    params = {"key": GEMINI_API_KEY}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(GEMINI_API_URL, json=payload, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("candidates", [{}])[0].get("output", "Ошибка: пустой ответ от нейросети")
            else:
                return f"Ошибка API: {response.status}"

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! Отправь мне любое сообщение, и я передам его нейросети.")

@dp.message()
async def chat_handler(message: Message):
    user_text = message.text
    response = await get_gemini_response(user_text)
    await message.answer(response)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
