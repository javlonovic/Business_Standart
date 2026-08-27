"""
Главный файл приложения FastAPI
Веб-платформа Business Standart - Оценочная компания
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.core.exceptions import validation_exception_handler, general_exception_handler
from app.api import services, content, admin
from app.api import currency_rates, calculator, auth, orders

app = FastAPI(
    title="Business Standart API",
    description="API для веб-платформы оценочной компании Business Standart",
    version="1.0.0"
)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(services.router)
app.include_router(content.router)
app.include_router(admin.router)
app.include_router(currency_rates.router)
app.include_router(calculator.router)
app.include_router(auth.router)
app.include_router(orders.router)


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Business Standart API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint для мониторинга"""
    from app.db.database import engine
    
    try:
        # Check database connection
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "business-standart-api",
        "database": db_status
    }
