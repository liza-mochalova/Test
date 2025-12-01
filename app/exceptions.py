from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
from typing import Any, Optional

class BaseAPIException(HTTPException):
    """Базовое исключение для API"""
    def __init__(self, status_code: int, detail: str, error_code: Optional[str] = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code

class BusinessRuleException(BaseAPIException):
    """Нарушение бизнес-правил"""
    def __init__(self, detail: str, error_code: Optional[str] = None):
        super().__init__(status_code=400, detail=detail, error_code=error_code)

class NotFoundException(BaseAPIException):
    """Ресурс не найден"""
    def __init__(self, resource: str, resource_id: Any = None):
        detail = f"{resource} not found"
        if resource_id:
            detail = f"{resource} with id {resource_id} not found"
        super().__init__(status_code=404, detail=detail, error_code="NOT_FOUND")

class ValidationException(BaseAPIException):
    """Ошибка валидации данных"""
    def __init__(self, detail: str, error_code: Optional[str] = None):
        super().__init__(status_code=422, detail=detail, error_code=error_code)

async def base_api_exception_handler(request: Request, exc: BaseAPIException):
    """Обработчик для кастомных API исключений"""
    error_response = {
        "ok": False,
        "error": exc.detail,
        "error_code": exc.error_code or "UNKNOWN_ERROR",
        "path": request.url.path,
        "method": request.method
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Обработчик для стандартных HTTP исключений"""
    error_response = {
        "ok": False,
        "error": exc.detail,
        "error_code": "HTTP_ERROR",
        "path": request.url.path,
        "method": request.method
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик для ошибок валидации Pydantic"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error['loc'])
        errors.append({
            "field": field,
            "message": error['msg'],
            "type": error['type']
        })
    
    error_response = {
        "ok": False,
        "error": "Validation failed",
        "error_code": "VALIDATION_ERROR",
        "details": errors,
        "path": request.url.path,
        "method": request.method
    }
    
    return JSONResponse(
        status_code=422,
        content=error_response
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Обработчик для непредвиденных исключений"""
    error_response = {
        "ok": False,
        "error": "Internal server error",
        "error_code": "INTERNAL_SERVER_ERROR", 
        "path": request.url.path,
        "method": request.method
    }
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )


def setup_exception_handlers(app):
    """Настройка обработчиков исключений для приложения"""
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)