from datetime import date, timedelta
from aiosqlite import IntegrityError, OperationalError
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, func, select
from database import StorageType
from reagents.storage_service import StorageService
from exceptions import BusinessRuleException, NotFoundException
from reagents.schemas import Reagent, ReagentAdd, ReagentUpdate
from database import ReagentsOrm, new_session
from database import  StorageLocationOrm
from sqlalchemy.exc import SQLAlchemyError

async def get_session():
    async with new_session() as session:
        yield session

class ReagentRepository:
    @classmethod
    async def add_one(
        cls, 
        session: AsyncSession,
        reag: ReagentAdd,
        storage_location_id: int) -> int:
                reag_dict = reag.model_dump()
                reag_dict['storage_location_id'] = storage_location_id

                reag_orm = ReagentsOrm(**reag_dict)
                session.add(reag_orm)

                await session.flush()
                reagent_id = reag_orm.id
                
                await session.commit()

                return reagent_id

    @classmethod
    async def find_all(
        cls, 
        session: AsyncSession,
        skip: int = 0, 
        limit: int = 100,
        ) -> list[Reagent]:
            query = select(ReagentsOrm).offset(skip).limit(limit)
            result = await session.execute(query)
            reag_models = result.scalars().all()
            reag_schemas = [Reagent.model_validate(reag_model) for reag_model in reag_models]
            return reag_schemas
    
    @classmethod
    async def find_by_id(cls, reagent_id: int) -> Reagent:
        async with new_session() as session:
            query = select(ReagentsOrm).where(ReagentsOrm.id == reagent_id)
            result = await session.execute(query)
            reagent_model = result.scalar_one_or_none()
            if reagent_model:
                return Reagent.model_validate(reagent_model)
            raise NotFoundException("Reagent", reagent_id)
        
    @classmethod
    async def update(cls, reagent_id: int, reagent_update: ReagentUpdate) -> Reagent:
        async with new_session() as session:
            query = select(ReagentsOrm).where(ReagentsOrm.id == reagent_id)
            result = await session.execute(query)
            reagent_model = result.scalar_one_or_none()
            
            if not reagent_model:
                raise NotFoundException("Reagent", reagent_id)

            update_data = reagent_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None:
                    setattr(reagent_model, field, value)
            await session.commit()
            await session.refresh(reagent_model)
            return Reagent.model_validate(reagent_model)
        
    @classmethod
    async def delete(cls, reagent_id: int) -> bool:
        async with new_session() as session:
            query = select(ReagentsOrm).where(ReagentsOrm.id == reagent_id)
            result = await session.execute(query)
            reagent_model = result.scalar_one_or_none()
            
            if not reagent_model:
                raise NotFoundException("Reagent", reagent_id)
            
            await session.delete(reagent_model)
            await session.commit()
            
            return True
    
    @classmethod
    async def get_expiring_soon(cls, days: int = 30) -> list[Reagent]:
        async with new_session() as session:
            target_date = date.today() + timedelta(days=days)
            query = select(ReagentsOrm).where(
                and_(
                    ReagentsOrm.expiry_date <= target_date,
                    ReagentsOrm.expiry_date >= date.today()
                )
            )
            result = await session.execute(query)
            reagent_models = result.scalars().all()
            return [Reagent.model_validate(model) for model in reagent_models]
    
    @classmethod
    async def filter_reagents(
        cls, 
        name: str = None, 
        formula: str = None, 
        hazard_class: int = None,
        storage_location_id: int = None,
        skip: int = 0, 
        limit: int = 100
    ) -> list[Reagent]:
        async with new_session() as session:
            query = select(ReagentsOrm)
            
            if name:
                query = query.where(ReagentsOrm.name.contains(name))
            if formula:
                query = query.where(ReagentsOrm.formula.contains(formula))
            if hazard_class:
                query = query.where(ReagentsOrm.hazard_class == hazard_class)
            if storage_location_id:
                query = query.where(ReagentsOrm.storage_location_id == storage_location_id)
            
            query = query.offset(skip).limit(limit)
            result = await session.execute(query)
            reagent_models = result.scalars().all()
            return [Reagent.model_validate(model) for model in reagent_models]
    
    @classmethod
    async def write_off(cls, reagent_id: int, quantity: float) -> Reagent:
        async with new_session() as session:
            async with session.begin():
                query = select(ReagentsOrm).where(ReagentsOrm.id == reagent_id)
                result = await session.execute(query)
                reagent_model = result.scalar_one_or_none()
            
                if not reagent_model:
                    raise NotFoundException("Reagent", reagent_id)
            
                if quantity > reagent_model.quantity:
                    raise BusinessRuleException(
                        f"Cannot write off {quantity}, only {reagent_model.quantity} available",
                        error_code="INSUFFICIENT_QUANTITY"
                    )
            
                reagent_model.quantity -= quantity  
                await session.flush()                                                                                                                                                                                                                                                                                                                                                                                                                         
                await session.refresh(reagent_model)
            return Reagent.model_validate(reagent_model)

