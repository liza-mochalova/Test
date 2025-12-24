from typing import Annotated
from fastapi import APIRouter, Query
from fastapi.params import Depends

from storage.repository import StorageLocationRepository
from storage.schemas import StorageLocationAdd, StorageLocation, StorageLocationId, StorageLocationUpdate

router = APIRouter(prefix="/storage", tags=["StorageLocation"])

# Storage Location endpoints
@router.post("/storage-locations", response_model=StorageLocationId)
async def add_storage_location(storage: Annotated[StorageLocationAdd, Depends()]) -> StorageLocationId:
    storage_id = await StorageLocationRepository.add_one(storage)
    return StorageLocationId(ok=True, storage_location_id=storage_id)

@router.get("/storage-locations", response_model=list[StorageLocation])
async def get_storage_locations(
    skip: int = Query(0, ge=0, description="Пропустить первых N записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимум записей")
) -> list[StorageLocation]:
    return await StorageLocationRepository.find_all(skip=skip, limit=limit)

@router.get("/storage-locations/active", response_model=list[StorageLocation])
async def get_active_storage_locations():
    return await StorageLocationRepository.get_active_locations()

@router.get("/storage-locations/{storage_id}", response_model=StorageLocation)
async def get_storage_location(storage_id: int) -> StorageLocation:
    return await StorageLocationRepository.find_by_id(storage_id)

@router.get("/storage-locations/search/{name}", response_model=StorageLocation)
async def get_storage_location_by_name(name: str) -> StorageLocation:
    return await StorageLocationRepository.find_by_name(name)

@router.put("/{storage_id}", response_model=StorageLocation)
async def update_storage(storage_id: int, storage_update: Annotated[StorageLocationUpdate, Depends()]) -> StorageLocation:
    return await StorageLocationRepository.update(storage_id, storage_update)

@router.delete("/{storage_id}")
async def delete_reagent(storage_id: int):
    await StorageLocationRepository.delete(storage_id)
    return {"ok": True, "message": "StorageLocation deleted"}