# Используем базовый образ Python
FROM python:3.12.2


# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . /app/

# Устанавливаем переменные окружения для Django
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# # Команда для запуска сервера разработки (или WSGI-сервера, например gunicorn)
# CMD ["python", "manage.py", "migrate"]
# CMD ["python", "manage.py", "runserver"]
