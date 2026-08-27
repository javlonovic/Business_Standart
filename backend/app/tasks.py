"""
Celery задачи для Business Standart

update_currency_rates — ежедневное обновление курсов валют из ЦБУ.
  - Запускается через Celery Beat в 09:00 по Ташкенту (04:00 UTC)
  - Retry: до 3 раз с интервалом 1 час (3600 сек)
  - Идемпотентна: повторный запуск не создаёт дублей
  - Инвалидирует кеш виджета в Redis после успешного обновления
"""
import asyncio
import logging
import json
from datetime import datetime

import redis as redis_sync

from app.celery_app import celery_app

logger = logging.getLogger(__name__)

# Ключ кеша виджета курсов валют в Redis
WIDGET_CACHE_KEY = "currency_rates:widget"


def _get_redis_client() -> redis_sync.Redis:
    """Синхронный Redis-клиент для использования внутри Celery задачи."""
    import os
    redis_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    return redis_sync.from_url(redis_url, decode_responses=True)


async def _run_update() -> dict:
    """
    Асинхронная логика обновления курсов.
    Запускается внутри синхронной Celery задачи через asyncio.run().
    """
    # Импортируем здесь, чтобы избежать circular import при старте Celery
    from app.db.database import AsyncSessionLocal
    from app.services.currency_rates import CurrencyRatesService

    async with AsyncSessionLocal() as db:
        service = CurrencyRatesService(db)
        
        # Получаем курсы из ЦБУ
        rates_data = await service.fetch_latest_rates()
        
        if not rates_data:
            raise ValueError("API ЦБУ вернул пустой список курсов")
        
        # Сохраняем в БД
        saved = await service.save_rates(rates_data)
        
        return {
            "updated_count": len(saved),
            "currencies": [r.currency_code for r in saved],
            "date": datetime.now().isoformat(),
        }


@celery_app.task(
    bind=True,
    name="app.tasks.update_currency_rates",
    max_retries=3,
    default_retry_delay=3600,  # 1 час между попытками
    autoretry_for=(Exception,),
    retry_backoff=False,
    acks_late=True,
)
def update_currency_rates(self) -> dict:
    """
    Celery задача: обновление курсов валют из API ЦБУ.

    Запускается ежедневно в 09:00 Ташкент (04:00 UTC) через Celery Beat.
    Идемпотентна — повторный запуск не создаёт дублей благодаря upsert.

    Returns:
        dict с результатом: количество обновлённых записей, список кодов валют, дата.

    Raises:
        Автоматически повторяет попытку при любом исключении.
        После 3 провалов задача помечается как FAILED.
    """
    logger.info(
        "[update_currency_rates] Старт. Попытка %d/%d",
        self.request.retries + 1,
        self.max_retries + 1,
    )

    try:
        # Запускаем асинхронную логику в синхронном контексте Celery
        result = asyncio.run(_run_update())

        # Инвалидируем кеш виджета в Redis
        try:
            redis_client = _get_redis_client()
            redis_client.delete(WIDGET_CACHE_KEY)
            logger.info("[update_currency_rates] Кеш виджета '%s' удалён", WIDGET_CACHE_KEY)
        except Exception as redis_err:
            # Не критично — следующий запрос к виджету просто промахнётся в кеш
            logger.warning("[update_currency_rates] Не удалось удалить кеш: %s", redis_err)

        logger.info(
            "[update_currency_rates] Успешно обновлено %d курсов: %s",
            result["updated_count"],
            result["currencies"],
        )
        return result

    except Exception as exc:
        logger.error(
            "[update_currency_rates] Ошибка (попытка %d): %s",
            self.request.retries + 1,
            exc,
            exc_info=True,
        )

        if self.request.retries >= self.max_retries:
            # Все попытки исчерпаны — уведомляем (логируем критически)
            logger.critical(
                "[update_currency_rates] Все %d попытки исчерпаны! "
                "Курсы валют НЕ обновлены. Требуется вмешательство администратора.",
                self.max_retries + 1,
            )
            # В будущем здесь будет вызов NotificationService для уведомления админа
            raise

        # Повторная попытка через 1 час
        raise self.retry(exc=exc)
