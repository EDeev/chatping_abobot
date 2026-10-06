FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# словарь английского для распознавания текста в неправильной раскладке
RUN apt-get update \
    && apt-get install -y --no-install-recommends libenchant-2-2 hunspell-en-us \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY code/ code/
COPY data/ data/
RUN useradd --create-home --uid 1000 app && mkdir -p db && chown -R app:app /app
USER app
VOLUME ["/app/db"]

# пути к базам и картинкам в коде — относительно папки code/ (../db, ../data)
WORKDIR /app/code
CMD ["python", "bot.py"]
