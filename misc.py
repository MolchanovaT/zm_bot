import aiosqlite
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config

BOT_TOKEN = config.BOT_TOKEN
DATABASE_PATH = "database.sqlite"

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS Dilers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                inn TEXT UNIQUE NOT NULL,
                allowed BOOLEAN DEFAULT FALSE
            )"""
        )
        await db.commit()

