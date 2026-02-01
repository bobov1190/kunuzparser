# ─── базовый образ ────────────────────────────────────────────────────────────
FROM python:3.12-slim

# ─── зависимости системы для Playwright (Chromium) ──────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ─── рабочая директория ─────────────────────────────────────────────────────
WORKDIR /app

# ─── копируем requirements и ставим Python-зависимости ──────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── устанавливаем Playwright browsers (chromium) ───────────────────────────
RUN playwright install chromium

# ─── копируем весь код ──────────────────────────────────────────────────────
COPY . .

# ─── порт — Render автоматически передаёт PORT через окружение ───────────────
ENV PORT=0100

EXPOSE $PORT

# ─── запуск через uvicorn ────────────────────────────────────────────────────
CMD ["sh", "-c", "uvicorn kunuzparser.main:app --host 0.0.0.0 --port $PORT"]
