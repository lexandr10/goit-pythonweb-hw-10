FROM python:3.13-slim

# Установка Poetry
RUN pip install --no-cache-dir poetry

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем только pyproject и lock-файл
COPY goit-pythonweb-hw-10/pyproject.toml ./

# Установка зависимостей через poetry
RUN poetry config virtualenvs.create false \
  && poetry install --no-root --no-interaction --no-ansi

# Копируем весь проект
COPY goit-pythonweb-hw-10/ .

# Запуск uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]