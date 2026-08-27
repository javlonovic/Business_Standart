"""
API endpoints for services
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db.database import get_db
from app.models.service import Service
from app.schemas.service import ServiceResponse, ServiceList

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("", response_model=ServiceList)
async def get_services(
    is_active: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список услуг
    
    - **is_active**: фильтр по активным услугам (по умолчанию True)
    """
    query = select(Service).where(Service.is_active == is_active).order_by(Service.sort_order)
    result = await db.execute(query)
    services = result.scalars().all()
    
    return ServiceList(
        items=[ServiceResponse.model_validate(service) for service in services],
        total=len(services)
    )


@router.get("/{slug}", response_model=ServiceResponse)
async def get_service_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить детали услуги по slug
    
    - **slug**: уникальный идентификатор услуги
    """
    query = select(Service).where(Service.slug == slug)
    result = await db.execute(query)
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    
    return ServiceResponse.model_validate(service)
