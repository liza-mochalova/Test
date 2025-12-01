from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Enum as SQLEnum
import enum

class UnitType(str, enum.Enum):
    ML = "ml"
    L = "l" 
    G = "g"
    KG = "kg"

class StorageType(str, enum.Enum):
    CABINET = "cabinet"
    REFRIGERATOR = "refrigerator" 
    FREEZER = "freezer"
    SAFE = "safe"

engine = create_async_engine(
    "sqlite+aiosqlite:///reagents.db"
)

new_session = async_sessionmaker(engine, expire_on_commit=False)

class Model(DeclarativeBase):
    pass
class Model(DeclarativeBase):
    pass

class StorageLocationOrm(Model):
    __tablename__ = "storage_locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[StorageType] = mapped_column(SQLEnum(StorageType), nullable=False) 
    max_capacity: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    reagents: Mapped[list["ReagentsOrm"]] = relationship(
        back_populates="storage_location",
        lazy="select"
    )

class ReagentsOrm(Model):
    __tablename__ = "reagents"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    formula: Mapped[str] = mapped_column(String(50))
    cas_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    quantity: Mapped[float] = mapped_column(nullable=False)
    unit: Mapped[UnitType] = mapped_column(SQLEnum(UnitType), nullable=False)
    hazard_class: Mapped[int] = mapped_column(nullable=False)
    expiry_date: Mapped[date] = mapped_column(nullable=False)

    storage_location_id: Mapped[int] = mapped_column(
        ForeignKey("storage_locations.id"), 
        nullable=False
    )
    storage_location: Mapped["StorageLocationOrm"] = relationship(back_populates="reagents")

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)