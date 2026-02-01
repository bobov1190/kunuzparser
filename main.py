"""
KunUz Parser — FastAPI API
Endpoints:
  GET  /categories          -> список категорий
  GET  /parse               -> парсинг (query params)
  GET  /health              -> healthcheck для Render
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import asyncio
from concurrent.futures import ProcessPoolExecutor

from parser import KunUzParser
from config import CATEGORIES

app = FastAPI(
    title="KunUz Parser API",
    description="Парсер новостей kun.uz",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Отдельный executor — Playwright запускается в своём процессе,
# иначе sync_playwright конфликтует с asyncio event loop FastAPI
executor = ProcessPoolExecutor(max_workers=2)


# ─── запускаем парсер в отдельном процессе ───────────────────────────────────
def _run_parser(category: str, limit: int, from_date, to_date):
    parser = KunUzParser()
    return parser.parse(
        category=category,
        limit=limit,
        from_date=from_date,
        to_date=to_date,
        save=False,
        verbose=True,
    )


# ─── healthcheck (Render ping) ───────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}


# ─── список категорий ────────────────────────────────────────────────────────
@app.get("/categories")
async def categories():
    return {
        key: {
            "url": val["url"],
            "category_name": val["category_name"],
        }
        for key, val in CATEGORIES.items()
    }


# ─── парсинг ─────────────────────────────────────────────────────────────────
@app.get("/parse")
async def parse(
    category: str = Query(default="everything", description="Категория или 'everything'"),
    limit: int = Query(default=20, ge=1, le=100, description="Кол-во новостей (макс 100)"),
    from_date: Optional[str] = Query(default=None, description="Дата начала YYYY-MM-DD"),
    to_date: Optional[str] = Query(default=None, description="Дата окончания YYYY-MM-DD"),
):
    # валидация категории
    valid_categories = list(CATEGORIES.keys()) + ["everything"]
    if category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Неизвестная категория '{category}'. Доступные: {valid_categories}"
        )

    # валидация дат
    for label, val in [("from_date", from_date), ("to_date", to_date)]:
        if val:
            try:
                datetime.strptime(val, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Неверный формат '{label}': {val}. Ожидается YYYY-MM-DD"
                )

    # запускаем парсер в отдельном процессе (не блокируем event loop)
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        executor,
        _run_parser,
        category,
        limit,
        from_date,
        to_date,
    )

    return {
        "count": len(results),
        "category": category,
        "limit": limit,
        "data": results,
    }
