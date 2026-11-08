from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.database.db import get_session
from app.database.models import Room, RoomCreate, RoomRead, RoomUpdate, Application, ApplicationStatus
router=APIRouter(prefix="/rooms",tags=["Бөлмелер"])
@router.post("",response_model=RoomRead,status_code=201)
def create(data:RoomCreate,session:Session=Depends(get_session)):
    obj=Room.model_validate(data); session.add(obj); session.commit(); session.refresh(obj); return obj
@router.get("",response_model=list[RoomRead])
def list_all(building:Optional[str]=Query(None),min_fee:Optional[float]=Query(None,ge=0),max_fee:Optional[float]=Query(None,ge=0),session:Session=Depends(get_session)):
    q=select(Room)
    if building: q=q.where(Room.building==building)
    if min_fee is not None: q=q.where(Room.monthly_fee>=min_fee)
    if max_fee is not None: q=q.where(Room.monthly_fee<=max_fee)
    rooms=session.exec(q.order_by(Room.building,Room.room_number)).all()
    result=[]
    for room in rooms:
        occupied=len(session.exec(select(Application).where(Application.room_id==room.id,Application.status==ApplicationStatus.approved)).all())
        result.append({**room.model_dump(),"occupied_places":occupied,"available_places":max(0,room.capacity-occupied)})
    return result
@router.get("/{item_id}",response_model=RoomRead)
def get(item_id:int,session:Session=Depends(get_session)):
    obj=session.get(Room,item_id)
    if not obj: raise HTTPException(404,"Бөлме табылмады")
    occupied=len(session.exec(select(Application).where(Application.room_id==obj.id,Application.status==ApplicationStatus.approved)).all())
    return {**obj.model_dump(),"occupied_places":occupied,"available_places":max(0,obj.capacity-occupied)}
@router.patch("/{item_id}",response_model=RoomRead)
def update(item_id:int,data:RoomUpdate,session:Session=Depends(get_session)):
    obj=session.get(Room,item_id)
    if not obj: raise HTTPException(404,"Бөлме табылмады")
    changes=data.model_dump(exclude_unset=True)
    occupied=len(session.exec(select(Application).where(Application.room_id==obj.id,Application.status==ApplicationStatus.approved)).all())
    if "capacity" in changes and changes["capacity"] < occupied: raise HTTPException(409,"Сыйымдылық бекітілген орын санынан аз болмауы керек")
    obj.sqlmodel_update(changes); session.add(obj); session.commit(); session.refresh(obj); return obj
@router.delete("/{item_id}",status_code=204)
def delete(item_id:int,session:Session=Depends(get_session)):
    obj=session.get(Room,item_id)
    if not obj: raise HTTPException(404,"Бөлме табылмады")
    if session.exec(select(Application).where(Application.room_id==item_id)).first(): raise HTTPException(409,"Өтініші бар бөлмені жоюға болмайды")
    session.delete(obj); session.commit()
