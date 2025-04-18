### Стартовая структура проекта и базовая инициализация

# app/__init__.py
# Пустой, просто для импорта как пакета

# app/config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
    DATABASE_URL = os.getenv("DATABASE_URL")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPEN_DOTA_API = os.getenv("OPEN_DOTA_API")
    STRATZ_API = os.getenv("STRATZ_API")

config = Config()


# app/main.py
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from app.config import config
from app.handlers import register_handlers
from app.db.base import init_db


async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Инициализация базы данных
    await init_db()

    # Регистрация хендлеров
    register_handlers(dp)

    # Команды бота
    await bot.set_my_commands([
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="menu", description="Главное меню"),
    ])

    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
