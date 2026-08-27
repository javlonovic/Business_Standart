"""
CurrencyRate model - курсы валют
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.db.database import Base


class CurrencyRate(Base):
    """Модель курса валюты"""
    __tablename__ = "currency_rates"
    __table_args__ = (
        UniqueConstraint('date', 'currency_code', name='uq_date_currency'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=False), nullable=False, index=True)
    currency_code = Column(String(3), nullable=False, index=True)
    rate = Column(Numeric(15, 6), nullable=False)
    change = Column(Numeric(15, 6), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
