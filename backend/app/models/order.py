"""
Order models - заявки клиентов
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class OrderStatus(str, enum.Enum):
    """Статусы заявки"""
    DRAFT = "draft"
    AWAITING_PAYMENT = "awaiting_payment"
    PAID = "paid"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    """Модель заявки"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    params = Column(JSONB, nullable=False)
    estimate_total = Column(Numeric(15, 2), nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.DRAFT, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deadline = Column(DateTime(timezone=True), nullable=True)
    document_url = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    service = relationship("Service", back_populates="orders")
    payments = relationship("Payment", back_populates="order")
    status_history = relationship("OrderStatusHistory", back_populates="order")


class OrderStatusHistory(Base):
    """История изменений статусов заявки"""
    __tablename__ = "order_status_history"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    old_status = Column(String(30), nullable=False)
    new_status = Column(String(30), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="status_history")
