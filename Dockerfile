# Используем Python 3.11
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порты для Flask
EXPOSE 5000

# Указываем запуск через docker-compose
CMD ["sh", "-c", "python admin.py & python main.py"]
