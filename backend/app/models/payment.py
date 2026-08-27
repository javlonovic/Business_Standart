"""
Payment model - платёжные транзакции
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class PaymentProvider(str, enum.Enum):
    """Платёжные системы"""
    PAYME = "payme"
    CLICK = "click"


class PaymentStatus(str, enum.Enum):
    """Статусы платежа"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Payment(Base):
    """Модель платёжной транзакции"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    provider = Column(SQLEnum(PaymentProvider), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    external_id = Column(String(255), unique=True, index=True, nullable=False)
    webhook_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="payments")
