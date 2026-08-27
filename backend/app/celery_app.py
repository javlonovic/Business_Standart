"""
Celery application configuration
Веб-платформа Business Standart

Tashkent timezone: UTC+5 (Asia/Tashkent)
Daily currency rate update at 09:00 Tashkent time = 04:00 UTC
"""
import os
from celery import Celery
from celery.schedules import crontab

# Получаем URL Redis из переменной окружения
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Создаём экземпляр Celery
celery_app = Celery(
    "business_standart",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks"],  # Модуль с задачами
)

# Настройки Celery
celery_app.conf.update(
    # Сериализация
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Временная зона
    timezone="Asia/Tashkent",
    enable_utc=True,
    
    # Результаты
    result_expires=3600,  # 1 час
    
    # Повторные попытки при подключении к broker
    broker_connection_retry_on_startup=True,
    
    # Настройки воркера
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    
    # Расписание Celery Beat
    beat_schedule={
        "update-currency-rates-daily": {
            "task": "app.tasks.update_currency_rates",
            # Каждый день в 09:00 по Ташкентскому времени (UTC+5)
            # UTC: 04:00
            "schedule": crontab(hour=4, minute=0),
        },
    },
)
