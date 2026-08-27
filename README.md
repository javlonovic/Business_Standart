# Business Standart - Веб-платформа оценочной компании

Современная веб-платформа для оценочной компании ООО «BUSINESS STANDART» (Ташкент, Узбекистан) с интерактивным калькулятором стоимости услуг, личным кабинетом и интеграцией платёжных систем Payme/Click.

## 🎯 Особенности

- ✨ **Интерактивный калькулятор** - расчёт стоимости оценочных услуг с прозрачной детализацией
- 💳 **Онлайн-оплата** - интеграция Payme и Click (Uzcard/Humo/Visa/MC)
- 👤 **Личный кабинет** - отслеживание заявок и скачивание документов
- 🗺️ **Интерактивная карта** - выбор района для оценки
- 💱 **Курсы валют** - актуальные данные от ЦБУ
- 🎨 **Cozy Minimalist** - тёплый минимализм в дизайне
- 🌐 **Полностью на русском** - все тексты и интерфейс

## 📚 Технологический стек

### Backend
- **Python 3.11+** + **FastAPI**
- **PostgreSQL** - база данных
- **Redis** - кеширование
- **Celery** - фоновые задачи (обновление курсов, уведомления)
- **S3** - хранилище документов
- **Alembic** - миграции БД

### Frontend
- **Flutter Web** (Dart) - единая кодовая база для web и будущих мобильных приложений
- **Provider** - state management
- **HTTP** - API клиент

### Интеграции
- **Payme Merchant API**
- **Click Merchant API**
- **API ЦБУ** (cbu.uz) - курсы валют
- **SMS Gateway** (playmobile.uz)

## 🚀 Быстрый старт

### Требования
- Docker & Docker Compose
- Python 3.11+ (для локальной разработки)
- Flutter 3.16+ (для frontend разработки)

### Запуск через Docker Compose

```bash
# Клонировать репозиторий
git clone <repository-url>
cd business-standart-website

# Запустить все сервисы
docker-compose up -d

# Применить миграции БД
docker-compose exec backend alembic upgrade head

# Проверить статус
docker-compose ps

# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# PostgreSQL: localhost:5432
# Redis: localhost:6379
```

### Локальная разработка

#### Backend

```bash
cd backend

# Установить зависимости (Poetry)
poetry install

# Создать .env файл
cp .env.example .env

# Запустить PostgreSQL и Redis через Docker
docker-compose up postgres redis -d

# Применить миграции
poetry run alembic upgrade head

# Запустить сервер
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Установить зависимости
flutter pub get

# Запустить в браузере
flutter run -d chrome --web-port 8080
```

## 📁 Структура проекта

```
business-standart-website/
├── backend/                 # Backend (FastAPI)
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Конфигурация, security
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── db/             # Database setup
│   ├── alembic/            # Миграции БД
│   └── tests/              # Тесты
│
├── frontend/               # Frontend (Flutter Web)
│   ├── lib/
│   │   ├── core/          # Тема, константы
│   │   ├── models/        # Data models
│   │   ├── providers/     # State management
│   │   ├── screens/       # UI screens
│   │   ├── services/      # API service
│   │   └── widgets/       # Reusable widgets
│   └── web/               # Web-specific files
│
├── docker-compose.yml     # Docker orchestration
└── business-standart-website/ # Спецификация проекта
    ├── design.md          # Техническое проектирование
    ├── requirements.md    # Требования
    └── tasks.md           # План реализации
```

## 📋 Фазы разработки

✅ **Фаза 1: Фундамент и статический контент** (ЗАВЕРШЕНО)
- Backend структура и API
- База данных и модели
- Flutter Web frontend
- Статические страницы

✅  **Фаза 2: Система курсов валют** (В РАЗРАБОТКЕ)
- Интеграция с API ЦБУ
- Celery задачи
- Виджет курсов

✅  **Фаза 3: Движок калькулятора**
- Конфигурируемые правила ценообразования
- Калькулятор UI
- Детализация расчётов

✅  **Фаза 4: Аутентификация и заявки**
- Регистрация/вход
- Личный кабинет
- Управление заявками

✅  **Фаза 5: Платёжная интеграция**
- Payme & Click
- Webhooks
- Уведомления

✅  **Фаза 6: Карта и документы**
- Интерактивная карта районов
- S3 хранилище документов
- Админ панель

## 🔧 Конфигурация

### Backend (.env)

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/business_standart
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
PAYME_MERCHANT_ID=your-payme-id
PAYME_SECRET_KEY=your-payme-secret
CLICK_MERCHANT_ID=your-click-id
CLICK_SECRET_KEY=your-click-secret
```

### Frontend (api_service.dart)

```dart
final String baseUrl = 'http://localhost:8000/api';
```

## 📖 API Документация

После запуска backend доступна Swagger документация:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Тестирование

### Backend

```bash
cd backend

# Unit тесты
poetry run pytest

# С покрытием
poetry run pytest --cov=app

# Property-based тесты
poetry run pytest -k property
```

### Frontend

```bash
cd frontend

# Unit тесты
flutter test

# Integration тесты
flutter test integration_test
```

## 🚢 Deployment

### Backend (Production)

```bash
# Build Docker image
docker build -t business-standart-backend ./backend

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  --env-file .env.production \
  business-standart-backend
```

### Frontend (Static hosting)

```bash
cd frontend

# Build production
flutter build web --release

# Deploy build/web/ to:
# - Vercel, Netlify, Cloudflare Pages
# - Nginx, Apache
# - AWS S3 + CloudFront
```

## 📝 Лицензия

Proprietary - ООО «BUSINESS STANDART»

## 📞 Контакты

- **Телефон**: +998 (71) 150-15-15
- **Мобильный**: +998 (90) 176-60-60
- **Email**: business_standart@mail.ru
- **Адрес**: г. Ташкент, Узбекистан

---

© 2024 Business Standart. Все права защищены.
