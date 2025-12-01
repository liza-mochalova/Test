from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator, Field
import re
from datetime import date
from enum import Enum

class UnitType(str, Enum):
    ML = "ml"
    L = "l"
    G = "g"
    KG = "kg"

class ReagentAdd(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="Название реактива")
    formula: str = Field(..., min_length=1, max_length=50, description="Химическая формула")
    cas_number: str = Field(..., description="CAS-номер в формате XXXXX-XX-X")
    quantity: float = Field(..., gt=0, description="Количество")
    unit: UnitType = Field(..., description="Единица измерения")
    hazard_class: int = Field(..., ge=1, le=4, description="Класс опасности (1-4)")
    expiry_date: date = Field(..., description="Срок годности")
    storage_location_id: Optional[int] = Field(None, description="ID места хранения")
    
    @field_validator('cas_number')
    @classmethod
    def validate_cas_number(cls, v):
        pattern = r'^\d{4,5}-\d{2}-\d$'
        if not re.match(pattern, v):
            raise ValueError('CAS number must be in format: XXXXX-XX-X')
        return v

    @field_validator('expiry_date')
    @classmethod
    def validate_expiry_date(cls, v):
        if v < date.today():
            raise ValueError('Expiry date cannot be in the past')
        return v
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError('Quantity cannot be negative')
        return v
    
class Reagent(ReagentAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)

class ReagentId(BaseModel):
    ok: bool = True
    reagent_id: int

class ReagentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Название реактива")
    formula: Optional[str] = Field(None, min_length=1, max_length=50, description="Химическая формула")
    cas_number: Optional[str] = Field(None, description="CAS-номер в формате XXXXX-XX-X")
    quantity: Optional[float] = Field(None, ge=0, description="Количество")
    unit: Optional[UnitType] = Field(None, description="Единица измерения")
    hazard_class: Optional[int] = Field(None, ge=1, le=4, description="Класс опасности (1-4)")
    expiry_date: Optional[date] = Field(None, description="Срок годности")
    storage_location_id: Optional[int] = Field(None, gt=0, description="ID места хранения")

    @field_validator('cas_number')
    @classmethod
    def validate_cas_number(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            pattern = r'^\d{4,5}-\d{2}-\d$'
            if not re.match(pattern, v):
                raise ValueError('CAS number must be in format: XXXXXXX-XX-X')
        return v

    @field_validator('expiry_date')
    @classmethod
    def validate_expiry_date(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v < date.today():
            raise ValueError('Expiry date cannot be in the past')
        return v

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError('Quantity cannot be negative')
        return v
