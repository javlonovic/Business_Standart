"""
Order Management Service - управление заявками
Требования: 2.1, 2.2, 2.3, 2.5, 2.7, 15.1-15.7, 18.1
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.order import Order, OrderStatus, OrderStatusHistory
from app.models.user import User
from app.models.service import Service


class OrderManagement:
    """Сервис управления заявками"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_order(
        self,
        user_id: int,
        service_id: int,
        params: Dict[str, Any],
        estimate_total: float
    ) -> Order:
        """
        Создать новую заявку
        
        Требование 2.1: КОГДА клиент подтверждает расчёт, ТОГДА Система ДОЛЖНА 
        создать заявку со статусом awaiting_payment
        
        Требование 2.2: КОГДА заявка создаётся, ТОГДА Система ДОЛЖНА сохранить 
        параметры расчёта и итоговую стоимость
        """
        # Проверить существование услуги
        service_query = select(Service).where(Service.id == service_id)
        service_result = await self.db.execute(service_query)
        service = service_result.scalar_one_or_none()
        
        if not service:
            raise ValueError(f"Услуга с ID {service_id} не найдена")
        
        # Создать заявку
        order = Order(
            user_id=user_id,
            service_id=service_id,
            params=params,
            estimate_total=estimate_total,
            status=OrderStatus.AWAITING_PAYMENT
        )
        
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        
        # Создать запись в истории статусов
        await self._record_status_change(
            order_id=order.id,
            old_status="",
            new_status=OrderStatus.AWAITING_PAYMENT.value,
            actor_id=user_id,
            comment="Заявка создана"
        )
        
        return order
    
    async def update_order_status(
        self,
        order_id: int,
        new_status: OrderStatus,
        actor_id: int,
        comment: Optional[str] = None
    ) -> Order:
        """
        Обновить статус заявки с валидацией переходов
        
        Требование 2.3: КОГДА статус заявки изменяется, ТОГДА Система ДОЛЖНА 
        валидировать допустимость перехода согласно графу состояний
        
        Требование 2.5: КОГДА статус заявки изменяется, ТОГДА Система ДОЛЖНА 
        записать изменение в OrderStatusHistory
        """
        # Получить заявку
        query = select(Order).where(Order.id == order_id)
        result = await self.db.execute(query)
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Заявка с ID {order_id} не найдена")
        
        old_status = order.status
        
        # Валидировать переход статуса
        if not self.validate_status_transition(old_status, new_status):
            raise ValueError(
                f"Недопустимый переход статуса: {old_status.value} → {new_status.value}"
            )
        
        # Обновить статус
        order.status = new_status
        
        # Если статус paid, установить deadline
        if new_status == OrderStatus.PAID:
            order.deadline = self.calculate_deadline(datetime.utcnow())
        
        await self.db.commit()
        await self.db.refresh(order)
        
        # Записать в историю
        await self._record_status_change(
            order_id=order_id,
            old_status=old_status.value,
            new_status=new_status.value,
            actor_id=actor_id,
            comment=comment
        )
        
        return order
    
    def validate_status_transition(
        self,
        old_status: OrderStatus,
        new_status: OrderStatus
    ) -> bool:
        """
        Валидировать допустимость перехода между статусами
        
        Требование 15.1-15.7: Граф допустимых переходов статусов
        
        Граф переходов:
        draft → awaiting_payment, cancelled
        awaiting_payment → paid, cancelled
        paid → in_progress, cancelled
        in_progress → ready, cancelled
        ready → delivered
        delivered → (финальный статус)
        cancelled → (финальный статус)
        """
        # Граф допустимых переходов
        transitions = {
            OrderStatus.DRAFT: [OrderStatus.AWAITING_PAYMENT, OrderStatus.CANCELLED],
            OrderStatus.AWAITING_PAYMENT: [OrderStatus.PAID, OrderStatus.CANCELLED],
            OrderStatus.PAID: [OrderStatus.IN_PROGRESS, OrderStatus.CANCELLED],
            OrderStatus.IN_PROGRESS: [OrderStatus.READY, OrderStatus.CANCELLED],
            OrderStatus.READY: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [],  # Финальный статус
            OrderStatus.CANCELLED: []   # Финальный статус
        }
        
        allowed_transitions = transitions.get(old_status, [])
        return new_status in allowed_transitions
    
    def calculate_deadline(self, start_date: datetime) -> datetime:
        """
        Рассчитать deadline для заявки (2-5 рабочих дней)
        
        Требование 2.7: КОГДА заявка оплачена, ТОГДА Система ДОЛЖНА 
        автоматически установить deadline (2-5 рабочих дней)
        
        Требование 15.8: Срок выполнения должен исключать выходные
        """
        # Базовый срок: 3 рабочих дня (средний)
        business_days = 3
        days_added = 0
        current_date = start_date
        
        while days_added < business_days:
            current_date += timedelta(days=1)
            # Пропустить выходные (суббота=5, воскресенье=6)
            if current_date.weekday() < 5:
                days_added += 1
        
        return current_date
    
    async def _record_status_change(
        self,
        order_id: int,
        old_status: str,
        new_status: str,
        actor_id: int,
        comment: Optional[str] = None
    ) -> None:
        """Записать изменение статуса в историю"""
        history = OrderStatusHistory(
            order_id=order_id,
            old_status=old_status,
            new_status=new_status,
            actor_id=actor_id,
            comment=comment
        )
        
        self.db.add(history)
        await self.db.commit()
