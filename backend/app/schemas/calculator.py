"""
Pydantic схемы для калькулятора и правил ценообразования
"""
from decimal import Decimal
from typing import Any, Optional, List
from pydantic import BaseModel, Field, field_validator


# ─────────────────────────────────────────────
# Calculator schemas
# ─────────────────────────────────────────────

class EstimateRequest(BaseModel):
    """Запрос на расчёт стоимости услуги"""
    service_id: int = Field(..., description="ID услуги")
    params: dict[str, Any] = Field(
        ...,
        description="Параметры расчёта. Ключи зависят от выбранной услуги.",
    )

    @field_validator("service_id")
    @classmethod
    def service_id_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("service_id должен быть положительным числом")
        return v

    @field_validator("params")
    @classmethod
    def params_not_empty(cls, v: dict) -> dict:
        if not v:
            raise ValueError("params не может быть пустым объектом")
        return v


class EstimateBreakdownItem(BaseModel):
    """Строка детализации расчёта"""
    item_name: str = Field(..., description="Название позиции")
    description: str = Field(..., description="Описание правила применения")
    amount: Decimal = Field(..., description="Сумма по данной позиции в сумах")


class EstimateResult(BaseModel):
    """Результат расчёта стоимости"""
    total: Decimal = Field(..., description="Итоговая стоимость в сумах")
    breakdown: List[EstimateBreakdownItem] = Field(
        ..., description="Детализация расчёта по правилам"
    )
    is_preliminary: bool = Field(
        True, description="Всегда True — это предварительная стоимость"
    )
    currency: str = Field("UZS", description="Валюта расчёта")


class ServiceParamMeta(BaseModel):
    """Метаданные одного параметра для динамической формы"""
    key: str = Field(..., description="Ключ параметра (совпадает с param_key в правиле)")
    label: str = Field(..., description="Подсказка для пользователя на русском")
    type: str = Field(
        ...,
        description="Тип поля: number | boolean | select",
    )
    required: bool = Field(True)
    min_value: Optional[float] = Field(None, description="Минимальное значение (для number)")
    max_value: Optional[float] = Field(None, description="Максимальное значение (для number)")
    options: Optional[List[dict[str, str]]] = Field(
        None, description="Опции для select [{value, label}]"
    )
    hint: Optional[str] = Field(None, description="Дополнительная подсказка")


class ServiceParamsResponse(BaseModel):
    """Список параметров для динамической формы калькулятора"""
    service_id: int
    service_name: str
    params: List[ServiceParamMeta]


# ─────────────────────────────────────────────
# Pricing Rule admin schemas
# ─────────────────────────────────────────────

class TierItem(BaseModel):
    """Один диапазон для tiered-правила"""
    min: float = Field(..., description="Нижняя граница диапазона (включительно)")
    max: Optional[float] = Field(None, description="Верхняя граница (None = без ограничения)")
    rate: float = Field(..., description="Ставка для этого диапазона")


class PricingRuleBase(BaseModel):
    """Базовая схема правила ценообразования"""
    service_id: int
    param_key: str = Field(..., max_length=100, description="Ключ параметра (area, has_land, …)")
    rate_type: str = Field(
        ...,
        description="Тип правила: linear | tiered | flat_addon",
    )
    base_fee: Optional[Decimal] = Field(
        None, description="Базовая ставка (для linear и flat_addon)"
    )
    tiers: Optional[List[TierItem]] = Field(
        None, description="Диапазоны для tiered-правила"
    )
    is_active: bool = True

    @field_validator("rate_type")
    @classmethod
    def validate_rate_type(cls, v: str) -> str:
        allowed = {"linear", "tiered", "flat_addon"}
        if v not in allowed:
            raise ValueError(
                f"rate_type должен быть одним из: {', '.join(allowed)}"
            )
        return v

    @field_validator("tiers")
    @classmethod
    def validate_tiers(cls, v, info):
        rate_type = info.data.get("rate_type")
        if rate_type == "tiered":
            if not v:
                raise ValueError(
                    "Для типа 'tiered' обязательно поле tiers (список диапазонов)"
                )
            # Проверяем отсутствие пересечений
            sorted_tiers = sorted(v, key=lambda t: t.min)
            for i in range(len(sorted_tiers) - 1):
                current_max = sorted_tiers[i].max
                next_min = sorted_tiers[i + 1].min
                if current_max is not None and current_max > next_min:
                    raise ValueError(
                        f"Диапазоны пересекаются: [{sorted_tiers[i].min}, {current_max})"
                        f" и [{next_min}, …)"
                    )
        return v


class PricingRuleCreate(PricingRuleBase):
    """Схема создания правила"""
    pass


class PricingRuleUpdate(BaseModel):
    """Схема обновления правила (все поля опциональны)"""
    param_key: Optional[str] = Field(None, max_length=100)
    rate_type: Optional[str] = None
    base_fee: Optional[Decimal] = None
    tiers: Optional[List[TierItem]] = None
    is_active: Optional[bool] = None

    @field_validator("rate_type")
    @classmethod
    def validate_rate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"linear", "tiered", "flat_addon"}
            if v not in allowed:
                raise ValueError(
                    f"rate_type должен быть одним из: {', '.join(allowed)}"
                )
        return v


class PricingRuleResponse(PricingRuleBase):
    """Схема ответа правила ценообразования"""
    id: int

    model_config = {"from_attributes": True}
