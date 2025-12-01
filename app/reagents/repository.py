from datetime import date, timedelta
from aiosqlite import IntegrityError, OperationalError
from sqlalchemy import and_, func, select
from database import StorageType
from reagents.storage_service import StorageService
from exceptions import BusinessRuleException, NotFoundException
from reagents.schemas import Reagent, ReagentAdd, ReagentUpdate
from database import ReagentsOrm, new_session
from database import  StorageLocationOrm
from sqlalchemy.exc import SQLAlchemyError

class ReagentRepository:
    @classmethod
    async def add_one(cls, reag: ReagentAdd) -> int:
        """
        Добавляет новый реактив в систему
        Автоматически подбирает место хранения если не указано явно
        """
        async with new_session() as session:
            try:
                storage_location_id = reag.storage_location_id
                if storage_location_id is None:
                    try:
                        storage_location_id = await StorageService.get_recommended_storage(reag.hazard_class)
                        print(f"Автоматически подобрано хранилище {storage_location_id} для класса опасности {reag.hazard_class}")
                    except BusinessRuleException as e:
                        raise BusinessRuleException(
                            f"Cannot add reagent: {e.detail}",
                            error_code=e.error_code
                        )

                storage = await session.get(StorageLocationOrm, storage_location_id)
                if not storage:
                    raise NotFoundException("Storage location", storage_location_id)
                
                if not storage.is_active:
                    raise BusinessRuleException(
                        f"Cannot add reagent to inactive storage location '{storage.name}' (ID: {storage_location_id})",
                        error_code="INACTIVE_STORAGE"
                    )

                if reag.hazard_class == 1 and storage.type != StorageType.SAFE:
                    raise BusinessRuleException(
                        f"Hazard class 1 reagents must be stored in safe, not {storage.type.value}",
                        error_code="INVALID_STORAGE_FOR_HAZARD_CLASS"
                    )

                current_count_query = select(func.count(ReagentsOrm.id)).where(
                    ReagentsOrm.storage_location_id == storage_location_id
                )
                current_count_result = await session.execute(current_count_query)
                current_count = current_count_result.scalar_one()

                if current_count >= storage.max_capacity:
                    raise BusinessRuleException(
                        f"Storage location '{storage.name}' capacity exceeded: {current_count}/{storage.max_capacity}",
                        error_code="STORAGE_CAPACITY_EXCEEDED"
                    )

                existing_cas_query = select(ReagentsOrm).where(
                    ReagentsOrm.cas_number == reag.cas_number
                )
                existing_cas_result = await session.execute(existing_cas_query)
                existing_reagent = existing_cas_result.scalar_one_or_none()
                
                if existing_reagent:
                    raise BusinessRuleException(
                        f"Reagent with CAS number '{reag.cas_number}' already exists (ID: {existing_reagent.id})",
                        error_code="DUPLICATE_CAS"
                    )

                if reag.expiry_date < date.today():
                    raise BusinessRuleException(
                        f"Cannot add reagent with expired date: {reag.expiry_date}",
                        error_code="EXPIRED_REAGENT"
                    )

                reag_dict = reag.model_dump()
                reag_dict['storage_location_id'] = storage_location_id
                
                reag_orm = ReagentsOrm(**reag_dict)
                session.add(reag_orm)

                await session.flush()
                reagent_id = reag_orm.id
                
                await session.commit()
                
                print(f"Реактив '{reag.name}' успешно добавлен с ID: {reagent_id} в хранилище: {storage.name} (ID: {storage_location_id})")
                return reagent_id

            except BusinessRuleException:
                await session.rollback()
                raise
                
            except IntegrityError as e:
                await session.rollback()
                if "UNIQUE constraint failed: reagents.cas_number" in str(e):
                    raise BusinessRuleException(
                        f"Reagent with CAS number '{reag.cas_number}' already exists",
                        error_code="DUPLICATE_CAS"
                    )
                raise BusinessRuleException(
                    "Database integrity error - possible data corruption",
                    error_code="DATA_INTEGRITY_ERROR"
                )
                
            except OperationalError as e:
                await session.rollback()
                raise BusinessRuleException(
                    "Database connection issue - please try again later",
                    error_code="DATABASE_CONNECTION_ERROR"
                )
                
            except SQLAlchemyError as e:
                await session.rollback()
                raise BusinessRuleException(
                    "Database operation failed",
                    error_code="DATABASE_ERROR"
                )
                
            except Exception as e:
                await session.rollback()
                raise BusinessRuleException(
                    f"Unexpected error while adding reagent: {str(e)}",
                    error_code="UNEXPECTED_ERROR"
                )
        
    @classmethod
    async def find_all(cls, skip: int = 0, limit: int = 100) -> list[Reagent]:
        async with new_session() as session:
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

