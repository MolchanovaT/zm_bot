# Используем базовый образ Python
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /bot

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запуск скрипта инициализации БД
CMD ["sh", "-c", "python -c 'import asyncio; from db import init_db; asyncio.run(init_db())' && python main.py"]
