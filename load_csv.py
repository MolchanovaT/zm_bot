import aiosqlite
import pandas as pd

DATABASE_PATH = "database.sqlite"

async def load_data_from_csv(file_path: str, table: str):
    """Загружает данные из CSV в указанную таблицу"""
    df = pd.read_csv(file_path)  # Загружаем CSV

    async with aiosqlite.connect(DATABASE_PATH) as db:
        for _, row in df.iterrows():
            await db.execute(
                f"INSERT OR IGNORE INTO {table} (name, inn, allowed) VALUES (?, ?, TRUE)",
                (row["name"], row["inn"])
            )
        await db.commit()

# Пример вызова:
# import asyncio
# asyncio.run(load_data_from_csv("data.csv", "Dilers"))
