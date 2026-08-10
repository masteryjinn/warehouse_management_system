FROM python:3.13-slim

# Встановлюємо default-mysql-client (щоб була доступна команда mysql та mysqldump)
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=Europe/Kyiv

WORKDIR /app

# Копіюємо файл залежностей та встановлюємо їх
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь проєкт
COPY . .

# Створюємо директорії під логи та зашифровані бекапи
RUN mkdir -p backups logs

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]