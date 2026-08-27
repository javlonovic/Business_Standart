"""
Custom exceptions and error handlers
"""
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


class NotFoundError(HTTPException):
    """Ресурс не найден"""
    def __init__(self, detail: str = "Ресурс не найден"):
        super().__init__(status_code=404, detail=detail)


class ValidationException(HTTPException):
    """Ошибка валидации"""
    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=detail)


class UnauthorizedException(HTTPException):
    """Не авторизован"""
    def __init__(self, detail: str = "Требуется авторизация"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenException(HTTPException):
    """Доступ запрещён"""
    def __init__(self, detail: str = "Доступ запрещён"):
        super().__init__(status_code=403, detail=detail)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации Pydantic"""
    errors = []
    for error in exc.errors():
        field = " -> ".join([str(loc) for loc in error["loc"]])
        message = error["msg"]
        errors.append({
            "поле": field,
            "ошибка": message
        })
    
    logger.warning(f"Ошибка валидации: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Ошибка валидации данных",
            "errors": errors
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Обработчик общих исключений"""
    logger.error(f"Необработанная ошибка: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Внутренняя ошибка сервера. Пожалуйста, попробуйте позже."
        }
    )
