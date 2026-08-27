"""
Pydantic schemas for static content
"""
from pydantic import BaseModel, Field


class ContentResponse(BaseModel):
    """Схема ответа статического контента"""
    page_key: str = Field(..., max_length=100)
    title_ru: str = Field(..., max_length=255)
    content_ru: str
    
    class Config:
        from_attributes = True


class ContentUpdate(BaseModel):
    """Схема обновления контента"""
    title_ru: str = Field(..., max_length=255)
    content_ru: str
