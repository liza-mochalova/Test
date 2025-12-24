from datetime import date
from sqlalchemy import func, select
from database import StorageLocationOrm, StorageType, new_session
from database import ReagentsOrm
from exceptions import BusinessRuleException, NotFoundException
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from reagents.schemas import ReagentAdd

class StorageService:
    @classmethod        
    async def get_recommended_storage(cls, hazard_class: int) -> int:
        """
        Автоматически подбирает место хранения по классу опасности
        с учетом свободной вместимости
        """
        async with new_session() as session:
            try:
                if hazard_class == 1:
                    allowed_types = [StorageType.SAFE]
                elif hazard_class in [2, 3]:
                    allowed_types = [StorageType.REFRIGERATOR, StorageType.FREEZER]
                else:
                    allowed_types = [StorageType.CABINET]

                query = (
                    select(StorageLocationOrm)
                    .where(
                        StorageLocationOrm.type.in_(allowed_types),
                        StorageLocationOrm.is_active == True
                    )
                    .order_by(StorageLocationOrm.id) 
                )
                
                result = await session.execute(query)
                storage_locations = result.scalars().all()
                
                if not storage_locations:
                    raise BusinessRuleException(
                        f"No suitable storage found for hazard class {hazard_class}",
                        error_code="NO_SUITABLE_STORAGE"
                    )
                
                for storage in storage_locations:
                    count_query = select(func.count(ReagentsOrm.id)).where(
                        ReagentsOrm.storage_location_id == storage.id
                    )
                    count_result = await session.execute(count_query)
                    current_count = count_result.scalar_one()
                    
                    if current_count < storage.max_capacity:
                        return storage.id
                
                raise BusinessRuleException(
                    "All suitable storage locations are at full capacity",
                    error_code="STORAGE_FULL"
                )
                
            except SQLAlchemyError as e:
                raise BusinessRuleException(
                    f"Database error while finding storage: {str(e)}",
                    error_code="STORAGE_SEARCH_ERROR"
                )
            
    @classmethod
    async def find_recommended_storage(
        cls, 
        session: AsyncSession,
        reag: ReagentAdd
        ) -> int:
        try:
            storage_location_id = reag.storage_location_id
            if storage_location_id is None:
                try:
                    storage_location_id = await StorageService.get_recommended_storage(reag.hazard_class)
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
            return storage_location_id
        except BusinessRuleException:
            raise

        except OperationalError as e:
            raise BusinessRuleException(
                "Database connection issue - please try again later",
                error_code="DATABASE_CONNECTION_ERROR"
            )
                
        except SQLAlchemyError as e:
            raise BusinessRuleException(
                "Database operation failed",
                error_code="DATABASE_ERROR"
            )
                
        except Exception as e:
            raise BusinessRuleException(
                f"Unexpected error while adding reagent: {str(e)}",
                error_code="UNEXPECTED_ERROR"
            )        
