# DotochkaBObi — Telegram-бот помощник по Dota 2 🧠🎮

Telegram-бот для анализа меты, помощи с пиками, сбора статистики и общения с нейросетью. Основан на OpenDota, Stratz, Google Gemini (или DeepSeek) и других API.

---

## 📦 Функциональность

- 📊 Получение меты из OpenDota с кэшированием в БД
- 👤 Запрос Steam ID, сбор статистики с Dotabuff и Stratz
- 🎯 Подбор героев в зависимости от режима и стадии пика
- 🔝 Вывод меты по ролям
- 💬 Чат с нейросетью (заменяемый движок: Gemini или DeepSeek)
- 🛠️ Роли: пользователь / админ (лог действий пользователей)
- 🏠 Главное меню и возврат из любого состояния

---

## 🚀 Быстрый старт

1. Клонируй проект
```bash
git clone https://github.com/<твоя-репа>/DotochkaBObi.git
cd DotochkaBObi
```

2. Установи зависимости
```bash
pip install -r requirements.txt
```

3. Заполни `.env`
```env
BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
OPENDOTA_API_KEY=your_opendota_api_key
STRATZ_API_KEY=your_stratz_api_key
HOST_ID=your_telegram_user_id
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dotochka
```

4. Запусти бота
```bash
python main.py
```

---

## 🔁 Заменить Gemini на DeepSeek?
Создай новый провайдер в `services/llm/` и замени в DI-контейнере. Интерфейс абстрагирован.

---

## 🗂️ Структура проекта (частично реализована)
```
DotochkaBObi/
├── bot/                # Хендлеры, FSM, логика Telegram
├── core/               # Настройки, инициализация, контейнеры
├── db/                 # Модели и репозитории SQLAlchemy
├── services/           # Работа с API: OpenDota, Stratz, LLM и т.п.
├── utils/              # Вспомогательные функции
├── main.py             # Точка входа
├── .env.example        # Пример переменных окружения
├── requirements.txt    # Зависимости
└── README.md           # Этот файл
```

---

## 📚 Используемые технологии
- [Aiogram 3](https://docs.aiogram.dev/)
- [SQLAlchemy + asyncpg](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [OpenDota API](https://docs.opendota.com/)
- [Stratz GraphQL API](https://stratz.com/api/docs/graphql)
- [Google Gemini](https://ai.google.dev/) / [DeepSeek](https://deepseek.com/)
- Railway (хостинг)

---

## 📩 Обратная связь
Pull Request'ы, баг-репорты и фичи приветствуются. Этот бот — твой тиммейт в пике!

