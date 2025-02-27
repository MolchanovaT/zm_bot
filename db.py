import aiosqlite

DATABASE_PATH = "database.sqlite"

async def init_db():
    """Создание базы данных и таблиц"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS Dilers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                inn TEXT UNIQUE NOT NULL,
                allowed BOOLEAN DEFAULT TRUE
            )"""
        )
        await db.execute(
            """CREATE TABLE IF NOT EXISTS LPU (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                inn TEXT UNIQUE NOT NULL,
                allowed BOOLEAN DEFAULT TRUE
            )"""
        )
        await db.commit()
