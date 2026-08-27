"""
PricingEngine — движок расчёта стоимости оценочных услуг

Реализует три типа правил ценообразования:
  • linear    — линейная надбавка: addon = param_value × base_fee
  • tiered    — ступенчатая ставка: выбирается диапазон по значению параметра
  • flat_addon — фиксированная надбавка: если param == True, addon = base_fee

Принцип работы:
  1. Загружаем все активные правила для service_id (с кешированием в Redis)
  2. Применяем base_fee первого правила как базовую ставку услуги
  3. Итерируемся по правилам, формируем breakdown
  4. total = sum(item.amount for item in breakdown)

Инвариант (гарантируется): sum(breakdown[i].amount) == total
"""
import json
import logging
import os
from decimal import Decimal
from typing import Any, Optional

import redis.asyncio as aioredis
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pricing_rule import PricingRule
from app.models.service import Service
from app.schemas.calculator import (
    EstimateBreakdownItem,
    EstimateResult,
    ServiceParamMeta,
    ServiceParamsResponse,
)

logger = logging.getLogger(__name__)

# Кеш правил в Redis, TTL 5 минут (администратор может изменить правила)
RULES_CACHE_TTL = 300
RULES_CACHE_KEY_PREFIX = "pricing_rules:"


async def _get_redis() -> Optional[aioredis.Redis]:
    """Асинхронный Redis-клиент. Возвращает None при недоступности."""
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    try:
        client = aioredis.from_url(redis_url, decode_responses=True)
        await client.ping()
        return client
    except Exception as e:
        logger.warning("Redis недоступен для PricingEngine: %s", e)
        return None


class PricingEngine:
    """Движок расчёта стоимости на основе конфигурируемых правил."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ─────────────────────────────────────────────
    # Получение правил
    # ─────────────────────────────────────────────

    async def get_pricing_rules(self, service_id: int) -> list[PricingRule]:
        """
        Получить активные правила ценообразования для услуги.
        Результат кешируется в Redis на 5 минут.
        """
        cache_key = f"{RULES_CACHE_KEY_PREFIX}{service_id}"
        redis = await _get_redis()

        # Попытка из кеша
        if redis:
            try:
                cached = await redis.get(cache_key)
                if cached:
                    raw_rules = json.loads(cached)
                    # Восстанавливаем объекты ORM из словарей
                    rules = [PricingRule(**r) for r in raw_rules]
                    logger.debug(
                        "Правила для service_id=%d: %d шт. (из кеша)",
                        service_id,
                        len(rules),
                    )
                    await redis.aclose()
                    return rules
            except Exception as e:
                logger.warning("Ошибка чтения кеша правил: %s", e)

        # Из БД
        query = (
            select(PricingRule)
            .where(
                and_(
                    PricingRule.service_id == service_id,
                    PricingRule.is_active == True,  # noqa: E712
                )
            )
            .order_by(PricingRule.id)
        )
        result = await self.db.execute(query)
        rules = list(result.scalars().all())

        logger.debug(
            "Правила для service_id=%d: %d шт. (из БД)", service_id, len(rules)
        )

        # Сохраняем в кеш
        if redis and rules:
            try:
                serializable = [
                    {
                        "id": r.id,
                        "service_id": r.service_id,
                        "param_key": r.param_key,
                        "rate_type": r.rate_type,
                        "base_fee": str(r.base_fee) if r.base_fee is not None else None,
                        "tiers": r.tiers,
                        "is_active": r.is_active,
                    }
                    for r in rules
                ]
                await redis.setex(cache_key, RULES_CACHE_TTL, json.dumps(serializable))
            except Exception as e:
                logger.warning("Ошибка записи кеша правил: %s", e)
            finally:
                await redis.aclose()

        return rules

    async def invalidate_rules_cache(self, service_id: int) -> None:
        """Удалить кеш правил для service_id (вызывается после изменения правил)."""
        redis = await _get_redis()
        if redis:
            try:
                await redis.delete(f"{RULES_CACHE_KEY_PREFIX}{service_id}")
                logger.info("Кеш правил для service_id=%d удалён", service_id)
            except Exception as e:
                logger.warning("Не удалось удалить кеш правил: %s", e)
            finally:
                await redis.aclose()

    # ─────────────────────────────────────────────
    # Применение правил
    # ─────────────────────────────────────────────

    def apply_linear_rule(
        self,
        rule: PricingRule,
        params: dict[str, Any],
    ) -> Optional[EstimateBreakdownItem]:
        """
        Линейная надбавка: addon = param_value × base_fee

        Пример: площадь 120 кв.м × 5 000 сум/м² = 600 000 сум
        """
        raw = params.get(rule.param_key)
        if raw is None:
            return None

        try:
            value = Decimal(str(raw))
        except Exception:
            raise ValueError(
                f"Параметр '{rule.param_key}' должен быть числом, получено: {raw!r}"
            )

        if value < 0:
            raise ValueError(
                f"Параметр '{rule.param_key}' должен быть неотрицательным, получено: {value}"
            )

        base_fee = Decimal(str(rule.base_fee)) if rule.base_fee is not None else Decimal("0")
        amount = value * base_fee

        return EstimateBreakdownItem(
            item_name=f"Расчёт по параметру «{rule.param_key}»",
            description=f"{value} × {base_fee} сум/ед. = {amount} сум",
            amount=amount,
        )

    def apply_tiered_rule(
        self,
        rule: PricingRule,
        params: dict[str, Any],
    ) -> Optional[EstimateBreakdownItem]:
        """
        Ступенчатая ставка: выбирается диапазон по значению параметра.

        tiers: [{"min": 0, "max": 100, "rate": 10000}, {"min": 100, "max": null, "rate": 15000}]
        """
        raw = params.get(rule.param_key)
        if raw is None:
            return None

        try:
            value = Decimal(str(raw))
        except Exception:
            raise ValueError(
                f"Параметр '{rule.param_key}' должен быть числом, получено: {raw!r}"
            )

        if value < 0:
            raise ValueError(
                f"Параметр '{rule.param_key}' должен быть неотрицательным"
            )

        tiers = rule.tiers or []
        matched_tier = None

        for tier in tiers:
            tier_min = Decimal(str(tier["min"]))
            tier_max = tier.get("max")

            if tier_max is None:
                # Последний диапазон без верхней границы
                if value >= tier_min:
                    matched_tier = tier
                    break
            else:
                tier_max_dec = Decimal(str(tier_max))
                if tier_min <= value < tier_max_dec:
                    matched_tier = tier
                    break

        if matched_tier is None:
            raise ValueError(
                f"Значение параметра '{rule.param_key}' = {value} "
                f"не попадает ни в один диапазон правила id={rule.id}"
            )

        rate = Decimal(str(matched_tier["rate"]))
        tier_min_str = str(matched_tier["min"])
        tier_max_str = (
            str(matched_tier["max"]) if matched_tier.get("max") is not None else "∞"
        )

        return EstimateBreakdownItem(
            item_name=f"Ставка по диапазону «{rule.param_key}»",
            description=(
                f"Диапазон [{tier_min_str}, {tier_max_str}): "
                f"фиксированная ставка {rate} сум"
            ),
            amount=rate,
        )

    def apply_flat_addon(
        self,
        rule: PricingRule,
        params: dict[str, Any],
    ) -> Optional[EstimateBreakdownItem]:
        """
        Фиксированная надбавка: если param == True, addon = base_fee

        Поддерживает bool, "true"/"yes"/"1", 1 как truthy.
        """
        raw = params.get(rule.param_key)
        if raw is None:
            return None

        # Поддержка разных truthy-форматов
        if isinstance(raw, bool):
            is_active = raw
        elif isinstance(raw, str):
            is_active = raw.lower() in {"true", "yes", "1", "да"}
        elif isinstance(raw, (int, float)):
            is_active = bool(raw)
        else:
            is_active = False

        if not is_active:
            return None

        base_fee = Decimal(str(rule.base_fee)) if rule.base_fee is not None else Decimal("0")

        # Описание берём из tiers[0]["description"] если есть, иначе генерируем
        description = f"Дополнительная опция «{rule.param_key}»: +{base_fee} сум"
        if rule.tiers and isinstance(rule.tiers, list) and len(rule.tiers) > 0:
            tier_desc = rule.tiers[0].get("description")
            if tier_desc:
                description = tier_desc

        return EstimateBreakdownItem(
            item_name=f"Надбавка «{rule.param_key}»",
            description=description,
            amount=base_fee,
        )

    # ─────────────────────────────────────────────
    # Основной расчёт
    # ─────────────────────────────────────────────

    async def calculate_estimate(
        self,
        service_id: int,
        params: dict[str, Any],
    ) -> EstimateResult:
        """
        Рассчитать предварительную стоимость услуги.

        Алгоритм:
        1. Загружаем активные правила для service_id
        2. Первое правило с base_fee и param_key='_base' (или любым) — базовая ставка услуги
        3. Итерируем по всем правилам, применяем нужный тип
        4. Суммируем breakdown → total

        Инвариант: sum(item.amount for item in breakdown) == total

        Args:
            service_id: ID услуги
            params: словарь параметров от клиента

        Returns:
            EstimateResult с total и breakdown

        Raises:
            ValueError: если правила не найдены или параметры невалидны
        """
        rules = await self.get_pricing_rules(service_id)

        if not rules:
            raise ValueError(
                f"Для услуги id={service_id} не настроены правила ценообразования. "
                "Обратитесь к администратору."
            )

        breakdown: list[EstimateBreakdownItem] = []

        for rule in rules:
            item: Optional[EstimateBreakdownItem] = None

            # Специальный param_key '_base' — базовая стоимость услуги (не зависит от params)
            if rule.param_key == "_base":
                base_fee = (
                    Decimal(str(rule.base_fee))
                    if rule.base_fee is not None
                    else Decimal("0")
                )
                item = EstimateBreakdownItem(
                    item_name="Базовая стоимость услуги",
                    description=f"Фиксированная базовая ставка: {base_fee} сум",
                    amount=base_fee,
                )
            elif rule.rate_type == "linear":
                item = self.apply_linear_rule(rule, params)
            elif rule.rate_type == "tiered":
                item = self.apply_tiered_rule(rule, params)
            elif rule.rate_type == "flat_addon":
                item = self.apply_flat_addon(rule, params)
            else:
                logger.warning(
                    "Неизвестный rate_type '%s' для правила id=%d, пропускаем",
                    rule.rate_type,
                    rule.id,
                )
                continue

            if item is not None:
                breakdown.append(item)

        if not breakdown:
            raise ValueError(
                f"Не удалось применить ни одного правила для услуги id={service_id} "
                "с переданными параметрами. Проверьте обязательные поля."
            )

        # Инвариант: total = sum(breakdown)
        total = sum(item.amount for item in breakdown)

        logger.info(
            "Расчёт для service_id=%d: итого=%s сум, %d позиций в breakdown",
            service_id,
            total,
            len(breakdown),
        )

        return EstimateResult(
            total=total,
            breakdown=breakdown,
            is_preliminary=True,
            currency="UZS",
        )

    # ─────────────────────────────────────────────
    # Метаданные параметров для динамической формы
    # ─────────────────────────────────────────────

    # Маппинг param_key → человекочитаемое название и тип поля
    # Администратор должен пополнять по мере добавления услуг
    PARAM_META: dict[str, dict] = {
        "_base": {"label": "Базовая ставка", "type": "hidden", "required": False},
        "area": {
            "label": "Площадь объекта (кв.м)",
            "type": "number",
            "required": True,
            "min_value": 1,
            "hint": "Общая площадь оцениваемого объекта в квадратных метрах",
        },
        "rooms": {
            "label": "Количество комнат",
            "type": "number",
            "required": False,
            "min_value": 1,
            "max_value": 50,
        },
        "floor": {
            "label": "Этаж",
            "type": "number",
            "required": False,
            "min_value": 1,
            "max_value": 100,
        },
        "floors_total": {
            "label": "Этажность здания",
            "type": "number",
            "required": False,
            "min_value": 1,
        },
        "has_land": {
            "label": "Есть земельный участок",
            "type": "boolean",
            "required": False,
        },
        "land_area": {
            "label": "Площадь земельного участка (сотка)",
            "type": "number",
            "required": False,
            "min_value": 0,
        },
        "region": {
            "label": "Регион расположения объекта",
            "type": "select",
            "required": True,
            "options": [
                {"value": "tashkent_city", "label": "Ташкент (город)"},
                {"value": "tashkent_region", "label": "Ташкентская область"},
                {"value": "samarkand", "label": "Самаркандская область"},
                {"value": "bukhara", "label": "Бухарская область"},
                {"value": "fergana", "label": "Ферганская область"},
                {"value": "andijan", "label": "Андижанская область"},
                {"value": "namangan", "label": "Наманганская область"},
                {"value": "kashkadarya", "label": "Кашкадарьинская область"},
                {"value": "surkhandarya", "label": "Сурхандарьинская область"},
                {"value": "jizzakh", "label": "Джизакская область"},
                {"value": "sirdarya", "label": "Сырдарьинская область"},
                {"value": "navoi", "label": "Навоийская область"},
                {"value": "khorezm", "label": "Хорезмская область"},
                {"value": "karakalpakstan", "label": "Республика Каракалпакстан"},
            ],
        },
        "property_type": {
            "label": "Тип объекта",
            "type": "select",
            "required": True,
            "options": [
                {"value": "apartment", "label": "Квартира"},
                {"value": "house", "label": "Частный дом"},
                {"value": "commercial", "label": "Коммерческая недвижимость"},
                {"value": "land", "label": "Земельный участок"},
                {"value": "office", "label": "Офис"},
                {"value": "warehouse", "label": "Склад"},
                {"value": "industrial", "label": "Промышленный объект"},
            ],
        },
        "year_built": {
            "label": "Год постройки",
            "type": "number",
            "required": False,
            "min_value": 1900,
            "max_value": 2030,
        },
        "urgency": {
            "label": "Срочная оценка (в течение 1 дня)",
            "type": "boolean",
            "required": False,
        },
        "num_objects": {
            "label": "Количество объектов",
            "type": "number",
            "required": True,
            "min_value": 1,
        },
        "vehicle_type": {
            "label": "Тип транспортного средства",
            "type": "select",
            "required": True,
            "options": [
                {"value": "car", "label": "Легковой автомобиль"},
                {"value": "truck", "label": "Грузовой автомобиль"},
                {"value": "bus", "label": "Автобус"},
                {"value": "special", "label": "Специальная техника"},
            ],
        },
        "engine_volume": {
            "label": "Объём двигателя (куб.см)",
            "type": "number",
            "required": False,
            "min_value": 0,
        },
        "business_type": {
            "label": "Тип бизнеса",
            "type": "select",
            "required": True,
            "options": [
                {"value": "individual", "label": "Индивидуальный предприниматель"},
                {"value": "llc", "label": "ООО"},
                {"value": "jsc", "label": "АО"},
                {"value": "other", "label": "Другое"},
            ],
        },
    }

    async def get_service_params(self, service_id: int) -> ServiceParamsResponse:
        """
        Получить метаданные параметров для динамической формы калькулятора.

        Загружает активные правила для услуги и формирует список параметров
        с типами полей, ограничениями и подсказками на русском.

        Args:
            service_id: ID услуги

        Returns:
            ServiceParamsResponse со списком ServiceParamMeta

        Raises:
            ValueError: если услуга не найдена
        """
        # Получаем название услуги
        service_query = select(Service).where(Service.id == service_id)
        service_result = await self.db.execute(service_query)
        service = service_result.scalar_one_or_none()

        if service is None:
            raise ValueError(f"Услуга с id={service_id} не найдена")

        rules = await self.get_pricing_rules(service_id)

        params_meta: list[ServiceParamMeta] = []
        seen_keys: set[str] = set()

        for rule in rules:
            key = rule.param_key

            # Скрываем внутренние ключи
            if key == "_base" or key in seen_keys:
                continue

            seen_keys.add(key)
            meta = self.PARAM_META.get(key, {})

            params_meta.append(
                ServiceParamMeta(
                    key=key,
                    label=meta.get("label", key),
                    type=meta.get("type", "number"),
                    required=meta.get("required", True),
                    min_value=meta.get("min_value"),
                    max_value=meta.get("max_value"),
                    options=meta.get("options"),
                    hint=meta.get("hint"),
                )
            )

        return ServiceParamsResponse(
            service_id=service_id,
            service_name=service.name_ru,
            params=params_meta,
        )
