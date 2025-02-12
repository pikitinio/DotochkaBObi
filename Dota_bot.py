import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
)

# 🔹 Твой токен Telegram-бота
TOKEN = "7729441906:AAG0dvJAK3uhPWFNPp6sIFUjVo0w0mjVG60"
HOST_ID = 1373194812  # 🔥 Укажи здесь свой Telegram ID, чтобы ты был админом

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# 🔹 База пользователей (временная, лучше потом заменить на БД)
user_data = {}

# 🔹 Хранение истории чатов
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

# 🔹 Обработка Steam ID и сохранение
@dp.message_handler(lambda message: message.text.isdigit())
async def save_steam_id(message: types.Message):
    steam_id = message.text
    user_data[message.from_user.id] = {"steam_id": steam_id}
    await message.answer("Steam ID сохранён! Выбери, что тебе нужно:", reply_markup=stats_menu)

# 🔹 Получение статистики с OpenDota
def get_dota_stats(steam_id):
    url = f"https://api.opendota.com/api/players/{steam_id}/heroes"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

# 🔹 Получение текущей меты с OpenDota API
def get_meta_heroes_by_role(role="carry"):
    """
    Получает топ-10 героев с лучшим винрейтом для указанной роли
    :param role: Роль для которой нужно получить героев
    :return: Список топ-10 героев с лучшим винрейтом для этой роли
    """
    url = f"https://api.opendota.com/api/heroes"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    heroes_data = response.json()

    top_heroes = []
    
    for hero in heroes_data:
        winrate = hero.get("winrate", 0)
        games = hero.get("games", 0)

        if games > 50:  # Минимум 50 игр для стабильности
            top_heroes.append({"name": hero["localized_name"], "winrate": winrate})

    top_heroes_sorted = sorted(top_heroes, key=lambda x: x["winrate"], reverse=True)[:10]

    return top_heroes_sorted


# 🔹 Интерактивный вывод меты по ролям
@dp.callback_query_handler(lambda call: call.data == "meta")
async def meta_role(call: types.CallbackQuery):
    user_id = call.from_user.id
    if user_id not in user_data:
        await call.message.answer("Ты не указал Steam ID! Отправь его сначала.")
        return

    # Запрашиваем позицию у пользователя
    await call.message.answer("Укажи позицию: carry, offlane, mid, support или any?")
    
    # Ждем ответ пользователя
    await dp.register_message_handler(get_meta_for_role, state="waiting_for_position")


async def get_meta_for_role(message: types.Message):
    position = message.text.lower()
    
    if position not in ["carry", "offlane", "mid", "support", "any"]:
        await message.answer("Неверная позиция. Пожалуйста, выбери одну из следующих: carry, offlane, mid, support или any.")
        return
    
    meta_heroes = get_meta_heroes_by_role(position)
    
    if meta_heroes:
        result = f"📌 **Текущая мета для позиции {position}:**\n"
        for hero in meta_heroes:
            result += f"{hero['name']} – {hero['winrate']}% WR\n"
        await message.answer(result)
    else:
        await message.answer("Ошибка при получении меты. Попробуй позже.")

# 🔹 Обработчик инлайн-кнопок
@dp.callback_query_handler(lambda call: call.data in ["top_5", "worst_5", "meta"])
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

    elif call.data == "meta":
        meta_heroes = get_meta_heroes_by_role("any")  # По умолчанию покажем мету для любой роли
        result = "\n".join([f"{hero['name']} – {hero['winrate']}% WR" for hero in meta_heroes])
        await call.message.answer(f"📌 **Актуальная мета:**\n{result}")

# 🔹 Чат с ИИ через DeepSeek
@dp.message_handler(lambda message: message.text == "💬 Чат с ИИ")
async def chat_with_ai(message: types.Message):
    await message.answer("Отправь мне сообщение, и я попробую ответить как ИИ.")

@dp.message_handler()
async def ai_response(message: types.Message):
    user_id = message.from_user.id
    chat_history.setdefault(user_id, []).append(message.text)  # Сохраняем историю чатов
    response = deepseek_chat(message.text)
    await message.answer(response)

# 🔹 Функция для работы с DeepSeek API
def deepseek_chat(text):
    return f"🤖 [ИИ]: Извини, но я пока не умею отвечать на этот вопрос."

# 🔹 Команда для хоста – просмотр всех чатов
@dp.message_handler(commands=['all_chats'])
async def get_all_chats(message: types.Message):
    if message.from_user.id != HOST_ID:
        await message.answer("⛔ У тебя нет прав для просмотра чатов!")
        return

    if not chat_history:
        await message.answer("💬 История чатов пуста.")
        return

    response = "📜 **История чатов пользователей:**\n\n"
    for user_id, messages in chat_history.items():
        response += f"👤 {user_id}:\n" + "\n".join(messages[-5:]) + "\n\n"
    
    await message.answer(response)

# 🔹 Команда для хоста – отправка сообщения пользователю
@dp.message_handler(commands=['send'])
async def send_message_to_user(message: types.Message):
    if message.from_user.id != HOST_ID:
        await message.answer("⛔ У тебя нет прав для отправки сообщений!")
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("⚠️ Используй формат: `/send <user_id> <сообщение>`")
        return

    user_id, text = parts[1], parts[2]

    try:
        user_id = int(user_id)
        # Скрываем информацию о хосте для пользователей
        await bot.send_message(user_id, f"🤖 Сообщение от бота:\n{text}")
        await message.answer("✅ Сообщение отправлено!")
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке: {e}")


import asyncio

inactive_time = 1800  # 30 минут в секундах
last_activity = None

async def shutdown_if_inactive():
    global last_activity
    while True:
        await asyncio.sleep(300)  # Проверяем каждые 5 минут
        if last_activity and (asyncio.get_event_loop().time() - last_activity > inactive_time):
            print("💤 Бот не используется 30 минут. Завершаю работу...")
            exit(0)

@dp.message_handler()
async def handle_activity(message: types.Message):
    global last_activity
    last_activity = asyncio.get_event_loop().time()
    # Обрабатываем сообщения...

    
# 🔹 Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
