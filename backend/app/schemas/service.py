"""
Pydantic schemas for Service
"""
from pydantic import BaseModel, Field
from typing import Optional


class ServiceBase(BaseModel):
    """Базовая схема услуги"""
    slug: str = Field(..., max_length=100)
    name_ru: str = Field(..., max_length=255)
    description_ru: Optional[str] = None
    icon_url: Optional[str] = Field(None, max_length=500)
    is_active: bool = True
    sort_order: int = 0


class ServiceCreate(ServiceBase):
    """Схема создания услуги"""
    pass


class ServiceUpdate(ServiceBase):
    """Схема обновления услуги"""
    slug: Optional[str] = None
    name_ru: Optional[str] = None


class ServiceResponse(ServiceBase):
    """Схема ответа услуги"""
    id: int
    
    class Config:
        from_attributes = True


class ServiceList(BaseModel):
    """Список услуг"""
    items: list[ServiceResponse]
    total: int
