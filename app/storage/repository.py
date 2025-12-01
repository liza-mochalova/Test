from sqlalchemy import select
from exceptions import BusinessRuleException, NotFoundException
from storage.schemas import StorageLocation, StorageLocationAdd, StorageLocationUpdate
from database import StorageLocationOrm, new_session

class StorageLocationRepository:
    @classmethod
    async def add_one(cls, storage: StorageLocationAdd) -> int:
        async with new_session() as session:
            storage_dict = storage.model_dump()
            storage_orm = StorageLocationOrm(**storage_dict)
            session.add(storage_orm)
            await session.flush()
            await session.commit()
            return storage_orm.id
    
    @classmethod
    async def find_all(cls) -> list[StorageLocation]:
        async with new_session() as session:
            query = select(StorageLocationOrm)
            result = await session.execute(query)
            storage_models = result.scalars().all()
            storage_schemas = [StorageLocation.model_validate(model) for model in storage_models]
            return storage_schemas
    
    @classmethod
    async def find_by_id(cls, storage_id: int) -> StorageLocation:
        async with new_session() as session:
            query = select(StorageLocationOrm).where(StorageLocationOrm.id == storage_id)
            result = await session.execute(query)
            storage_model = result.scalar_one_or_none()
            if storage_model:
                return StorageLocation.model_validate(storage_model)
            raise NotFoundException("Storage location", storage_id)
    
    @classmethod
    async def get_active_locations(cls) -> list[StorageLocation]:
        async with new_session() as session:
            query = select(StorageLocationOrm).where(StorageLocationOrm.is_active == True)
            result = await session.execute(query)
            storage_models = result.scalars().all()
            return [StorageLocation.model_validate(model) for model in storage_models]
        
    @classmethod
    async def find_by_name(cls, name: str) -> StorageLocation:
        async with new_session() as session:
            query = select(StorageLocationOrm).where(StorageLocationOrm.name == name)
            result = await session.execute(query)
            storage_model = result.scalar_one_or_none()
            if storage_model:
                return StorageLocation.model_validate(storage_model)
            raise NotFoundException("Storage location")
    
    @classmethod
    async def update(cls, storage_id: int, storage_update: StorageLocationUpdate) -> StorageLocation:
        async with new_session() as session:
            query = select(StorageLocationOrm).where(StorageLocationOrm.id == storage_id)
            result = await session.execute(query)
            storage_model = result.scalar_one_or_none()
        
            if not storage_model:
                raise NotFoundException("Storage location", storage_id)

            update_data = storage_update.model_dump(exclude_unset=True)
        
            for field, value in update_data.items():
                if value is not None:
                    setattr(storage_model, field, value)
        
            await session.commit()
            await session.refresh(storage_model)
            return StorageLocation.model_validate(storage_model)
    
    @classmethod
    async def delete(cls, storage_location_id: int) -> bool:
        async with new_session() as session:
            query = select(StorageLocationOrm).where(StorageLocationOrm.id == storage_location_id)
            result = await session.execute(query)
            storage_model = result.scalar_one_or_none()
            
            if not storage_model:
                raise NotFoundException("Storage", storage_location_id)
        
            if storage_model.is_active:

                raise BusinessRuleException(
                    f"Cannot delite active storage location '{storage_model.name}' (ID: {storage_location_id})",
                    error_code="INACTIVE_STORAGE"
                    )

            await session.delete(storage_model)
            await session.commit()
            
            return True