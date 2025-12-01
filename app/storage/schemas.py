from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, field_validator, Field
from enum import Enum

class StorageType(str, Enum):
    CABINET = "cabinet"
    REFRIGERATOR = "refrigerator"
    FREEZER = "freezer" 
    SAFE = "safe"

class StorageLocationAdd(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название места хранения")
    type: StorageType = Field(..., description="Тип места хранения")
    max_capacity: int = Field(..., gt=0, description="Максимальная вместимость")
    is_active: bool = Field(default=True, description="Активно ли место хранения")

class StorageLocation(StorageLocationAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)

class StorageLocationId(BaseModel):
    ok: bool = True
    storage_location_id: int
    
class StorageLocationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Название места хранения")
    type: Optional[StorageType] = Field(None, description="Тип места хранения")
    max_capacity: Optional[int] = Field(None, gt=0, description="Максимальная вместимость")
    is_active: Optional[bool] = Field(None, description="Активно ли место хранения")
    
    @field_validator('max_capacity')
    @classmethod
    def validate_max_capacity(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError('Capasity cannot be negative')
        return v

class BaseResponse(BaseModel):
    ok: bool = True
    message: str = ""

class ErrorResponse(BaseModel):
    ok: bool = False
    error: str
    details: Dict[str, Any] = {}

