"""
Authentication API - регистрация и вход пользователей
Требования: 7.1, 7.2, 7.5
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field, field_validator
from app.db.database import get_db
from app.models.user import User, UserRole
from app.core.security import hash_password, verify_password, create_access_token
import re


router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Pydantic модели для request/response
class RegisterRequest(BaseModel):
    """Запрос регистрации"""
    phone: str = Field(..., description="Номер телефона в формате +998XXXXXXXXX")
    password: str = Field(..., min_length=8, description="Пароль минимум 8 символов")
    full_name: str = Field(..., min_length=1, description="Полное имя")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Валидация формата телефона: +998XXXXXXXXX"""
        pattern = r'^\+998\d{9}$'
        if not re.match(pattern, v):
            raise ValueError('Номер телефона должен быть в формате +998XXXXXXXXX')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Валидация пароля: минимум 8 символов"""
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        return v


class LoginRequest(BaseModel):
    """Запрос входа"""
    phone: str = Field(..., description="Номер телефона")
    password: str = Field(..., description="Пароль")


class AuthResponse(BaseModel):
    """Ответ с токеном"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    full_name: str
    phone: str
    role: str


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя"
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя
    
    **Требование 7.1**: КОГДА клиент регистрируется, ТОГДА Система ДОЛЖНА принять 
    номер телефона в формате +998XXXXXXXXX и проверить его уникальность
    
    **Требование 7.2**: КОГДА клиент создаёт пароль, ТОГДА Система ДОЛЖНА принять 
    пароль длиной минимум 8 символов
    
    **Требование 7.9**: КОГДА клиент регистрируется, ТОГДА Система ДОЛЖНА требовать 
    заполнения поля "Полное имя"
    
    Параметры:
    - **phone**: Номер телефона в формате +998XXXXXXXXX
    - **password**: Пароль минимум 8 символов
    - **full_name**: Полное имя пользователя
    
    Возвращает JWT токен с временем жизни 24 часа
    """
    # Проверка уникальности номера телефона
    # Требование 7.1: проверить уникальность номера телефона
    query = select(User).where(User.phone == data.phone)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким номером телефона уже зарегистрирован"
        )
    
    # Хеширование пароля
    # Требование 7.3: хешировать пароль с использованием bcrypt с cost factor 12
    password_hash = hash_password(data.password)
    
    # Создание пользователя
    new_user = User(
        phone=data.phone,
        password_hash=password_hash,
        full_name=data.full_name,
        role=UserRole.CLIENT,
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Создание JWT токена
    # Требование 7.6: КОГДА аутентификация успешна, ТОГДА Система ДОЛЖНА выдать 
    # JWT токен с временем жизни 24 часа
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user.id,
        full_name=new_user.full_name,
        phone=new_user.phone,
        role=new_user.role.value
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Вход в систему"
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход в систему
    
    **Требование 7.5**: КОГДА клиент входит в систему, ТОГДА Система ДОЛЖНА 
    проверить соответствие введённого пароля сохранённому хешу
    
    **Требование 7.6**: КОГДА аутентификация успешна, ТОГДА Система ДОЛЖНА 
    выдать JWT токен с временем жизни 24 часа
    
    Параметры:
    - **phone**: Номер телефона
    - **password**: Пароль
    
    Возвращает JWT токен с временем жизни 24 часа
    """
    # Поиск пользователя по номеру телефона
    query = select(User).where(User.phone == data.phone)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    # Проверка существования пользователя и соответствия пароля
    # Требование 7.5: проверить соответствие введённого пароля сохранённому хешу
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный номер телефона или пароль"
        )
    
    # Проверка активности пользователя
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Учётная запись деактивирована"
        )
    
    # Создание JWT токена
    # Требование 7.6: выдать JWT токен с временем жизни 24 часа
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role.value
    )
