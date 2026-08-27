@echo off
REM Business Standart Platform - Local Testing Script (Windows)
REM This script helps you quickly start and test the platform locally

echo.
echo ========================================
echo Business Standart Platform - Local Testing
echo ========================================
echo.

REM Check Docker
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not installed
    echo Please install Docker Desktop from: https://www.docker.com/get-started
    pause
    exit /b 1
)
echo [OK] Docker is installed

REM Check Docker Compose
where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker Compose is not installed
    pause
    exit /b 1
)
echo [OK] Docker Compose is installed

REM Check Flutter
where flutter >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Flutter is not installed (needed for frontend)
    echo You can still test the backend API
    echo Install Flutter from: https://docs.flutter.dev/get-started/install
    set SKIP_FRONTEND=true
) else (
    echo [OK] Flutter is installed
)

echo.
echo ========================================
echo.

REM Start backend services
echo [INFO] Starting backend services with Docker...
echo.

REM Stop any existing containers
docker-compose down >nul 2>nul

REM Start services
echo [INFO] Starting PostgreSQL, Redis, Backend, Celery...
docker-compose up -d

echo.
echo [INFO] Waiting for services to be ready (15 seconds)...
timeout /t 15 /nobreak >nul

REM Check if services are running
echo.
echo [INFO] Checking service status...
docker-compose ps

echo.
echo ========================================
echo.

REM Apply migrations
echo [INFO] Applying database migrations...
docker-compose exec -T backend alembic upgrade head

if %ERRORLEVEL% EQU 0 (
    echo [OK] Database migrations applied
) else (
    echo [ERROR] Migration failed
    echo Try running manually: docker-compose exec backend alembic upgrade head
    pause
    exit /b 1
)

echo.
echo ========================================
echo.

REM Test backend
echo [INFO] Testing backend API...
timeout /t 2 /nobreak >nul

curl -s http://localhost:8000/health
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend API is responding
) else (
    echo [WARNING] Backend API is not responding yet
    echo Waiting 5 more seconds...
    timeout /t 5 /nobreak >nul
)

echo.
echo ========================================
echo.

REM Start frontend if Flutter is available
if NOT "%SKIP_FRONTEND%"=="true" (
    echo [INFO] Starting Flutter frontend...
    echo.
    
    cd frontend
    
    REM Check if dependencies are installed
    if not exist ".dart_tool" (
        echo [INFO] Installing Flutter dependencies (first time)...
        flutter pub get
    )
    
    echo [INFO] Building and starting Flutter web app...
    echo This may take 1-2 minutes on first run...
    echo.
    
    REM Start Flutter
    start "Flutter Web" cmd /c "flutter run -d chrome --web-port 8080"
    
    cd ..
    
    echo.
    echo [OK] Frontend is starting in a new window...
) else (
    echo [INFO] Skipping frontend (Flutter not installed)
)

echo.
echo ========================================
echo.
echo Platform is ready for testing!
echo.
echo Access URLs:
echo   - Frontend:       http://localhost:8080
echo   - Backend API:    http://localhost:8000
echo   - API Docs:       http://localhost:8000/docs
echo   - Health Check:   http://localhost:8000/health
echo.
echo Test the platform:
echo   1. Open http://localhost:8080 in your browser
echo   2. Register a new user (click 'Регистрация')
echo   3. Go to Calculator and create an estimate
echo   4. Create an order from the estimate
echo   5. Test the payment flow (simulation)
echo.
echo Useful commands:
echo   - View logs:      docker-compose logs -f
echo   - Stop services:  docker-compose down
echo   - Restart:        docker-compose restart
echo.
echo For detailed testing guide, see: LOCAL_TESTING_GUIDE.md
echo.
echo ========================================
echo.

REM Open browser automatically
timeout /t 3 /nobreak >nul
start http://localhost:8000/docs
timeout /t 2 /nobreak >nul
if NOT "%SKIP_FRONTEND%"=="true" (
    start http://localhost:8080
)

echo.
echo Press any key to stop all services...
pause >nul

echo.
echo [INFO] Stopping services...
docker-compose down

echo [OK] All services stopped
echo.
pause
