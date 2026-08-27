"""
PricingRule model - правила ценообразования
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.database import Base


class PricingRule(Base):
    """Модель правила ценообразования"""
    __tablename__ = "pricing_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    param_key = Column(String(100), nullable=False)
    rate_type = Column(String(20), nullable=False)  # 'linear', 'tiered', 'flat_addon'
    base_fee = Column(Numeric(15, 2), nullable=True)
    tiers = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    service = relationship("Service", back_populates="pricing_rules")
