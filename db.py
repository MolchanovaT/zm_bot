import aiosqlite

DATABASE_PATH = "data/database.sqlite"


async def init_db():
    """Создание базы данных и таблиц (если их нет)"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS Dilers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                inn TEXT NOT NULL UNIQUE,  
                allowed BOOLEAN DEFAULT TRUE
            )"""
        )
        await db.execute(
            """CREATE TABLE IF NOT EXISTS LPU (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                inn TEXT NOT NULL UNIQUE, 
                allowed BOOLEAN DEFAULT TRUE
            )"""
        )
        await db.commit()



async def check_inn_in_db(inn: str, table: str) -> bool:
    """Проверяет, есть ли ИНН в указанной таблице"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(f"SELECT name, allowed FROM {table} WHERE inn = ?", (str(inn),)) as cursor:
            row = await cursor.fetchone()
            return row is not None and row[1] == 1

