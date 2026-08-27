"""
Admin API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.service import Service
from app.models.user import User
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from app.core.security import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/services", response_model=ServiceResponse)
async def create_service(
    service: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Создать новую услугу (только для администраторов)
    """
    # Check slug uniqueness
    query = select(Service).where(Service.slug == service.slug)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Услуга с таким slug уже существует")
    
    new_service = Service(**service.model_dump())
    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)
    
    return ServiceResponse.model_validate(new_service)


@router.put("/services/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    service_update: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Обновить услугу (только для администраторов)
    """
    query = select(Service).where(Service.id == service_id)
    result = await db.execute(query)
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    
    # Update fields
    update_data = service_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)
    
    await db.commit()
    await db.refresh(service)
    
    return ServiceResponse.model_validate(service)


@router.delete("/services/{service_id}")
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Деактивировать услугу (мягкое удаление, только для администраторов)
    """
    query = select(Service).where(Service.id == service_id)
    result = await db.execute(query)
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    
    service.is_active = False
    await db.commit()
    
    return {"message": "Услуга деактивирована"}


# ─────────────────────────────────────────────
# Pricing Rules Admin Endpoints
# ─────────────────────────────────────────────

from app.schemas.calculator import (
    PricingRuleCreate,
    PricingRuleUpdate,
    PricingRuleResponse,
)
from app.models.pricing_rule import PricingRule


@router.post("/pricing-rules", response_model=PricingRuleResponse)
async def create_pricing_rule(
    rule_data: PricingRuleCreate,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(require_admin),  # TODO: Uncomment when auth is ready
) -> PricingRuleResponse:
    """Создать новое правило ценообразования (только для администраторов)"""
    try:
        new_rule = PricingRule(
            service_id=rule_data.service_id,
            param_key=rule_data.param_key,
            rate_type=rule_data.rate_type,
            base_fee=rule_data.base_fee,
            tiers=rule_data.tiers,
            is_active=rule_data.is_active,
        )
        db.add(new_rule)
        await db.commit()
        await db.refresh(new_rule)

        # Инвалидируем кеш правил для этой услуги
        from app.services.pricing_engine import PricingEngine
        engine = PricingEngine(db)
        await engine.invalidate_rules_cache(rule_data.service_id)

        return PricingRuleResponse.model_validate(new_rule)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка создания правила: {str(e)}"
        )


@router.get("/pricing-rules", response_model=list[PricingRuleResponse])
async def list_pricing_rules(
    service_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(require_admin),  # TODO: Uncomment when auth is ready
) -> list[PricingRuleResponse]:
    """Получить список правил ценообразования (с фильтром по service_id)"""
    query = select(PricingRule)
    if service_id is not None:
        query = query.where(PricingRule.service_id == service_id)
    query = query.order_by(PricingRule.id)

    result = await db.execute(query)
    rules = result.scalars().all()

    return [PricingRuleResponse.model_validate(rule) for rule in rules]


@router.put("/pricing-rules/{rule_id}", response_model=PricingRuleResponse)
async def update_pricing_rule(
    rule_id: int,
    rule_data: PricingRuleUpdate,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(require_admin),  # TODO: Uncomment when auth is ready
) -> PricingRuleResponse:
    """Обновить правило ценообразования (только для администраторов)"""
    query = select(PricingRule).where(PricingRule.id == rule_id)
    result = await db.execute(query)
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=404, detail="Правило не найдено")

    try:
        # Обновляем только переданные поля
        if rule_data.param_key is not None:
            rule.param_key = rule_data.param_key
        if rule_data.rate_type is not None:
            rule.rate_type = rule_data.rate_type
        if rule_data.base_fee is not None:
            rule.base_fee = rule_data.base_fee
        if rule_data.tiers is not None:
            rule.tiers = rule_data.tiers
        if rule_data.is_active is not None:
            rule.is_active = rule_data.is_active

        await db.commit()
        await db.refresh(rule)

        # Инвалидируем кеш правил
        from app.services.pricing_engine import PricingEngine
        engine = PricingEngine(db)
        await engine.invalidate_rules_cache(rule.service_id)

        return PricingRuleResponse.model_validate(rule)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обновления правила: {str(e)}"
        )


@router.delete("/pricing-rules/{rule_id}", response_model=dict)
async def delete_pricing_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(require_admin),  # TODO: Uncomment when auth is ready
) -> dict:
    """Деактивировать правило ценообразования (is_active=False)"""
    query = select(PricingRule).where(PricingRule.id == rule_id)
    result = await db.execute(query)
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=404, detail="Правило не найдено")

    try:
        rule.is_active = False
        await db.commit()

        # Инвалидируем кеш правил
        from app.services.pricing_engine import PricingEngine
        engine = PricingEngine(db)
        await engine.invalidate_rules_cache(rule.service_id)

        return {"message": "Правило успешно деактивировано", "rule_id": rule_id}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка деактивации правила: {str(e)}"
        )
