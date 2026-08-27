"""
API endpoints для модуля курсов валют

GET /api/currency-rates/widget  — виджет с топ-5 последними курсами (кеш Redis, TTL 1ч)
GET /api/currency-rates/history — история курсов для конкретной валюты
"""
import json
import logging
from datetime import datetime
from typing import Optional, Annotated

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.currency_rates import CurrencyRatesService, TARGET_CURRENCIES
from app.schemas.currency_rate import (
    CurrencyRatesWidgetResponse,
    CurrencyRateResponse,
    CurrencyRatesHistoryResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/currency-rates", tags=["currency-rates"])

# Ключ кеша виджета
WIDGET_CACHE_KEY = "currency_rates:widget"
WIDGET_CACHE_TTL = 3600  # 1 час


async def _get_redis() -> Optional[aioredis.Redis]:
    """Получить асинхронный Redis-клиент (возвращает None при недоступности)."""
    import os
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    try:
        client = aioredis.from_url(redis_url, decode_responses=True)
        await client.ping()
        return client
    except Exception as e:
        logger.warning("Redis недоступен: %s. Работаем без кеша.", e)
        return None


@router.get("/widget", response_model=CurrencyRatesWidgetResponse)
async def get_currency_rates_widget(
    db: AsyncSession = Depends(get_db),
) -> CurrencyRatesWidgetResponse:
    """
    Получить актуальные курсы валют для виджета на главной странице.

    Возвращает последние курсы для 5 валют: USD, EUR, RUB, GBP, CNY.
    Данные кешируются в Redis с TTL 1 час.

    При недоступности Redis данные берутся напрямую из БД (fallback).
    """
    redis_client = await _get_redis()

    # --- Попытка получить из кеша ---
    if redis_client:
        try:
            cached_raw = await redis_client.get(WIDGET_CACHE_KEY)
            if cached_raw:
                cached_data = json.loads(cached_raw)
                logger.debug("Виджет курсов: отдаём из кеша Redis")
                return CurrencyRatesWidgetResponse(
                    rates=[CurrencyRateResponse(**r) for r in cached_data["rates"]],
                    cached=True,
                    updated_at=datetime.fromisoformat(cached_data["updated_at"])
                    if cached_data.get("updated_at")
                    else None,
                )
        except Exception as e:
            logger.warning("Ошибка чтения из кеша Redis: %s", e)

    # --- Fallback: берём из БД ---
    service = CurrencyRatesService(db)
    rates = await service.get_widget_rates()

    if not rates:
        # Нет данных вообще — возвращаем пустой ответ, не 404
        logger.warning("В БД нет курсов валют — виджет пустой")
        return CurrencyRatesWidgetResponse(rates=[], cached=False, updated_at=None)

    rate_responses = [CurrencyRateResponse.model_validate(r) for r in rates]
    updated_at = max(r.date for r in rate_responses)

    # --- Записываем в кеш ---
    if redis_client:
        try:
            cache_payload = {
                "rates": [r.model_dump(mode="json") for r in rate_responses],
                "updated_at": updated_at.isoformat(),
            }
            await redis_client.setex(
                WIDGET_CACHE_KEY,
                WIDGET_CACHE_TTL,
                json.dumps(cache_payload, default=str),
            )
            logger.debug("Виджет курсов: данные записаны в кеш (TTL %d сек)", WIDGET_CACHE_TTL)
        except Exception as e:
            logger.warning("Ошибка записи в кеш Redis: %s", e)
        finally:
            await redis_client.aclose()

    return CurrencyRatesWidgetResponse(
        rates=rate_responses,
        cached=False,
        updated_at=updated_at,
    )


@router.get("/history", response_model=CurrencyRatesHistoryResponse)
async def get_currency_rates_history(
    currency: Annotated[
        str,
        Query(description="ISO код валюты (USD, EUR, RUB, GBP, CNY)"),
    ] = "USD",
    days: Annotated[
        int,
        Query(ge=1, le=365, description="Количество дней истории (1–365)"),
    ] = 30,
    offset: Annotated[
        int,
        Query(ge=0, description="Смещение для пагинации"),
    ] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=200, description="Максимум записей (1–200)"),
    ] = 100,
    db: AsyncSession = Depends(get_db),
) -> CurrencyRatesHistoryResponse:
    """
    Получить историю курсов для выбранной валюты.

    - **currency**: код валюты, один из: USD, EUR, RUB, GBP, CNY
    - **days**: глубина истории в днях (по умолчанию 30, максимум 365)
    - **offset**: смещение для пагинации
    - **limit**: максимум записей в ответе
    """
    currency_upper = currency.upper()

    if currency_upper not in TARGET_CURRENCIES:
        raise HTTPException(
            status_code=422,
            detail=f"Неверный код валюты '{currency}'. "
                   f"Доступные: {', '.join(TARGET_CURRENCIES)}",
        )

    service = CurrencyRatesService(db)
    records = await service.get_rates_history(
        currency_code=currency_upper,
        days=days,
        offset=offset,
        limit=limit,
    )

    return CurrencyRatesHistoryResponse(
        currency_code=currency_upper,
        items=[CurrencyRateResponse.model_validate(r) for r in records],
        total=len(records),
        days=days,
        offset=offset,
        limit=limit,
    )
