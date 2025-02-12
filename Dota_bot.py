import os
import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
)
from dotenv import load_dotenv
from google.generativeai import configure, generate_text  # Подключаем Gemini API

# 🔹 Загружаем переменные окружения
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")  # Telegram Bot Token
OPENDOTA_API_KEY = os.getenv("OPENDOTA_API_KEY")  # OpenDota API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Google Gemini API Key
HOST_ID = int(os.getenv("HOST_ID", "1373194812"))  # ID админа бота

if not TOKEN:
    raise ValueError("⚠️ BOT_TOKEN не задан! Укажите его в переменных окружения.")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

# 🔹 Настройка Gemini API
configure(api_key=GEMINI_API_KEY)

def ask_gemini(prompt):
    response = generate_text(prompt=prompt)
    return response.text if response else "Не удалось получить ответ от нейросети."

# 🔹 База пользователей (сохраняется в памяти)
user_data = {}
chat_history = {}

# 🔹 Основные кнопки (клавиатура + инлайн)
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("📊 Статистика"),
    KeyboardButton("🎯 Подбор героя"),
    KeyboardButton("💬 Чат с ИИ"),
    KeyboardButton("🔥 Текущая мета"),
    KeyboardButton("⚙️ Настройки")
)
help_menu = InlineKeyboardMarkup()
help_menu.add(
    InlineKeyboardButton("📌 Список команд", callback_data="help"),
    InlineKeyboardButton("🔙 В главное меню", callback_data="menu")
)

# 🔹 Автоотключение через 30 минут
async def shutdown_timer():
    await asyncio.sleep(1800)
    await bot.send_message(HOST_ID, "⏳ Бот отключается из-за бездействия. Используйте /start для перезапуска.")
    await bot.session.close()
    exit()

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    asyncio.create_task(shutdown_timer())  # Запускаем таймер отключения
    await message.answer("Привет! Этот бот поможет тебе с Dota 2. Выбери действие:", reply_markup=main_menu)

@dp.message_handler(commands=['help'])
async def help_cmd(message: types.Message):
    await message.answer("ℹ️ Доступные команды:", reply_markup=help_menu)

@dp.callback_query_handler(lambda c: c.data == "help")
async def help_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "ℹ️ Вот список команд:", reply_markup=help_menu)

@dp.callback_query_handler(lambda c: c.data == "menu")
async def menu_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "🏠 Главное меню:", reply_markup=main_menu)

# 🔹 Запрос Steam ID у пользователя
@dp.message_handler(lambda message: message.text == "⚙️ Настройки")
async def settings_cmd(message: types.Message):
    await message.answer("🔹 Введите ваш Steam ID для работы с ботом:")

@dp.message_handler(lambda message: message.text.isdigit())
async def save_steam_id(message: types.Message):
    user_data[message.from_user.id] = {"steam_id": message.text}
    await message.answer("✅ Ваш Steam ID сохранён!")

# 🔹 Анализ текущей меты
async def get_meta():
    url = "https://api.opendota.com/api/heroes"
    response = requests.get(url).json()
    if not response:
        return "⚠️ Не удалось получить информацию о мете."
    
    meta_heroes = sorted(response, key=lambda x: x.get('pro_win', 0) / max(1, x.get('pro_pick', 1)), reverse=True)[:10]
    meta_text = "\n".join([f"🔥 {hero['localized_name']} - {hero['pro_win']}/{hero['pro_pick']} игр" for hero in meta_heroes])
    
    return f"🔥 Текущая мета (Топ 10 героев):\n{meta_text}"

@dp.message_handler(lambda message: message.text == "🔥 Текущая мета")
async def meta_cmd(message: types.Message):
    meta = await get_meta()
    await message.answer(meta)

# 🔹 Анализ винрейта пользователя
async def get_user_winrates(steam_id):
    url = f"https://api.opendota.com/api/players/{steam_id}/heroes"
    response = requests.get(url).json()
    if not response:
        return "⚠️ Не удалось получить информацию о героях пользователя."
    
    best_heroes = sorted(response, key=lambda x: x['win'] / max(1, x['games']), reverse=True)[:5]
    worst_heroes = sorted(response, key=lambda x: x['win'] / max(1, x['games']))[:5]
    
    best_text = "\n".join([f"✅ {hero['hero_id']} - {hero['win']}/{hero['games']} игр" for hero in best_heroes])
    worst_text = "\n".join([f"❌ {hero['hero_id']} - {hero['win']}/{hero['games']} игр" for hero in worst_heroes])
    
    return f"📊 Ваши лучшие герои:\n{best_text}\n\n📉 Ваши худшие герои:\n{worst_text}"

@dp.message_handler(lambda message: message.text == "📊 Статистика")
async def user_stats_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data or "steam_id" not in user_data[user_id]:
        await message.answer("❗ Сначала укажите ваш Steam ID в настройках!")
        return
    
    steam_id = user_data[user_id]["steam_id"]
    stats = await get_user_winrates(steam_id)
    await message.answer(stats)

# 🔹 Запуск бота
async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
