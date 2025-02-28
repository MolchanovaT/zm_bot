import asyncio
import logging

from db import init_db  # Импортируем инициализацию БД
from misc import bot
from handlers import dp


async def main():
    logging.basicConfig(level=logging.INFO)

    # Проверяем и создаем БД, если её нет
    await init_db()

    # Очищаем возможные старые обновления и запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
