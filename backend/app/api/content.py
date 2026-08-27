"""
API endpoints for static content
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.static_content import StaticContent
from app.schemas.content import ContentResponse

router = APIRouter(prefix="/api/content", tags=["content"])


@router.get("/{page_key}", response_model=ContentResponse)
async def get_content(
    page_key: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить статический контент по ключу страницы
    
    - **page_key**: идентификатор страницы (about, contacts, etc.)
    """
    query = select(StaticContent).where(StaticContent.page_key == page_key)
    result = await db.execute(query)
    content = result.scalar_one_or_none()
    
    if not content:
        # Return default content if not found
        return ContentResponse(
            page_key=page_key,
            title_ru=f"Страница {page_key}",
            content_ru="Контент в разработке"
        )
    
    return ContentResponse.model_validate(content)
