"""
Service model - оценочные услуги компании
"""
from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base


class Service(Base):
    """Модель услуги"""
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name_ru = Column(String(255), nullable=False)
    description_ru = Column(Text, nullable=True)
    icon_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    
    # Relationships
    pricing_rules = relationship("PricingRule", back_populates="service")
    orders = relationship("Order", back_populates="service")
