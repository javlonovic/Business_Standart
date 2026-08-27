# 🧪 Local Testing Guide - Business Standart Platform

**Complete step-by-step guide to test the platform on your local machine**

---

## 📋 Prerequisites Check

Before starting, make sure you have:
- ✅ Python 3.11+ installed
- ✅ Flutter 3.16+ installed
- ✅ Docker Desktop installed (optional but recommended)
- ✅ Git installed

### Quick Check
```bash
# Check Python
python --version  # or python3 --version

# Check Flutter
flutter --version

# Check Docker
docker --version
docker-compose --version

# Check Git
git --version
```

---

## 🚀 Method 1: Quick Start with Docker (Recommended)

This is the easiest way - Docker will handle PostgreSQL, Redis, and all backend services.

### Step 1: Start Backend Services

```bash
# Navigate to project root
cd business-standart-website

# Start all backend services (PostgreSQL, Redis, API, Celery)
docker-compose up -d

# Wait 10-15 seconds for services to start

# Check if services are running
docker-compose ps

# Expected output:
# business_standart_backend         running
# business_standart_db              running  
# business_standart_redis           running
# business_standart_celery_worker   running
# business_standart_celery_beat     running
```

### Step 2: Apply Database Migrations

```bash
# Enter backend container
docker-compose exec backend bash

# Apply migrations
alembic upgrade head

# Exit container
exit

# Or run directly without entering container
docker-compose exec backend alembic upgrade head
```

### Step 3: Verify Backend is Running

Open your browser and visit:
- **API Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **API Root**: http://localhost:8000

You should see:
- Health check returns: `{"status":"healthy","service":"business-standart-api","database":"healthy"}`
- Swagger UI with all API endpoints

### Step 4: Start Frontend

```bash
# Open a new terminal window
cd frontend

# Install dependencies (first time only)
flutter pub get

# Run Flutter web app
flutter run -d chrome --web-port 8080

# Wait for compilation (~1-2 minutes first time)
```

### Step 5: Access the Platform

Once Flutter finishes compiling, it will automatically open:
- **Frontend**: http://localhost:8080

---

## 🔧 Method 2: Manual Setup (Without Docker)

If you prefer to run services manually or don't have Docker.

### Step 1: Start PostgreSQL

**Option A: Local PostgreSQL Installation**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-15
sudo systemctl start postgresql

# macOS (using Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Windows
# Download and install from: https://www.postgresql.org/download/windows/
```

**Option B: Docker for PostgreSQL only**
```bash
docker run -d \
  --name business_standart_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=business_standart \
  -p 5432:5432 \
  postgres:15-alpine
```

### Step 2: Start Redis

**Option A: Local Redis Installation**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS (using Homebrew)
brew install redis
brew services start redis

# Windows
# Download from: https://github.com/tporadowski/redis/releases
```

**Option B: Docker for Redis only**
```bash
docker run -d \
  --name business_standart_redis \
  -p 6379:6379 \
  redis:7-alpine
```

### Step 3: Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install poetry
poetry install

# Create .env file
cp .env.example .env

# Edit .env to match your setup
nano .env  # or use any text editor
```

**Minimum .env configuration:**
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/business_standart
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Step 4: Apply Migrations

```bash
# Still in backend directory with venv activated
poetry run alembic upgrade head
```

### Step 5: Start Backend Services

**Terminal 1 - API Server:**
```bash
cd backend
source venv/bin/activate  # if not already activated
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
source venv/bin/activate
poetry run celery -A app.celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat:**
```bash
cd backend
source venv/bin/activate
poetry run celery -A app.celery_app beat --loglevel=info
```

### Step 6: Start Frontend

**Terminal 4 - Flutter:**
```bash
cd frontend
flutter pub get
flutter run -d chrome --web-port 8080
```

---

## 🧪 Complete Testing Flow

Once everything is running, follow this complete test flow:

### Test 1: Browse Static Pages

1. Open http://localhost:8080
2. You should see the **homepage** with:
   - Navigation bar (Home, About, Services, Contacts, Calculator)
   - Service cards
   - Currency rates widget
   - Footer

3. Click through pages:
   - **About**: http://localhost:8080/about
   - **Services**: http://localhost:8080/services
   - **Contacts**: http://localhost:8080/contacts

### Test 2: Currency Rates

1. On homepage, check the **currency rates widget**
   - Should show: USD, EUR, RUB, GBP, CNY
   - Each with rate and change indicator

2. Visit **Archive**: http://localhost:8080/currency-archive
   - Select currency from dropdown
   - View historical data

### Test 3: Calculator

1. Navigate to **Calculator**: http://localhost:8080/calculator
2. Select a service from dropdown (e.g., "Оценка квартиры")
3. Fill in parameters (e.g., area: 100, floors: 5)
4. Click **"Рассчитать стоимость"**
5. View the estimate with total amount
6. Click **"Посмотреть детализацию"** to see breakdown

### Test 4: User Registration

1. Click **"Регистрация"** in navigation bar
2. Fill in form:
   - **Phone**: +998901234567
   - **Password**: testpass123
   - **Confirm Password**: testpass123
   - **Full Name**: Test User
3. Click **"Зарегистрироваться"**
4. You should be redirected to **Cabinet**

### Test 5: User Login

1. Logout (if logged in)
2. Click **"Войти"** in navigation bar
3. Enter credentials:
   - **Phone**: +998901234567
   - **Password**: testpass123
4. Click **"Войти"**
5. You should be redirected to **Cabinet**

### Test 6: Create Order from Calculator

1. Make sure you're **logged in**
2. Go to **Calculator**: http://localhost:8080/calculator
3. Select service and calculate estimate
4. Click **"Создать заявку"**
5. You should be redirected to **Order Details** page
6. Verify order information is displayed

### Test 7: View Orders in Cabinet

1. Click your name in navigation bar or go to http://localhost:8080/cabinet
2. You should see **"Мои заявки"** tab
3. Your newly created order should appear
4. Try filtering by status (use filter chips)
5. Click on an order to view details

### Test 8: Payment Flow (Test Simulation)

1. From **Order Details**, if status is "Ожидает оплаты"
2. Click **"Оплатить"** button
3. **Payment Screen** opens
4. Select payment provider:
   - **Payme** (Uzcard, Humo, Visa, MC)
   - **Click** (Uzcard, Humo)
5. Click **"Оплатить"**
6. **Test Dialog** appears with options:
   - Click **"Успех"** to simulate successful payment
   - Click **"Провал"** to simulate failed payment
7. If you clicked "Успех":
   - Success dialog appears
   - Click **"Вернуться к заявке"**
   - Order status changes to **"Оплачено"** (paid)
8. Verify status changed in **Cabinet**

### Test 9: Multiple Orders

1. Create 2-3 more orders with different services
2. Test different payment outcomes (success/failure)
3. View all orders in cabinet
4. Filter by status
5. Check order details for each

### Test 10: API Testing (Advanced)

Open **Swagger UI**: http://localhost:8000/docs

**Test Authentication:**
```
1. Expand "auth" section
2. POST /api/auth/register - Try registering another user
3. POST /api/auth/login - Get JWT token
4. Click "Authorize" button at top
5. Enter: Bearer <your-token>
6. Now you can test authenticated endpoints
```

**Test Calculator:**
```
1. Expand "calculator" section
2. GET /api/calculator/params/1 - Get parameters for service 1
3. POST /api/calculator/estimate - Calculate estimate
```

**Test Orders:**
```
1. Make sure you're authorized (see auth above)
2. GET /api/orders/my - List your orders
3. GET /api/orders/{order_id} - Get specific order
4. POST /api/orders/create - Create new order
```

**Test Payments:**
```
1. Make sure you're authorized
2. POST /api/payments/create - Create payment for order
3. GET /api/payments/order/{order_id} - View payment history
4. GET /api/payments/stub/simulate-success/{external_id} - Simulate payment
```

---

## 🔍 Verification Checklist

Go through this checklist to ensure everything works:

### Backend
- [ ] Health check returns healthy
- [ ] Swagger UI loads at /docs
- [ ] Can register new user via API
- [ ] Can login and receive JWT token
- [ ] Calculator endpoints work
- [ ] Orders endpoints require authentication
- [ ] Payments endpoints work

### Frontend
- [ ] Homepage loads
- [ ] Static pages load (About, Services, Contacts)
- [ ] Currency rates widget displays
- [ ] Calculator works
- [ ] Registration form works
- [ ] Login form works
- [ ] Cabinet displays orders
- [ ] Order details page works
- [ ] Payment screen works

### Integration
- [ ] Creating order from calculator works
- [ ] Order appears in cabinet immediately
- [ ] Payment updates order status
- [ ] Navigation between screens works
- [ ] Session persists after page reload

### Background Tasks
- [ ] Celery worker is running (check logs)
- [ ] Celery beat is running (check logs)
- [ ] Currency rates update (check at 09:00 Tashkent time, or manually trigger)

---

## 🐛 Troubleshooting

### Backend won't start

**Error: "Database connection failed"**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres
# or
sudo systemctl status postgresql

# Check connection
psql -h localhost -U postgres -d business_standart
# Password: postgres
```

**Error: "Redis connection failed"**
```bash
# Check if Redis is running
docker ps | grep redis
# or
sudo systemctl status redis

# Test connection
redis-cli ping
# Should return: PONG
```

**Error: "ModuleNotFoundError"**
```bash
# Reinstall dependencies
cd backend
poetry install
```

### Frontend won't start

**Error: "Unable to find Chrome"**
```bash
# List available devices
flutter devices

# Run on a specific device
flutter run -d <device-id>

# Or run on web-server mode
flutter run -d web-server --web-port 8080
# Then open manually: http://localhost:8080
```

**Error: "flutter: command not found"**
```bash
# Check Flutter installation
which flutter

# If not found, install Flutter:
# https://docs.flutter.dev/get-started/install
```

### Database Issues

**Reset database (⚠️ deletes all data)**
```bash
# With Docker
docker-compose down -v
docker-compose up -d postgres redis
docker-compose exec backend alembic upgrade head

# Without Docker
dropdb -U postgres business_standart
createdb -U postgres business_standart
cd backend
poetry run alembic upgrade head
```

### CORS Errors

If you see CORS errors in browser console:

1. Check backend `.env` file:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

2. Make sure frontend URL matches CORS_ORIGINS

3. Restart backend:
```bash
docker-compose restart backend
# or
# Ctrl+C and restart uvicorn
```

### Payment Not Working

**Error: "Требуется авторизация"**
- Make sure you're logged in
- Check if JWT token is valid (try logging out and in again)

**Payment doesn't update order status**
- Check backend logs for errors
- Check if Celery worker is running
- Try creating payment again

---

## 📊 Monitoring Logs

### View Docker Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat

# Last 100 lines
docker-compose logs --tail=100 backend
```

### View Manual Setup Logs

Logs appear in the terminal where you started each service:
- **Terminal 1**: uvicorn logs (API requests)
- **Terminal 2**: Celery worker logs (background tasks)
- **Terminal 3**: Celery beat logs (scheduled tasks)
- **Terminal 4**: Flutter logs (frontend)

---

## 🎥 Quick Video Tutorial (Steps)

If you want to record yourself testing:

1. **Start recording**
2. **Show terminal**: `docker-compose up -d`
3. **Show browser**: Open http://localhost:8000/docs
4. **Show browser**: Open http://localhost:8080
5. **Register user**: Full registration flow
6. **Calculator**: Calculate an estimate
7. **Create order**: From calculator
8. **Payment**: Complete payment flow
9. **Cabinet**: Show order with "paid" status

---

## 🚀 Next: Deploy to a Server

Once local testing is complete and everything works, you can:

1. **Deploy to a VPS** (DigitalOcean, Linode, AWS EC2)
2. **Use managed services** (Render, Railway, Heroku)
3. **Deploy frontend to** (Vercel, Netlify, Cloudflare Pages)

See [PRODUCTION_STATUS_FINAL.md](PRODUCTION_STATUS_FINAL.md) for deployment guide.

---

## ✅ Success Criteria

You've successfully tested the platform if:

- ✅ You can register and login
- ✅ You can browse all pages
- ✅ Calculator works and shows estimates
- ✅ You can create orders
- ✅ Orders appear in cabinet
- ✅ Payment simulation works
- ✅ Order status updates after payment
- ✅ Currency rates are visible

**Congratulations! Your platform is working perfectly!** 🎉

---

## 📞 Need Help?

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review [START_HERE.md](START_HERE.md)
3. Check backend logs for errors
4. Verify all services are running
5. Try resetting the database (last resort)

---

**Happy Testing!** 🧪
