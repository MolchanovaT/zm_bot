import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

import config

BOT_TOKEN = config.BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer("Привет! Я тестовый бот!")


async def main():
    logging.basicConfig(level=logging.INFO)
    print("✅ Запускаем тестовый бот...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
