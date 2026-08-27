"""
Orders API - управление заявками клиентов
Требования: 2.1, 2.2, 2.4, 5.3, 11.2, 12.8
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.db.database import get_db
from app.models.order import Order, OrderStatus, OrderStatusHistory
from app.models.user import User
from app.core.security import get_current_user
from app.services.order_management import OrderManagement


router = APIRouter(prefix="/api/orders", tags=["orders"])


# Pydantic schemas
class CreateOrderRequest(BaseModel):
    """Запрос на создание заявки"""
    service_id: int = Field(..., description="ID услуги")
    params: Dict[str, Any] = Field(..., description="Параметры расчёта")
    estimate_total: float = Field(..., gt=0, description="Итоговая стоимость")


class OrderResponse(BaseModel):
    """Ответ с данными заявки"""
    id: int
    user_id: int
    service_id: int
    service_name: Optional[str] = None
    params: Dict[str, Any]
    estimate_total: float
    status: str
    created_at: datetime
    deadline: Optional[datetime] = None
    document_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class OrderDetailResponse(OrderResponse):
    """Детальная информация о заявке с историей статусов"""
    status_history: List[Dict[str, Any]] = []


class OrderListResponse(BaseModel):
    """Список заявок с пагинацией"""
    orders: List[OrderResponse]
    total: int
    offset: int
    limit: int


@router.post(
    "/create",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать заявку"
)
async def create_order(
    data: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Создать новую заявку
    
    **Требование 2.1**: КОГДА клиент подтверждает расчёт, ТОГДА Система ДОЛЖНА 
    создать заявку со статусом awaiting_payment
    
    **Требование 2.2**: КОГДА заявка создаётся, ТОГДА Система ДОЛЖНА сохранить 
    параметры расчёта и итоговую стоимость
    
    **Требование 12.8**: Rate limiting: 5 req/min
    
    Параметры:
    - **service_id**: ID услуги
    - **params**: Параметры расчёта (JSONB)
    - **estimate_total**: Итоговая стоимость
    
    Возвращает созданную заявку с order_id и статусом awaiting_payment
    """
    order_mgmt = OrderManagement(db)
    
    try:
        order = await order_mgmt.create_order(
            user_id=current_user.id,
            service_id=data.service_id,
            params=data.params,
            estimate_total=data.estimate_total
        )
        
        # Загрузить связанные данные
        await db.refresh(order, ["service"])
        
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            service_id=order.service_id,
            service_name=order.service.name_ru if order.service else None,
            params=order.params,
            estimate_total=float(order.estimate_total),
            status=order.status.value,
            created_at=order.created_at,
            deadline=order.deadline,
            document_url=order.document_url
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/my",
    response_model=OrderListResponse,
    summary="Список моих заявок"
)
async def get_my_orders(
    status_filter: Optional[str] = Query(None, description="Фильтр по статусу"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    limit: int = Query(20, ge=1, le=100, description="Количество записей"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список заявок текущего пользователя
    
    **Требование 2.4**: КОГДА клиент открывает Личный кабинет, ТОГДА Система 
    ДОЛЖНА показать список его заявок
    
    **Требование 11.2**: Запросы orders должны выполняться <1s для 1000 заявок
    
    Параметры:
    - **status_filter**: Фильтр по статусу (опционально)
    - **offset**: Смещение для пагинации
    - **limit**: Количество записей (макс 100)
    
    Возвращает список заявок с сортировкой по created_at DESC
    """
    # Построить запрос
    query = select(Order).where(Order.user_id == current_user.id)
    
    # Применить фильтр статуса
    if status_filter:
        try:
            status_enum = OrderStatus(status_filter)
            query = query.where(Order.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Недопустимый статус: {status_filter}"
            )
    
    # Подсчитать total
    from sqlalchemy import func
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # Применить сортировку и пагинацию
    query = query.order_by(Order.created_at.desc())
    query = query.offset(offset).limit(limit)
    query = query.options(selectinload(Order.service))
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    # Преобразовать в response
    order_responses = [
        OrderResponse(
            id=order.id,
            user_id=order.user_id,
            service_id=order.service_id,
            service_name=order.service.name_ru if order.service else None,
            params=order.params,
            estimate_total=float(order.estimate_total),
            status=order.status.value,
            created_at=order.created_at,
            deadline=order.deadline,
            document_url=order.document_url
        )
        for order in orders
    ]
    
    return OrderListResponse(
        orders=order_responses,
        total=total,
        offset=offset,
        limit=limit
    )


@router.get(
    "/{order_id}",
    response_model=OrderDetailResponse,
    summary="Детали заявки"
)
async def get_order_details(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить детальную информацию о заявке
    
    **Требование 2.4**: Доступ к деталям заявки
    **Требование 5.3**: Проверка владельца заявки (403)
    
    Параметры:
    - **order_id**: ID заявки
    
    Возвращает детали заявки с историей статусов
    """
    # Получить заявку
    query = select(Order).where(Order.id == order_id)
    query = query.options(
        selectinload(Order.service),
        selectinload(Order.status_history)
    )
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    
    # Проверить владельца (403)
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён"
        )
    
    # Получить историю статусов
    history_query = select(OrderStatusHistory).where(
        OrderStatusHistory.order_id == order_id
    ).order_by(OrderStatusHistory.created_at)
    
    history_result = await db.execute(history_query)
    history_items = history_result.scalars().all()
    
    history = [
        {
            "old_status": item.old_status,
            "new_status": item.new_status,
            "comment": item.comment,
            "created_at": item.created_at.isoformat()
        }
        for item in history_items
    ]
    
    return OrderDetailResponse(
        id=order.id,
        user_id=order.user_id,
        service_id=order.service_id,
        service_name=order.service.name_ru if order.service else None,
        params=order.params,
        estimate_total=float(order.estimate_total),
        status=order.status.value,
        created_at=order.created_at,
        deadline=order.deadline,
        document_url=order.document_url,
        status_history=history
    )
