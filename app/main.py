from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from datetime import datetime

from database import create_tables, delete_tables
from reagents.router_reagent import router as reagents_router
from storage.router_storage import router as storage_router
from exceptions import BusinessRuleException, NotFoundException
from examples_data import print_demo_instructions

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Старт приложения
    # await delete_tables()
    # print("🗑️ База данных очищена")
    await create_tables()
    print("🗄️ База данных создана")

    print_demo_instructions()
    
    yield
    
    # Завершение работы
    print("👋 Приложение завершает работу")

app = FastAPI(
    title="🧪 Chemical Reagents Inventory API",
    description="API для учёта химических реактивов в лаборатории",
    version="1.0.0",
    lifespan=lifespan
)


# Глобальная обработка ошибок
@app.exception_handler(BusinessRuleException)
async def business_rule_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"ok": False, "error": exc.detail}
    )

@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"ok": False, "error": exc.detail}
    )

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"ok": False, "error": str(exc)}
    )

# Подключаем роутеры
app.include_router(storage_router)
app.include_router(reagents_router)

@app.get("/")
async def root():
    return {
        "message": "🧪 Chemical Reagents Inventory API", 
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat()
    }