# Задачи по реализации: Веб-сайт Business Standart

## Обзор
План реализации веб-платформы Business Standart в 6 фазах.

**Стек:** Backend (Python/FastAPI/PostgreSQL), Frontend (Flutter Web), Celery/Redis, S3, Payme/Click API

## Фаза 1: Фундамент и статический контент (2-3 недели)

### 1. Настройка проекта

- [x] 1.1 Создать структуру backend проекта
  - Директории: `backend/app/{api,core,models,services,schemas,db}`
  - pyproject.toml с зависимостями (fastapi, sqlalchemy, alembic, asyncpg, pydantic)
  - .env.example, main.py с FastAPI и CORS
  - _Требования: NFR-5, NFR-10_

- [x] 1.2 Настроить PostgreSQL и Alembic
  - alembic.ini, env.py для async миграций
  - database.py с async engine
  - Base класс для моделей SQLAlchemy
  - Health check endpoint
  - _Требования: NFR-2_

- [x]* 1.3 Docker Compose для разработки
  - docker-compose.yml с PostgreSQL, Redis
  - Dockerfile для backend
  - _Требования: NFR-9_

### 2. Модели данных

- [x] 2.1 Создать модели User и Service
  - User: id, phone, email, password_hash, full_name, is_active, is_verified, created_at
  - Service: id, slug, name_ru, description_ru, icon_url, is_active, sort_order
  - Валидация phone +998XXXXXXXXX
  - Alembic миграция
  - _Требования: 7.1, 7.2, 16.1_

- [x] 2.2 Создать модели Order и OrderStatusHistory
  - Order: id, user_id, service_id, params (JSONB), estimate_total, status, created_at, deadline, document_url
  - OrderStatusHistory для аудита
  - Relationship User-Order
  - Alembic миграция
  - _Требования: 2.1, 2.5, 18.1_

- [x] 2.3 Создать модели PricingRule, Payment, CurrencyRate
  - PricingRule: id, service_id, param_key, rate_type, base_fee, tiers (JSONB), is_active
  - Payment: id, order_id, provider, amount, status, external_id, webhook_data (JSONB)
  - CurrencyRate: id, date, currency_code, rate, change
  - Alembic миграции с индексами
  - _Требования: 1.2, 3.8, 4.9_

- [x]* 2.4 Создать индексы производительности
  - (user_id, status, created_at) для orders
  - (date, currency_code) для currency_rates
  - Уникальный индекс external_id для payments
  - _Требования: 11.3_

### 3. API для статических страниц

- [x] 3.1 CRUD API для услуг
  - GET /api/services - список услуг
  - GET /api/services/{slug} - детали услуги
  - Pydantic схемы ServiceResponse, ServiceList
  - Кеширование в Redis (TTL 1 час)
  - _Требования: 16.6, 16.7_

- [x] 3.2 Endpoints статического контента
  - GET /api/content/about
  - GET /api/content/contacts
  - Модель StaticContent в БД
  - Эндпоинт редактирования
  - _Требования: 13.1, 13.4_

- [x]* 3.3 Валидация и обработка ошибок
  - Exception handlers для ValidationError, NotFoundError
  - Middleware для логирования ошибок
  - Ошибки на русском языке
  - _Требования: 10.1-10.4, 10.7_

### 4. Flutter Web - базовая структура

- [x] 4.1 Создать Flutter Web проект
  - `flutter create --platforms=web business_standart_web`
  - pubspec.yaml: http, provider, flutter_svg, intl
  - Структура lib/{screens,widgets,services,models,providers}
  - Routes и навигация
  - _Требования: NFR-6, NFR-7_

- [x] 4.2 API service и модели
  - ApiService с base URL, headers
  - Модели Service, EstimateResult, Order
  - Методы getServices(), getServiceBySlug()
  - Обработка HTTP ошибок
  - _Требования: 10.1_

- [x] 4.3 Главная страница со списком услуг
  - HomeScreen с карточками услуг
  - Фильтрация и поиск
  - Адаптивная сетка
  - Loading states, error handling
  - _Требования: 19.1, 19.2_

- [x] 4.4 Статические страницы
  - AboutScreen, ServicesScreen, ContactsScreen
  - Responsive layout для мобильных
  - _Требования: 19.1, 19.4_

- [x]* 4.5 Тема и локализация
  - theme.dart "cozy minimalist"
  - Русская локализация (intl)
  - Форматирование дат дд.мм.гггг
  - Форматирование чисел с пробелами
  - _Требования: 13.1, 13.5, 13.7_

### 5. Базовая админ панель

- [ ] 5.1 Модель Admin и роли
  - Поле role в User: client, admin, superadmin
  - Middleware проверки роли
  - Decorator @require_admin
  - _Требования: 8.1, 8.2_

- [x] 5.2 CRUD услуг в админке
  - POST /api/admin/services
  - PUT /api/admin/services/{id}
  - DELETE /api/admin/services/{id} (is_active=False)
  - Валидация уникальности slug
  - _Требования: 8.6, 16.5_

- [x]* 5.3 Админ интерфейс услуг
  - AdminServicesScreen с таблицей
  - Формы создания/редактирования
  - Drag-and-drop для sort_order
  - _Требования: 8.6_

### 6. Checkpoint Фаза 1

- [x] 6.1 Проверка базового функционала
  - Миграции БД применяются
  - API endpoints работают
  - Flutter Web собирается и работает
  - Статические страницы отображаются
  - Задать вопросы при проблемах

## Фаза 2: Система курсов валют (1-2 недели)

### 7. Интеграция с API ЦБУ

- [x] 7.1 Создать CurrencyRatesService
  - backend/app/services/currency_rates.py
  - fetch_latest_rates() с httpx
  - Timeout 30 секунд
  - Парсинг JSON, маппинг на CurrencyRate
  - _Требования: 4.2_

- [x] 7.2 Логика расчёта изменений курсов
  - calculate_change() - разница с предыдущим днём
  - Обработка первой записи
  - get_rates_history(currency_code, days)
  - _Требования: 4.3_

- [ ]* 7.3 Unit тесты CurrencyRatesService
  - Тест fetch_latest_rates с моком httpx
  - Тест calculate_change
  - Тест обработки ошибок
  - _Требования: 20.1_

### 8. Celery и Redis

- [x] 8.1 Настроить Celery worker
  - celery_app.py
  - Redis как broker и result backend
  - tasks.py
  - Retry политика: max_retries=3, countdown=3600
  - _Требования: 4.5, 17.1_

- [x] 8.2 Задача update_currency_rates
  - @celery_app.task для обновления
  - Обработка ошибок, логирование
  - Идемпотентность
  - Инвалидация кеша
  - _Требования: 4.2, 4.4_

- [x] 8.3 Celery Beat расписание
  - beat_schedule: 09:00 Ташкент
  - docker-compose для celery-beat
  - docker-compose для celery-worker
  - _Требования: 4.1_

- [ ]* 8.4 Мониторинг Celery
  - Уведомление админа при провале
  - Логирование метрик
  - _Требования: 4.6, 22.4_

### 9. API курсов валют

- [x] 9.1 Endpoint виджета курсов
  - GET /api/currency-rates/widget (топ-5)
  - Кеш Redis TTL 1 час
  - Fallback на последние данные
  - Pydantic схема CurrencyRateResponse
  - _Требования: 4.7, 17.2_

- [x] 9.2 Endpoint истории курсов
  - GET /api/currency-rates/history?currency={code}&days={n}
  - Валидация параметров
  - Пагинация
  - _Требования: 4.8_

- [ ]* 9.3 Integration тесты currency rates API
  - Тест GET /widget с кешированием
  - Тест GET /history
  - Тест fallback поведения
  - _Требования: 20.6_

### 10. Frontend - виджет курсов

- [x] 10.1 Виджет курсов для главной
  - CurrencyRatesWidget
  - Отображение курса, изменения, даты
  - Auto-refresh каждые 10 минут
  - Адаптивный дизайн
  - _Требования: 4.7, 19.1_

- [x] 10.2 Страница истории курсов
  - ArchiveScreen с выбором валюты и дат
  - Таблица с детальными данными
  - _Требования: 4.8_

- [x]* 10.3 Обработка ошибок
  - Loading indicator
  - Сообщение об ошибке на русском
  - Retry кнопка
  - _Требования: 10.1, 17.2_

### 11. Checkpoint Фаза 2

- [x] 11.1 Проверка модуля курсов
  - Celery обновляет курсы из API ЦБУ
  - Виджет показывает актуальные данные
  - История показывает таблицу с данными
  - Кеширование Redis работает
  - _Завершено: 2026-08-26_



## Фаза 3: Движок калькулятора (2-3 недели)

### 12. Pricing Engine

- [ ] 12.1 Создать PricingEngine сервис
  - backend/app/services/pricing_engine.py
  - get_pricing_rules(service_id) с кешированием
  - Pydantic: EstimateRequest, EstimateResult, EstimateBreakdown
  - _Требования: 1.1, 1.2_

- [x] 12.2 Реализовать apply_linear_rule
  - addon = param_value × rate
  - Валидация положительных чисел
  - EstimateBreakdown с описанием
  - _Требования: 1.7_

- [x] 12.3 Реализовать apply_tiered_rule
  - Поиск диапазона (min <= value < max)
  - Обработка выхода за диапазоны
  - EstimateBreakdown с диапазоном
  - _Требования: 1.7, 1.8_

- [x] 12.4 Реализовать apply_flat_addon
  - Если param = true, addon = rate
  - Поддержка boolean, truthy values
  - EstimateBreakdown из rule.tiers
  - _Требования: 1.7_

- [x] 12.5 Реализовать calculate_estimate
  - Загрузить правила для service_id
  - Применить base_fee
  - Итерация по правилам
  - total = sum(breakdown[i].amount)
  - is_preliminary=True
  - _Требования: 1.1, 1.5_

- [ ]* 12.6 Property-based тесты
  - **Property 2: Сумма breakdown = total**
  - **Валидирует: Требования 1.4**
  - Hypothesis, 100+ случайных входов
  - _Требования: 20.4_

- [ ]* 12.7 Unit тесты правил
  - Тесты apply_linear_rule
  - Тесты apply_tiered_rule с граничными случаями
  - Тесты apply_flat_addon
  - Тесты calculate_estimate
  - _Требования: 20.1_

### 13. API калькулятора

- [x] 13.1 POST /api/calculator/estimate
  - Валидация EstimateRequest
  - Вызов pricing_engine.calculate_estimate()
  - Rate limiting: 20 req/min
  - Логирование запросов
  - _Требования: 1.1, 12.8_

- [x] 13.2 GET /api/calculator/params/{service_id}
  - Список обязательных параметров
  - Метаданные: тип, мин/макс, подсказки на русском
  - Для динамического построения формы
  - _Требования: 1.6, 13.1_

- [ ]* 13.3 Валидация параметров
  - Проверка обязательных полей
  - Проверка типов (положительные числа)
  - HTTP 422 с ошибками на русском
  - _Требования: 1.6, 10.1, 10.2_

- [ ]* 13.4 Integration тесты calculator API
  - POST /estimate с валидными параметрами
  - POST /estimate с невалидными (422)
  - Rate limiting (429 после 20)
  - _Требования: 20.6_

### 14. Frontend калькулятора

- [x] 14.1 CalcPage с выбором услуги
  - CalculatorScreen с dropdown
  - getServices()
  - Иконки услуг
  - _Требования: 1.1, 16.2_

- [x] 14.2 Динамическая форма параметров
  - ParamsFormWidget
  - Загрузка через GET /api/calculator/params/{service_id}
  - Генерация полей: TextField, Checkbox, Dropdown
  - Валидация на клиенте
  - _Требования: 1.6, 16.3_

- [x] 14.3 Расчёт и отображение результата
  - Кнопка "Рассчитать стоимость"
  - POST /api/calculator/estimate
  - Отображение total с форматированием
  - Loading indicator
  - Пометка "Предварительная стоимость"
  - _Требования: 1.1, 1.3, 13.7_

- [x] 14.4 Модальное окно детализации (breakdown)
  - BreakdownModal с таблицей
  - item_name, description, amount
  - Итоговая строка
  - Адаптивный дизайн
  - _Требования: 1.3, 19.4_

- [ ]* 14.5 Обработка ошибок и UX
  - Ошибки валидации рядом с полями
  - Debounce для пересчёта
  - Tooltips для сложных полей
  - _Требования: 10.1, 10.2_

### 15. Админ - правила ценообразования

- [x] 15.1 CRUD API pricing rules
  - POST /api/admin/pricing-rules
  - PUT /api/admin/pricing-rules/{id}
  - DELETE (is_active=False)
  - GET ?service_id={id}
  - _Требования: 8.3-8.5_

- [x] 15.2 Валидация правил
  - rate_type в ['linear', 'tiered', 'flat_addon']
  - Для tiered: массив с min, max, rate
  - Проверка непересечения диапазонов
  - HTTP 422 на русском
  - _Требования: 8.3, 8.4_

- [ ]* 15.3 Админ интерфейс правил
  - AdminPricingRulesScreen
  - Формы с выбором типа
  - Визуальный редактор tiered
  - Preview расчёта
  - _Требования: 8.3, 8.4_

### 16. Checkpoint Фаза 3

- [x] 16.1 Проверка калькулятора
  - Расчёты для разных комбинаций параметров
  - Детализация корректна, breakdown = total
  - Rate limiting работает (429)
  - Админ панель изменяет правила
  - Задать вопросы при проблемах

## Фаза 4: Аутентификация и заявки (2 недели)

### 17. Аутентификация JWT

- [x] 17.1 Хеширование паролей bcrypt
  - backend/app/core/security.py
  - hash_password() с passlib, bcrypt cost=12
  - verify_password()
  - _Требования: 7.3, 7.4, 12.4_

- [x] 17.2 Генерация JWT токенов
  - create_access_token() с python-jose
  - Срок жизни 24 часа
  - decode_access_token()
  - Dependency get_current_user()
  - _Требования: 7.6-7.8_

- [x] 17.3 API регистрации и входа
  - POST /api/auth/register (phone, password, full_name)
  - POST /api/auth/login (phone, password)
  - Валидация +998XXXXXXXXX, уникальность
  - Валидация пароля мин 8 символов
  - Возврат JWT
  - _Требования: 7.1, 7.2, 7.5_

- [ ]* 17.4 Unit тесты auth
  - hash_password (уникальность хешей)
  - verify_password
  - create/decode_access_token
  - Валидация телефона и пароля
  - _Требования: 20.1_

### 18. Order Management

- [x] 18.1 OrderManagement сервис
  - backend/app/services/order_management.py
  - create_order() на основе калькулятора
  - Статус awaiting_payment
  - Сохранение params, estimate_total в JSONB
  - _Требования: 2.1, 2.2_

- [x] 18.2 Машина состояний заявок
  - enum OrderStatus
  - validate_status_transition() с графом
  - update_order_status() с валидацией
  - Запись в OrderStatusHistory
  - _Требования: 2.3, 2.5, 15.1-15.7, 18.1_

- [x] 18.3 Логика deadline
  - calculate_deadline() с рабочими днями (2-5)
  - Автоустановка при paid
  - Исключение выходных
  - _Требования: 2.7, 15.8_

- [ ]* 18.4 Unit тесты OrderManagement
  - validate_status_transition разрешённые
  - validate_status_transition запрещённые (ошибка)
  - calculate_deadline с разными датами
  - _Требования: 20.1_

### 19. API заявок

- [x] 19.1 POST /api/orders/create
  - service_id, params, estimate_total от auth пользователя
  - order_management.create_order()
  - Возврат order_id, payment_url (заглушка)
  - Rate limiting: 5 req/min
  - _Требования: 2.1, 2.2, 12.8_

- [x] 19.2 GET /api/orders/my
  - Список заявок пользователя
  - Фильтр ?status=paid
  - Сортировка created_at DESC
  - Пагинация (offset, limit)
  - _Требования: 2.4, 11.2_

- [x] 19.3 GET /api/orders/{order_id}
  - Детали заявки
  - Проверка владельца (403)
  - История статусов
  - _Требования: 2.4, 5.3_

- [ ]* 19.4 Integration тесты orders API
  - Создание заявки auth пользователем
  - Создание без auth (401)
  - GET /my с фильтрацией
  - Доступ к чужой заявке (403)
  - _Требования: 20.6, 20.7_

### 20. Frontend - регистрация и кабинет

- [x] 20.1 Страницы регистрации и входа
  - RegisterScreen (телефон, пароль, имя)
  - LoginScreen (телефон, пароль)
  - Валидация на клиенте
  - POST /api/auth/register, /login
  - JWT в SharedPreferences
  - _Требования: 7.1, 7.2, 7.9_

- [x] 20.2 AuthProvider
  - ChangeNotifier
  - currentUser, isAuthenticated
  - login(), register(), logout()
  - Проверка токена при запуске
  - _Требования: 7.6, 7.8_

- [ ] 20.3 Личный кабинет
  - CabinetScreen с профилем
  - Вкладка "Мои заявки"
  - Фильтрация по статусу
  - Отображение: номер, услуга, сумма, статус, дата, deadline
  - _Требования: 2.4_

- [x] 20.4 Страница деталей заявки
  - OrderDetailScreen
  - Полная информация
  - Breakdown расчёта
  - История статусов с датами
  - Кнопка "Оплатить" для awaiting_payment
  - _Требования: 2.4, 2.5_

- [ ]* 20.5 Защита роутов
  - AuthGuard для кабинета
  - При 401 → страница входа
  - Уведомление "Сессия истекла"
  - _Требования: 7.8, 10.1_

### 21. Checkpoint Фаза 4

- [~] 21.1 Проверка auth и заявок
  - Регистрация пользователя
  - Вход корректный/некорректный
  - Создание заявки, отображение в кабинете
  - Фильтрация и пагинация
  - Изоляция чужих заявок
  - Задать вопросы при проблемах



## Фаза 5: Платёжные системы (2-3 недели)

### 22. Payme Integration

- [ ] 22.1 PaymeIntegration сервис
  - backend/app/services/payment/payme_integration.py
  - create_payment() через Payme API
  - merchant_id, secret_key из env
  - Возврат payment URL
  - _Требования: 3.1, 12.4_

- [ ] 22.2 compute_payme_signature()
  - HMAC-SHA256
  - verify_webhook_signature() с X-Payme-Signature
  - Логирование security incident
  - _Требования: 3.2, 3.3, 12.2_

- [ ] 22.3 Webhook POST /api/webhooks/payme
  - Прием payload, signature
  - verify_webhook_signature()
  - Парсинг transaction_id, order_id, amount, status
  - handle_payment_webhook()
  - Возврат {"result": "ok"} или 401
  - _Требования: 3.2, 3.3_

- [ ]* 22.4 Unit тесты Payme
  - compute_payme_signature
  - verify_webhook_signature валидная/невалидная
  - Мок create_payment
  - _Требования: 20.1_

### 23. Click Integration

- [ ] 23.1 ClickIntegration сервис
  - backend/app/services/payment/click_integration.py
  - create_payment()
  - merchant_id, secret_key из env
  - Возврат payment URL
  - _Требования: 3.1_

- [ ] 23.2 compute_click_signature() и webhook
  - Алгоритм проверки Click (MD5/другой)
  - POST /api/webhooks/click
  - _Требования: 3.2, 3.3_

- [ ]* 23.3 Unit тесты Click
  - Аналогично Payme
  - _Требования: 20.1_

### 24. PaymentIntegration фасад

- [ ] 24.1 Унифицированный PaymentIntegration
  - backend/app/services/payment/payment_integration.py
  - create_payment(provider) выбор Payme/Click
  - handle_webhook(provider, payload, signature) с идемпотентностью
  - Создание Payment в БД
  - _Требования: 3.1, 3.4, 3.6, 3.9_

- [ ] 24.2 Идемпотентность webhook
  - Проверка Payment по external_id
  - Если существует с тем же статусом → возврат без изменений
  - SELECT FOR UPDATE против race conditions
  - _Требования: 3.6_

- [ ] 24.3 Обновление статуса заявки при оплате
  - status='success' → update_order_status(order_id, 'paid')
  - Атомарность Payment + Order в одной транзакции
  - status='failed' → awaiting_payment
  - Логирование webhook_data
  - _Требования: 3.4, 3.8, 14.1-14.4_

- [ ]* 24.4 Property-based тесты идемпотентности
  - **Property 3: Идемпотентность webhook**
  - **Валидирует: Требования 3.6**
  - Повтор webhook не создаёт дубликаты
  - _Требования: 20.5_

- [ ]* 24.5 Integration тесты payment flow
  - Полный флоу: заявка → платёж → webhook success → paid
  - webhook failed → awaiting_payment
  - Невалидная подпись → 401, security incident
  - _Требования: 20.6, 20.7_

### 25. Уведомления

- [ ] 25.1 NotificationService
  - backend/app/services/notification_service.py
  - send_sms() с SMS gateway (playmobile.uz)
  - send_email() SMTP/email API
  - Retry: 3 попытки, интервал 5 минут (Celery)
  - _Требования: 9.5, 17.5_

- [ ] 25.2 Шаблоны уведомлений на русском
  - Подтверждение оплаты (SMS + email)
  - Провал оплаты с ссылкой (SMS + email)
  - Готовность документа (SMS + email)
  - Уведомление сотрудникам о новой paid заявке
  - _Требования: 9.1-9.4, 9.6, 13.3_

- [ ] 25.3 Интеграция уведомлений в lifecycle
  - paid → уведомления клиенту и сотрудникам
  - ready → уведомление о готовности документа
  - Провал оплаты → уведомление с ссылкой
  - Логирование попыток
  - _Требования: 3.5, 9.1-9.4_

- [ ]* 25.4 Мониторинг отказов уведомлений
  - Уведомление админа при провале SMS
  - Логирование ошибок SMS gateway
  - _Требования: 9.5, 17.6_

### 26. Frontend - оплата

- [ ] 26.1 Выбор способа оплаты
  - PaymentMethodSelector: Payme или Click
  - Логотипы систем
  - Поддерживаемые карты (Uzcard, Humo, Visa, MC)
  - _Требования: 3.1_

- [ ] 26.2 Создание платежа и редирект
  - Кнопка "Оплатить" → POST /api/payments/create
  - Получение payment_url
  - Редирект на hosted checkout
  - _Требования: 3.1_

- [ ] 26.3 Обработка возврата после оплаты
  - CallbackScreen для редиректа
  - Loading во время проверки статуса
  - Успех: "Оплата успешна", обновление статуса
  - Провал: ошибка, кнопка "Попробовать снова"
  - _Требования: 3.4, 3.7, 9.3_

- [ ]* 26.4 История платежей
  - Список попыток на странице заявки
  - Дата, сумма, статус, система
  - _Требования: 3.8_

### 27. Checkpoint Фаза 5

- [ ] 27.1 Проверка платёжной интеграции
  - Создание платежа Payme/Click (sandbox)
  - Обработка webhook при успехе
  - Обновление статуса paid
  - Отправка уведомлений
  - Обработка провала оплаты
  - Задать вопросы при проблемах

## Фаза 6: Карта и документы (1-2 недели)

### 28. Интерактивная карта

- [ ] 28.1 Подготовить GeoJSON
  - GeoJSON регионов Узбекистана
  - Детальный GeoJSON районов Ташкента
  - Метаданные: name_ru, region_id
  - Сохранение в backend/static/geojson/
  - _Требования: 6.1_

- [ ] 28.2 API для GeoJSON
  - GET /api/map/regions - все регионы
  - GET /api/map/regions/{region_id}/districts - районы
  - Кеш Redis (статичные данные)
  - _Требования: 6.7_

- [ ] 28.3 MapScreen в Flutter
  - flutter_map или custom canvas
  - Рендеринг GeoJSON полигонов
  - Hover: подсветка, название на русском
  - Обработка клика
  - _Требования: 6.1, 6.2, 19.6_

- [ ] 28.4 Детализация Ташкента
  - Клик "Ташкент" → загрузка районов
  - Рендеринг районов
  - Клик другой регион → калькулятор с region
  - Клик район Ташкента → калькулятор с region + district
  - _Требования: 6.3-6.5_

- [ ]* 28.5 Оптимизация карты
  - Lazy loading GeoJSON
  - Debounce hover
  - Упрощение геометрии
  - _Требования: 6.7_

### 29. S3 документы

- [ ] 29.1 Настроить S3 клиент
  - backend/app/core/s3_client.py
  - boto3 с endpoint_url, access_key, secret_key из env
  - Приватный bucket (без публичного доступа)
  - _Требования: 5.1, 12.6_

- [ ] 29.2 upload_document() в OrderManagement
  - Прием file (PDF), order_id
  - UUID имя файла
  - Загрузка s3://bucket/documents/{order_id}/{uuid}.pdf
  - Сохранение order.document_url
  - Обновление статуса ready
  - Атомарность: rollback при провале S3
  - _Требования: 5.1, 5.2, 12.5_

- [ ] 29.3 generate_presigned_url()
  - Временная signed URL (1 час)
  - boto3 generate_presigned_url()
  - _Требования: 5.6, 5.7_

- [ ] 29.4 API документов
  - POST /api/admin/orders/{order_id}/document - загрузка админом
  - GET /api/orders/{order_id}/document - signed URL клиенту
  - Проверка владельца (403)
  - Проверка статуса ready/delivered (400)
  - Логирование обращений
  - _Требования: 5.3-5.5, 18.5_

- [ ]* 29.5 Integration тесты S3
  - Загрузка документа админом
  - Генерация signed URL владельцем
  - Доступ к чужому документу (403)
  - Доступ до ready (400)
  - _Требования: 20.6_

### 30. Админ - заявки

- [ ] 30.1 API админа для заявок
  - GET /api/admin/orders - все заявки с фильтрами, пагинацией
  - Фильтры: status, date_from, date_to, user_id, service_id
  - PUT /api/admin/orders/{order_id}/status - изменение статуса
  - Валидация через validate_status_transition()
  - _Требования: 8.7, 15.1-15.7_

- [ ] 30.2 Загрузка документов в админке
  - POST /api/admin/orders/{order_id}/document multipart/form-data
  - Валидация: только PDF, макс 50 МБ
  - order_management.upload_document()
  - Автостатус ready
  - _Требования: 5.1, 5.2, 8.8_

- [ ]* 30.3 Админ интерфейс заявок
  - AdminOrdersScreen с таблицей
  - Фильтры по статусу, дате, услуге
  - Форма изменения статуса с комментарием
  - Форма загрузки PDF
  - История статусов
  - _Требования: 8.7, 8.8_

### 31. Финальная интеграция

- [ ] 31.1 Карта → калькулятор
  - Ссылка "Выбрать на карте" на главной
  - Выбор района → калькулятор с предзаполненными полями
  - Отображение выбранного района (неизменяемое)
  - _Требования: 6.4, 6.5_

- [ ]* 31.2 End-to-end тесты
  - Флоу 1: Карта → расчёт → заявка → оплата → документ
  - Флоу 2: Калькулятор → регистрация → заявка → оплата
  - Флоу 3: Админ загружает → уведомление → скачивание
  - _Требования: 20.6_

- [ ]* 31.3 Нагрузочное тестирование
  - 100 одновременных запросов к калькулятору
  - Запросы orders <1s для 1000 заявок
  - Rate limiting
  - _Требования: 11.1, 11.2, 11.7_

- [ ]* 31.4 Security тесты
  - SQL injection через parameterized queries
  - Валидация webhook подписей
  - Защита документов (чужие документы)
  - Rate limiting всех endpoints
  - _Требования: 12.1-12.3, 12.7, 12.8, 20.8_

### 32. Финальный Checkpoint

- [ ] 32.1 Проверка всей системы
  - Полный цикл: расчёт → документ
  - Карта + калькулятор
  - Загрузка/скачивание документов S3
  - Уведомления SMS/email
  - Админка: услуги, правила, заявки
  - Все критичные требования реализованы
  - Задать вопросы при проблемах

## Примечания

- Задачи с `*` опциональные (можно пропустить для быстрой MVP доставки)
- Каждая фаза завершается checkpoint для валидации
- Property-based тесты помечены свойством и валидируемыми требованиями
- Требования ссылаются на requirements.md номерами
- `git commit` после каждой фазы для сохранения прогресса
- Backend на Python согласно design.md








