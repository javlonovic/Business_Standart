"""
API endpoints для калькулятора стоимости услуг

POST /api/calculator/estimate — расчёт стоимости услуги
GET /api/calculator/params/{service_id} — метаданные параметров для динамической формы
"""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.pricing_engine import PricingEngine
from app.schemas.calculator import (
    EstimateRequest,
    EstimateResult,
    ServiceParamsResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/calculator", tags=["calculator"])

# Rate limiting: 20 запросов в минуту (будет реализовано через middleware)
# Пока просто логируем


@router.post("/estimate", response_model=EstimateResult)
async def calculate_estimate(
    request_data: EstimateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> EstimateResult:
    """
    Рассчитать предварительную стоимость услуги.

    Принимает ID услуги и параметры объекта, возвращает:
    - Итоговую стоимость (total)
    - Детализацию расчёта (breakdown)
    - Флаг is_preliminary=True
    - Валюту (UZS)

    Rate limiting: 20 запросов в минуту.
    """
    logger.info(
        "Запрос расчёта для service_id=%d от IP=%s",
        request_data.service_id,
        request.client.host if request.client else "unknown",
    )

    try:
        engine = PricingEngine(db)
        result = await engine.calculate_estimate(
            service_id=request_data.service_id,
            params=request_data.params,
        )

        logger.info(
            "Расчёт успешен: service_id=%d, total=%s сум",
            request_data.service_id,
            result.total,
        )

        return result

    except ValueError as e:
        # Ошибки валидации параметров или отсутствия правил
        logger.warning(
            "Ошибка валидации для service_id=%d: %s",
            request_data.service_id,
            str(e),
        )
        raise HTTPException(
            status_code=422,
            detail=str(e),
        )

    except Exception as e:
        logger.error(
            "Внутренняя ошибка при расчёте service_id=%d: %s",
            request_data.service_id,
            str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера при расчёте стоимости. Попробуйте позже.",
        )


@router.get("/params/{service_id}", response_model=ServiceParamsResponse)
async def get_service_params(
    service_id: int,
    db: AsyncSession = Depends(get_db),
) -> ServiceParamsResponse:
    """
    Получить метаданные параметров для динамической формы калькулятора.

    Возвращает список параметров с:
    - Ключом параметра
    - Подсказкой на русском языке
    - Типом поля (number, boolean, select)
    - Обязательностью
    - Ограничениями (min, max)
    - Опциями для select
    """
    logger.info("Запрос параметров для service_id=%d", service_id)

    try:
        engine = PricingEngine(db)
        result = await engine.get_service_params(service_id)

        logger.info(
            "Параметры для service_id=%d: %d полей",
            service_id,
            len(result.params),
        )

        return result

    except ValueError as e:
        logger.warning("Услуга не найдена: service_id=%d", service_id)
        raise HTTPException(
            status_code=404,
            detail=f"Услуга с ID {service_id} не найдена",
        )

    except Exception as e:
        logger.error(
            "Ошибка получения параметров service_id=%d: %s",
            service_id,
            str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера. Попробуйте позже.",
        )
