import asyncio
import logging
from aiogram import Bot, Dispatcher
from core.config import settings
from core.handlers import setup_handlers
from core.db.session import async_session
from core.utils.commands import set_bot_commands


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    await set_bot_commands(bot)
    setup_handlers(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await async_session.close()


if __name__ == "__main__":
    asyncio.run(main())
