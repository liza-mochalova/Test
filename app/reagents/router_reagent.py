from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from reagents.repository import ReagentRepository, get_session
from reagents.schemas import ReagentAdd, Reagent, ReagentId, ReagentUpdate
from reagents.storage_service import StorageService

router = APIRouter(prefix="/reagents", tags=["Reagents"])

# Reagent endpoints
@router.post("", response_model=ReagentId)
async def add_reagent(
    reagent: Annotated[ReagentAdd, Depends()],
    session: AsyncSession = Depends(get_session)) -> ReagentId:
    storage_location_id = await StorageService.find_recommended_storage(
        session, reagent
    )
    reagent_id = await ReagentRepository.add_one(session, reagent, storage_location_id)
    return ReagentId(ok=True, reagent_id=reagent_id)

@router.get("", response_model=list[Reagent])
async def get_reagents(
    skip: int = Query(0, ge=0, description="Пропустить первых N записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимум записей"),
    session: AsyncSession = Depends(get_session)
) -> list[Reagent]:
    return await ReagentRepository.find_all(session=session, skip=skip, limit=limit)

@router.get("/{reagent_id}", response_model=Reagent)
async def get_reagent(reagent_id: int) -> Reagent:
    return await ReagentRepository.find_by_id(reagent_id)

@router.put("/{reagent_id}", response_model=Reagent)
async def update_reagent(reagent_id: int, reagent_update: Annotated[ReagentUpdate, Depends()]) -> Reagent:
    return await ReagentRepository.update(reagent_id, reagent_update)

@router.delete("/{reagent_id}")
async def delete_reagent(reagent_id: int):
    await ReagentRepository.delete(reagent_id)
    return {"ok": True, "message": "Reagent deleted"}

@router.get("/filter/search", response_model=list[Reagent])
async def filter_reagents(
    name: Optional[str] = Query(None, min_length=1, max_length=100, description="Фильтр по названию"),
    formula: Optional[str] = Query(None, description="Фильтр по химической формуле"),
    hazard_class: Optional[int] = Query(None, ge=1, le=4, description="Фильтр по классу опасности"),
    storage_location_id: Optional[int] = Query(None, description="Фильтр по месту хранения"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> list[Reagent]:
    return await ReagentRepository.filter_reagents(
        name=name,
        formula=formula,
        hazard_class=hazard_class,
        storage_location_id=storage_location_id,
        skip=skip,
        limit=limit,
    )

@router.get("/expiring/soon", response_model=list[Reagent])
async def get_expiring_reagents(days: int = Query(30, ge=1, le=365, description="Дней до истечения срока")) -> list[Reagent]:
    return await ReagentRepository.get_expiring_soon(days=days)

@router.post("/{reagent_id}/write-off")
async def write_off_reagent(
    reagent_id: int, 
    quantity: float = Query(..., gt=0, description="Количество для списания")
):
    reagent = await ReagentRepository.write_off(reagent_id, quantity)
    return {"ok": True, "message": f"Written off {quantity}, remaining: {reagent.quantity}"}

