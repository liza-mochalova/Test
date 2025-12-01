from sqlalchemy import func, select
from database import StorageLocationOrm, StorageType, new_session
from database import ReagentsOrm
from exceptions import BusinessRuleException
from sqlalchemy.exc import SQLAlchemyError

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