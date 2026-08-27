"""
Payments API (Stub Implementation for Phase 5)

Endpoints for creating payments and handling webhooks.
This is a stub implementation for testing without real payment providers.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from decimal import Decimal
import logging

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.payment import Payment, PaymentProvider, PaymentStatus
from app.services.payment.payment_integration import PaymentIntegration
from app.core.exceptions import ValidationException, NotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


# Schemas

class CreatePaymentRequest(BaseModel):
    """Request to create a payment"""
    order_id: int = Field(..., description="ID заявки")
    provider: str = Field(..., description="Провайдер: payme или click")
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_id": 1,
                "provider": "payme"
            }
        }


class PaymentResponse(BaseModel):
    """Payment response"""
    payment_id: int
    external_id: str
    payment_url: str
    provider: str
    amount: float
    status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "payment_id": 1,
                "external_id": "payme_abc123",
                "payment_url": "https://checkout.payme.uz/...",
                "provider": "payme",
                "amount": 1500000,
                "status": "pending"
            }
        }


class WebhookResponse(BaseModel):
    """Webhook response"""
    success: bool
    message: str


# Endpoints

@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    request: CreatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Создать платёж для заявки
    
    **STUB IMPLEMENTATION**: Возвращает тестовый payment URL
    
    - Создаёт запись Payment в БД
    - Возвращает URL для оплаты
    - В production: интеграция с Payme/Click API
    
    **Требования:**
    - Пользователь должен быть владельцем заявки
    - Заявка должна быть в статусе awaiting_payment
    - Провайдер должен быть 'payme' или 'click'
    """
    # Get order and verify ownership
    from sqlalchemy import select
    from app.models.order import Order
    
    result = await db.execute(
        select(Order).where(Order.id == request.order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    
    # Create payment
    try:
        payment_service = PaymentIntegration(db)
        payment_data = await payment_service.create_payment(
            order_id=request.order_id,
            provider=request.provider,
            amount=Decimal(str(order.estimate_total))
        )
        
        return PaymentResponse(**payment_data)
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Payment creation error: {e}")
        raise HTTPException(status_code=500, detail="Ошибка создания платежа")


@router.post("/webhook/{provider}", response_model=WebhookResponse)
async def handle_webhook(
    provider: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Обработка webhook от платёжной системы
    
    **STUB IMPLEMENTATION**: Принимает любой payload без проверки подписи
    
    - Обновляет статус платежа
    - Обновляет статус заявки (paid при успехе)
    - Идемпотентность: повторные webhook не дублируют изменения
    
    **В production:**
    - Проверка webhook signature
    - Валидация IP источника
    - Логирование всех webhook для аудита
    """
    # Get signature from headers
    signature = request.headers.get("X-Signature") or request.headers.get("Authorization")
    
    # Parse JSON payload
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Webhook: invalid JSON - {e}")
        raise HTTPException(status_code=400, detail="Неверный формат данных")
    
    # Handle webhook
    try:
        payment_service = PaymentIntegration(db)
        success, message = await payment_service.handle_webhook(
            provider=provider,
            payload=payload,
            signature=signature
        )
        
        return WebhookResponse(success=success, message=message)
        
    except ValidationException as e:
        logger.warning(f"Webhook validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Ошибка обработки webhook")


@router.get("/order/{order_id}", response_model=list[Dict[str, Any]])
async def get_order_payments(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить историю платежей для заявки
    
    - Список всех попыток оплаты
    - С информацией о провайдере, статусе, дате
    """
    # Verify order ownership
    from sqlalchemy import select
    from app.models.order import Order
    
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    
    # Get payments
    payment_service = PaymentIntegration(db)
    payments = await payment_service.list_payments(order_id=order_id)
    
    return [
        {
            "payment_id": p.id,
            "provider": p.provider.value,
            "amount": float(p.amount),
            "status": p.status.value,
            "external_id": p.external_id,
            "created_at": p.created_at.isoformat(),
            "completed_at": p.completed_at.isoformat() if p.completed_at else None
        }
        for p in payments
    ]


@router.get("/stub/simulate-success/{external_id}")
async def simulate_payment_success(
    external_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    **TESTING ONLY**: Симулировать успешный платёж
    
    Отправляет webhook с успешным статусом для тестирования
    """
    payment_service = PaymentIntegration(db)
    
    payload = {
        "external_id": external_id,
        "status": "success",
        "timestamp": "2026-08-27T12:00:00Z"
    }
    
    success, message = await payment_service.handle_webhook(
        provider="stub",
        payload=payload,
        signature=None
    )
    
    return {"success": success, "message": message}


@router.get("/stub/simulate-failure/{external_id}")
async def simulate_payment_failure(
    external_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    **TESTING ONLY**: Симулировать провал платежа
    
    Отправляет webhook с failed статусом для тестирования
    """
    payment_service = PaymentIntegration(db)
    
    payload = {
        "external_id": external_id,
        "status": "failed",
        "error": "Card declined",
        "timestamp": "2026-08-27T12:00:00Z"
    }
    
    success, message = await payment_service.handle_webhook(
        provider="stub",
        payload=payload,
        signature=None
    )
    
    return {"success": success, "message": message}
