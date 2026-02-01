"""
KunUz Parser — FastAPI API
"""

import logging
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime

from parser import KunUzParser
from config import CATEGORIES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/categories")
def categories():
    return {
        key: {"url": val["url"], "category_name": val["category_name"]}
        for key, val in CATEGORIES.items()
    }


@app.get("/parse")
def parse(
    category: str = Query(default="everything"),
    limit: int = Query(default=20, ge=1, le=100),
    from_date: Optional[str] = Query(default=None),
    to_date: Optional[str] = Query(default=None),
):
    valid_categories = list(CATEGORIES.keys()) + ["everything"]
    if category not in valid_categories:
        raise HTTPException(400, detail=f"Неизвестная категория '{category}'. Доступные: {valid_categories}")

    for label, val in [("from_date", from_date), ("to_date", to_date)]:
        if val:
            try:
                datetime.strptime(val, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(400, detail=f"Неверный формат '{label}': {val}. Ожидается YYYY-MM-DD")

    logger.info(f"[PARSE] START category={category} limit={limit}")
    try:
        parser = KunUzParser()
        logger.info("[PARSE] KunUzParser created, calling parse()...")
        results = parser.parse(
            category=category,
            limit=limit,
            from_date=from_date,
            to_date=to_date,
            save=False,
            verbose=True,
        )
        logger.info(f"[PARSE] DONE, got {len(results)} results")
    except Exception as e:
        logger.error(f"[PARSE] ERROR: {e}", exc_info=True)
        raise HTTPException(500, detail=str(e))

    return {"count": len(results), "category": category, "limit": limit, "data": results}
