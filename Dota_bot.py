import os
import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
)
from dotenv import load_dotenv

# 🔹 Загружаем переменные окружения
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")  # Telegram Bot Token
OPENDOTA_API_KEY = os.getenv("OPENDOTA_API_KEY")  # OpenDota API Key (если есть)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # DeepSeek API Key (если есть)
HOST_ID = int(os.getenv("HOST_ID", "1373194812"))  # ID админа бота

if not TOKEN:
    raise ValueError("⚠️ BOT_TOKEN не задан! Укажите его в переменных окружения.")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🔹 База пользователей (временная, лучше потом заменить на БД)
user_data = {}
chat_history = {}

# 🔹 Клавиатура с главными кнопками
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("📊 Статистика"),
    KeyboardButton("🎯 Подбор героя"),
    KeyboardButton("💬 Чат с ИИ")
)

# 🔹 Инлайн-клавиатура для статистики
stats_menu = InlineKeyboardMarkup()
stats_menu.add(
    InlineKeyboardButton("🔥 Топ-5 лучших героев", callback_data="top_5"),
    InlineKeyboardButton("💀 Топ-5 худших героев", callback_data="worst_5"),
)
stats_menu.add(InlineKeyboardButton("📌 Текущая мета", callback_data="meta"))

# 🔹 Старт бота
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Привет! Этот бот поможет тебе с Dota 2. Выбери действие:", reply_markup=main_menu)

# 🔹 Запрос Steam ID у пользователя
@dp.message_handler(lambda message: message.text == "📊 Статистика")
async def ask_steam_id(message: types.Message):
    await message.answer("Отправь свой **Steam ID** или ссылку на профиль, чтобы я мог получить твою статистику.")

# 🔹 Обработка Steam ID
@dp.message_handler(lambda message: message.text.isdigit())
async def save_steam_id(message: types.Message):
    steam_id = message.text
    user_data[message.from_user.id] = {"steam_id": steam_id}
    await message.answer("Steam ID сохранён! Выбери, что тебе нужно:", reply_markup=stats_menu)

# 🔹 Получение статистики с OpenDota
def get_dota_stats(steam_id):
    url = f"https://api.opendota.com/api/players/{steam_id}/heroes"
    headers = {"Authorization": f"Bearer {OPENDOTA_API_KEY}"} if OPENDOTA_API_KEY else {}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None
    return response.json()

# 🔹 Обработчик инлайн-кнопок (топ-5 лучших и худших героев)
@dp.callback_query_handler(lambda call: call.data in ["top_5", "worst_5"])
async def handle_stats_buttons(call: types.CallbackQuery):
    user_id = call.from_user.id
    if user_id not in user_data:
        await call.message.answer("Ты не указал Steam ID! Отправь его сначала.")
        return

    steam_id = user_data[user_id]["steam_id"]
    stats = get_dota_stats(steam_id)
    if not stats:
        await call.message.answer("Ошибка при получении статистики.")
        return

    if call.data == "top_5":
        top_5 = sorted(stats, key=lambda x: x['win'] / x['games'], reverse=True)[:5]
        result = "\n".join([f"{hero['hero_id']} – {hero['win']}/{hero['games']} побед" for hero in top_5])
        await call.message.answer(f"🔥 **Топ-5 лучших героев:**\n{result}")

    elif call.data == "worst_5":
        worst_5 = sorted(stats, key=lambda x: x['win'] / x['games'])[:5]
        result = "\n".join([f"{hero['hero_id']} – {hero['win']}/{hero['games']} побед" for hero in worst_5])
        await call.message.answer(f"💀 **Топ-5 худших героев:**\n{result}")

# 🔹 Чат с ИИ через DeepSeek API
def deepseek_chat(text):
    if not DEEPSEEK_API_KEY:
        return "🤖 [ИИ]: API-ключ отсутствует. Подключите DeepSeek API для работы ИИ."

    url = "https://api.deepseek.com/chat"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    data = {"prompt": text}

    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        return "🤖 [ИИ]: Ошибка при обработке запроса."
    
    return response.json().get("response", "🤖 [ИИ]: Ошибка обработки ответа.")

@dp.message_handler(lambda message: message.text == "💬 Чат с ИИ")
async def chat_with_ai(message: types.Message):
    await message.answer("Отправь мне сообщение, и я попробую ответить как ИИ.")

@dp.message_handler()
async def ai_response(message: types.Message):
    user_id = message.from_user.id
    chat_history.setdefault(user_id, []).append(message.text)  # Сохраняем историю чатов
    response = deepseek_chat(message.text)
    await message.answer(response)

# 🔹 Завершение работы при неактивности 30 минут
inactive_time = 1800  # 30 минут в секундах
last_activity = None

async def shutdown_if_inactive():
    global last_activity
    while True:
        await asyncio.sleep(300)
        if last_activity and (asyncio.get_event_loop().time() - last_activity > inactive_time):
            print("💤 Бот не используется 30 минут. Завершаю работу...")
            exit(0)

@dp.message_handler()
async def handle_activity(message: types.Message):
    global last_activity
    last_activity = asyncio.get_event_loop().time()

# 🔹 Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
