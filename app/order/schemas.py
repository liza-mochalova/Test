
from datetime import date
from enum import Enum
import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from database import UnitType

class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class OrderStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OrderForUser(BaseModel):
    reagent_cas: str = Field(..., description="CAS-номер в формате XXXXX-XX-X")
    quantity: float = Field(..., gt=0, description="Количество")
    unit: UnitType = Field(..., description="Единица измерения")
    priority: Priority = Field(..., description="Приоритет задачи")
    
    @field_validator('reagent_cas')
    @classmethod
    def validate_reagent_cas(cls, v):
        pattern = r'^\d{4,5}-\d{2}-\d$'
        if not re.match(pattern, v):
            raise ValueError('CAS number must be in format: XXXXX-XX-X')
        return v
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError('Quantity cannot be negative')
        return v

class OrderResponse(OrderForUser):
    id: int 
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    create_date: date = Field(default=date.today)

    class Config:
        from_attributes = True

