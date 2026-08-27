"""
CurrencyRatesService - сервис для работы с курсами валют ЦБУ

Получает официальные курсы валют из API Центрального Банка Узбекистана (ЦБУ),
вычисляет изменения относительно предыдущего дня и сохраняет в БД.
"""
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional

import httpx
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.currency_rate import CurrencyRate

logger = logging.getLogger(__name__)

# API ЦБУ: https://cbu.uz/ru/arkhiv-kursov-valyut/json/
CBU_API_URL = "https://cbu.uz/ru/arkhiv-kursov-valyut/json/"

# Целевые валюты для отображения
TARGET_CURRENCIES = ["USD", "EUR", "RUB", "GBP", "CNY"]

# Маппинг кодов ЦБУ → ISO кодов
CBU_CODE_MAP = {
    "USD": "USD",
    "EUR": "EUR",
    "RUB": "RUB",
    "GBP": "GBP",
    "CNY": "CNY",
}


class CurrencyRatesService:
    """Сервис для получения и хранения курсов валют ЦБУ"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_latest_rates(self) -> list[dict]:
        """
        Получить актуальные курсы валют из API ЦБУ.

        Returns:
            Список словарей с данными по каждой валюте.

        Raises:
            httpx.HTTPError: При проблемах с сетью или API ЦБУ.
        """
        logger.info("Запрос курсов валют из API ЦБУ: %s", CBU_API_URL)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(CBU_API_URL)
            response.raise_for_status()
            data = response.json()

        logger.info("Получено %d записей от ЦБУ", len(data))

        rates = []
        for item in data:
            code = item.get("Ccy", "").upper()
            if code not in TARGET_CURRENCIES:
                continue

            try:
                rate_value = Decimal(str(item.get("Rate", "0")))
                rate_date_str = item.get("Date", "")
                # ЦБУ возвращает дату в формате "дд.мм.гггг"
                rate_date = datetime.strptime(rate_date_str, "%d.%m.%Y").date()

                rates.append({
                    "currency_code": code,
                    "rate": rate_value,
                    "date": rate_date,
                    "name": item.get("CcyNm_RU", code),
                    "nominal": int(item.get("Nominal", 1)),
                })
            except (ValueError, KeyError) as e:
                logger.warning("Не удалось обработать запись для %s: %s", code, e)
                continue

        logger.info("Обработано %d целевых валют", len(rates))
        return rates

    async def calculate_change(
        self,
        currency_code: str,
        current_rate: Decimal,
        current_date: date,
    ) -> Decimal:
        """
        Вычислить изменение курса относительно предыдущей записи в БД.

        Args:
            currency_code: ISO код валюты (например, "USD").
            current_rate: Текущий курс.
            current_date: Дата текущего курса.

        Returns:
            Изменение курса (положительное = рост, отрицательное = падение).
            Возвращает 0 если предыдущая запись не найдена.
        """
        # Ищем предыдущую запись для этой валюты (до текущей даты)
        query = (
            select(CurrencyRate)
            .where(
                and_(
                    CurrencyRate.currency_code == currency_code,
                    CurrencyRate.date < datetime.combine(current_date, datetime.min.time()),
                )
            )
            .order_by(desc(CurrencyRate.date))
            .limit(1)
        )
        result = await self.db.execute(query)
        previous = result.scalar_one_or_none()

        if previous is None:
            logger.debug(
                "Нет предыдущей записи для %s — изменение = 0",
                currency_code,
            )
            return Decimal("0")

        change = current_rate - previous.rate
        logger.debug(
            "%s: предыдущий=%.4f, текущий=%.4f, изменение=%.4f",
            currency_code,
            previous.rate,
            current_rate,
            change,
        )
        return change

    async def save_rates(self, rates: list[dict]) -> list[CurrencyRate]:
        """
        Сохранить полученные курсы в БД с расчётом изменений.
        Операция идемпотентна: если запись (дата, код) уже существует,
        она обновляется.

        Args:
            rates: Список словарей от fetch_latest_rates().

        Returns:
            Список сохранённых/обновлённых объектов CurrencyRate.
        """
        saved = []

        for rate_data in rates:
            code = rate_data["currency_code"]
            current_rate = rate_data["rate"]
            current_date = rate_data["date"]

            # Проверяем, существует ли запись на эту дату
            existing_query = select(CurrencyRate).where(
                and_(
                    CurrencyRate.currency_code == code,
                    CurrencyRate.date == datetime.combine(current_date, datetime.min.time()),
                )
            )
            existing_result = await self.db.execute(existing_query)
            existing = existing_result.scalar_one_or_none()

            change = await self.calculate_change(code, current_rate, current_date)

            if existing:
                # Обновляем существующую запись
                existing.rate = current_rate
                existing.change = change
                saved.append(existing)
                logger.debug("Обновлён курс %s на %s: %.4f", code, current_date, current_rate)
            else:
                # Создаём новую запись
                new_rate = CurrencyRate(
                    date=datetime.combine(current_date, datetime.min.time()),
                    currency_code=code,
                    rate=current_rate,
                    change=change,
                )
                self.db.add(new_rate)
                saved.append(new_rate)
                logger.debug("Добавлен курс %s на %s: %.4f", code, current_date, current_rate)

        await self.db.commit()

        # Обновляем состояние после коммита
        for obj in saved:
            await self.db.refresh(obj)

        logger.info("Сохранено/обновлено %d записей курсов валют", len(saved))
        return saved

    async def get_rates_history(
        self,
        currency_code: str,
        days: int = 30,
        offset: int = 0,
        limit: int = 100,
    ) -> list[CurrencyRate]:
        """
        Получить историю курсов для конкретной валюты.

        Args:
            currency_code: ISO код валюты.
            days: Количество дней для выборки (по умолчанию 30).
            offset: Смещение для пагинации.
            limit: Максимум записей для возврата.

        Returns:
            Список CurrencyRate, отсортированный по дате (новые первые).
        """
        from_date = datetime.now() - timedelta(days=days)

        query = (
            select(CurrencyRate)
            .where(
                and_(
                    CurrencyRate.currency_code == currency_code.upper(),
                    CurrencyRate.date >= from_date,
                )
            )
            .order_by(desc(CurrencyRate.date))
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_widget_rates(self) -> list[CurrencyRate]:
        """
        Получить последние курсы для виджета (топ-5 целевых валют).

        Returns:
            Список последних записей CurrencyRate по каждой из TARGET_CURRENCIES.
        """
        latest_rates = []

        for code in TARGET_CURRENCIES:
            query = (
                select(CurrencyRate)
                .where(CurrencyRate.currency_code == code)
                .order_by(desc(CurrencyRate.date))
                .limit(1)
            )
            result = await self.db.execute(query)
            rate = result.scalar_one_or_none()
            if rate:
                latest_rates.append(rate)

        return latest_rates
