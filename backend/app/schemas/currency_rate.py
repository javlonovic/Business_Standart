"""
Pydantic схемы для модуля курсов валют
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class CurrencyRateResponse(BaseModel):
    """Схема ответа с курсом одной валюты"""
    id: int
    currency_code: str = Field(..., description="ISO код валюты (USD, EUR, RUB, GBP, CNY)")
    rate: Decimal = Field(..., description="Курс в сумах за единицу иностранной валюты")
    change: Decimal = Field(..., description="Изменение курса относительно предыдущего дня")
    date: datetime = Field(..., description="Дата курса")

    model_config = {"from_attributes": True}


class CurrencyRatesWidgetResponse(BaseModel):
    """Схема ответа виджета курсов (топ-5 валют)"""
    rates: list[CurrencyRateResponse]
    cached: bool = Field(default=False, description="Данные из кеша Redis")
    updated_at: Optional[datetime] = Field(None, description="Дата последнего обновления")


class CurrencyRatesHistoryResponse(BaseModel):
    """Схема ответа с историей курсов валюты"""
    currency_code: str
    items: list[CurrencyRateResponse]
    total: int
    days: int
    offset: int
    limit: int
