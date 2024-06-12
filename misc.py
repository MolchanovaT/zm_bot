import asyncpg
from aiogram import Bot, Dispatcher
import config
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# db_pool = asyncpg.create_pool(config.DATABASE_URL)
