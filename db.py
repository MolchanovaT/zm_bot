import aiosqlite
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "database.sqlite")


async def init_db():
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
        await db.execute(
            """CREATE TABLE IF NOT EXISTS PendingReview (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                inn TEXT NOT NULL UNIQUE,
                date TEXT NOT NULL,
                approved BOOLEAN DEFAULT 0,
                denied BOOLEAN DEFAULT 0
            )"""
        )
        await db.commit()


async def check_inn_in_db(inn: str, table: str) -> str:
    """Возвращает статус ИНН: approved, denied, pending, not_found"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(f"SELECT allowed FROM {table} WHERE inn = ?", (inn,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return "approved" if row[0] else "denied"

        async with db.execute("SELECT date, approved, denied FROM PendingReview WHERE inn = ?", (inn,)) as cursor:
            row = await cursor.fetchone()
            if row:
                date, approved, denied = row
                if denied:
                    return f"denied_date:{date}"
                return f"pending:{date}"

        return "not_found"
