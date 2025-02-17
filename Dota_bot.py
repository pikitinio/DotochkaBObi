import asyncio
import os
import time
import requests
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv

# Загружаем API-ключи
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENDOTA_API_KEY = os.getenv("OPENDOTA_API_KEY")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Инициализация Google Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Список пользователей, которые активировали бота (для автоотключения)
active_users = {}
INACTIVITY_LIMIT = 1800  # 30 минут


# Функция для проверки активности пользователей
async def check_activity():
    while True:
        current_time = time.time()
        for user_id in list(active_users.keys()):
            if current_time - active_users[user_id] > INACTIVITY_LIMIT:
                await bot.send_message(user_id, "Бот выключается из-за бездействия. Напишите команду, чтобы снова запустить его.")
                del active_users[user_id]
        await asyncio.sleep(60)


# Главное меню
def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🔍 Анализ профиля"), KeyboardButton("🎮 Помощь с пиком"))
    return keyboard


# Получение данных о профиле через OpenDota API
def get_player_data(steam_id):
    url = f"https://api.opendota.com/api/players/{steam_id}?api_key={OPENDOTA_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# Анализ винрейта героев
def get_winrate_heroes(steam_id, top=True):
    url = f"https://api.opendota.com/api/players/{steam_id}/heroes?api_key={OPENDOTA_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        heroes = response.json()
        sorted_heroes = sorted(heroes, key=lambda x: x["win"] / x["games"], reverse=top)
        return sorted_heroes[:5]
    return None


# Функция взаимодействия с Google Gemini API
def ask_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text


# Обработчик команд
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    active_users[user_id] = time.time()
    await message.answer("Привет! Я Dota 2 бот с нейросетью. Чем могу помочь?", reply_markup=main_menu())


# Обработчик сообщений
@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    active_users[user_id] = time.time()

    user_text = message.text.lower()

    # Обрабатываем запрос через Google Gemini
    response = ask_gemini(f"Пользователь спрашивает: {user_text}. Какая команда ему нужна?")

    if "анализ профиля" in response:
        await message.answer("Введите ваш Steam ID:")
    elif "помощь с пиком" in response:
        await message.answer("Введите выбранных героев и вашу роль:")
    elif "лучшие герои" in response:
        await message.answer("Введите ваш Steam ID, чтобы узнать 5 лучших героев по винрейту.")
    elif "худшие герои" in response:
        await message.answer("Введите ваш Steam ID, чтобы узнать 5 худших героев по винрейту.")
    elif "текущая мета" in response:
        await message.answer("Укажите позицию, и я покажу 10 лучших героев на ней.")
    else:
        await message.answer("Не понял ваш запрос. Попробуйте переформулировать.")


# Запуск проверки активности
async def on_startup(dp):
    asyncio.create_task(check_activity())


# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
