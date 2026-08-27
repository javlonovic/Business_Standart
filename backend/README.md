# Business Standart Backend

Backend для веб-платформы оценочной компании Business Standart.

## Технологии

- **Python 3.11+**
- **FastAPI** - веб-фреймворк
- **PostgreSQL** - база данных
- **SQLAlchemy** - ORM
- **Alembic** - миграции БД
- **Celery + Redis** - фоновые задачи
- **Docker Compose** - для разработки

## Установка и запуск

### Через Docker Compose (рекомендуется)

```bash
# Запустить все сервисы (PostgreSQL, Redis, Backend)
docker-compose up -d

# Применить миграции
docker-compose exec backend alembic upgrade head

# Просмотр логов
docker-compose logs -f backend
```

### Локальная установка

```bash
# Установить зависимости
cd backend
poetry install

# Создать .env файл
cp .env.example .env
# Отредактировать .env с вашими настройками

# Применить миграции
poetry run alembic upgrade head

# Запустить сервер
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Документация

После запуска, документация доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Структура проекта

```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Конфигурация, security
│   ├── db/           # Database setup
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   └── services/     # Business logic
├── alembic/          # Database migrations
├── tests/            # Tests
└── pyproject.toml    # Dependencies
```

## Миграции базы данных

```bash
# Создать новую миграцию
poetry run alembic revision --autogenerate -m "Description"

# Применить миграции
poetry run alembic upgrade head

# Откатить миграцию
poetry run alembic downgrade -1
```

## Разработка

### Создать суперпользователя (TODO)

```python
# Через Python console
from app.db.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin = User(
            phone="+998901234567",
            email="admin@business-standart.uz",
            password_hash=hash_password("admin123"),
            full_name="Администратор",
            role=UserRole.SUPERADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(admin)
        await db.commit()
```

## Тестирование

```bash
# Запустить все тесты
poetry run pytest

# С покрытием
poetry run pytest --cov=app
```
