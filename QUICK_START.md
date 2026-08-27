# ⚡ Quick Start - Business Standart Platform

**Get the platform running in under 5 minutes!**

---

## 🚀 Super Quick Start (Docker)

```bash
# 1. Start all services
docker-compose up -d

# 2. Apply database migrations
docker-compose exec backend alembic upgrade head

# 3. Open another terminal and start frontend
cd frontend
flutter pub get
flutter run -d chrome --web-port 8080

# 4. Open in browser
# Frontend: http://localhost:8080
# API Docs: http://localhost:8000/docs
```

---

## 🎯 Even Easier - Use Script

### Linux/macOS:
```bash
./test-local.sh
```

### Windows:
```cmd
test-local.bat
```

The script will:
- ✅ Check prerequisites
- ✅ Start Docker services
- ✅ Apply migrations
- ✅ Start frontend
- ✅ Open browser automatically

---

## 📱 Test Flow (5 minutes)

1. **Register** → http://localhost:8080/register
   - Phone: +998901234567
   - Password: test123
   - Name: Test User

2. **Calculator** → http://localhost:8080/calculator
   - Select service
   - Enter parameters
   - Calculate estimate

3. **Create Order** → Click "Создать заявку"

4. **Payment** → Click "Оплатить"
   - Select provider (Payme or Click)
   - Choose "Успех" in test dialog

5. **Cabinet** → View order with "Оплачено" status

---

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:8080 |
| **Backend API** | http://localhost:8000 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/health |

---

## 🛠️ Useful Commands

```bash
# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Restart services
docker-compose restart

# Reset database (⚠️ deletes data)
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

---

## 📚 Full Documentation

- **Detailed Testing**: [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md)
- **Getting Started**: [START_HERE.md](START_HERE.md)
- **Production Deploy**: [PRODUCTION_STATUS_FINAL.md](PRODUCTION_STATUS_FINAL.md)

---

## 🆘 Common Issues

**Backend won't start:**
```bash
docker-compose logs backend
```

**Frontend build error:**
```bash
cd frontend
flutter clean
flutter pub get
```

**CORS error:**
Check `backend/.env` has:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

---

## ✅ Success Check

Platform is working if you can:
- ✅ Visit http://localhost:8080
- ✅ See API docs at http://localhost:8000/docs
- ✅ Register and login
- ✅ Use calculator
- ✅ Create and pay for order

---

**That's it! You're ready to test!** 🎉

For more details, see [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md)
