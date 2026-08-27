"""
StaticContent model - статические страницы сайта
"""
from sqlalchemy import Column, Integer, String, Text
from app.db.database import Base


class StaticContent(Base):
    """Модель статического контента"""
    __tablename__ = "static_content"
    
    id = Column(Integer, primary_key=True, index=True)
    page_key = Column(String(100), unique=True, nullable=False, index=True)
    title_ru = Column(String(255), nullable=False)
    content_ru = Column(Text, nullable=False)
