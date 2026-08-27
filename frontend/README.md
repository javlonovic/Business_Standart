# Business Standart Frontend

Flutter Web приложение для оценочной компании Business Standart.

## Технологии

- **Flutter 3.16+** (Web)
- **Provider** - state management
- **HTTP** - API клиент
- **URL Launcher** - открытие ссылок

## Установка и запуск

```bash
cd frontend

# Установить зависимости
flutter pub get

# Запустить в режиме разработки
flutter run -d chrome --web-port 8080

# Собрать production build
flutter build web --release
```

## Структура проекта

```
frontend/
├── lib/
│   ├── core/         # Тема, константы
│   ├── models/       # Data models
│   ├── providers/    # State management
│   ├── screens/      # UI screens
│   ├── services/     # API service
│   ├── widgets/      # Reusable widgets
│   └── main.dart
├── web/              # Web-specific files
└── pubspec.yaml
```

## Конфигурация API

По умолчанию API endpoint: `http://localhost:8000/api`

Для изменения отредактируйте `lib/services/api_service.dart`:

```dart
final String baseUrl = 'http://your-backend-url/api';
```

## Дизайн

Приложение использует **Cozy Minimalist** дизайн:
- Тёплая палитра (бежевый/кремовый фон)
- Мягкие тени и скругления (12-20px)
- Спокойная типографика
- Много воздуха (щедрые отступы)

## Разработка

### Добавить новую страницу

1. Создать файл в `lib/screens/`
2. Добавить роут в `main.dart`
3. Добавить навигацию в `AppBarWidget`

### Добавить новый API endpoint

1. Добавить метод в `lib/services/api_service.dart`
2. Обновить модели в `lib/models/`
3. Использовать в Provider или Screen

## Тестирование

```bash
# Unit тесты
flutter test

# Integration тесты
flutter test integration_test
```

## Production Build

```bash
# Собрать web build
flutter build web --release

# Файлы будут в build/web/
# Деплой на статический хостинг (Nginx, Vercel, Netlify, etc.)
```
