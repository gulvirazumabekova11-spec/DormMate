from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.database.db import get_session
from app.database.models import Application, ApplicationCreate, ApplicationRead, ApplicationUpdate, Room, Student, ApplicationStatus
router=APIRouter(prefix="/applications",tags=["Өтініштер"])
def ensure_refs(data,session):
    if not session.get(Student,data.student_id): raise HTTPException(404,"Студент табылмады")
    if not session.get(Room,data.room_id): raise HTTPException(404,"Бөлме табылмады")
@router.post("",response_model=ApplicationRead,status_code=201)
def create(data:ApplicationCreate,session:Session=Depends(get_session)):
    ensure_refs(data,session)
    if data.status==ApplicationStatus.approved:
        occupied=len(session.exec(select(Application).where(Application.room_id==data.room_id,Application.status==ApplicationStatus.approved)).all())
        if occupied>=session.get(Room,data.room_id).capacity: raise HTTPException(409,"Бұл бөлмеде бос орын жоқ")
    duplicate=session.exec(select(Application).where(Application.student_id==data.student_id,Application.status!=ApplicationStatus.rejected)).first()
    if duplicate: raise HTTPException(409,"Студенттің белсенді өтініші бар")
    obj=Application.model_validate(data); session.add(obj); session.commit(); session.refresh(obj); return obj
@router.get("",response_model=list[ApplicationRead])
def list_all(status_filter:Optional[ApplicationStatus]=Query(None,alias="status"),student_id:Optional[int]=Query(None,gt=0),session:Session=Depends(get_session)):
    q=select(Application)
    if status_filter: q=q.where(Application.status==status_filter)
    if student_id is not None: q=q.where(Application.student_id==student_id)
    return session.exec(q.order_by(Application.submitted_at.desc())).all()
@router.get("/{item_id}",response_model=ApplicationRead)
def get(item_id:int,session:Session=Depends(get_session)):
    obj=session.get(Application,item_id)
    if not obj: raise HTTPException(404,"Өтініш табылмады")
    return obj
@router.patch("/{item_id}",response_model=ApplicationRead)
def update(item_id:int,data:ApplicationUpdate,session:Session=Depends(get_session)):
    obj=session.get(Application,item_id)
    if not obj: raise HTTPException(404,"Өтініш табылмады")
    changes=data.model_dump(exclude_unset=True)
    target_room_id=changes.get("room_id",obj.room_id)
    target_room=session.get(Room,target_room_id)
    if not target_room: raise HTTPException(404,"Бөлме табылмады")
    target_status=changes.get("status",obj.status)
    if target_status==ApplicationStatus.approved and (obj.status!=ApplicationStatus.approved or target_room_id!=obj.room_id):
        occupied=len(session.exec(select(Application).where(Application.room_id==target_room_id,Application.status==ApplicationStatus.approved)).all())
        if occupied>=target_room.capacity: raise HTTPException(409,"Бұл бөлмеде бос орын жоқ")
    obj.sqlmodel_update(changes); session.add(obj); session.commit(); session.refresh(obj); return obj
@router.delete("/{item_id}",status_code=204)
def delete(item_id:int,session:Session=Depends(get_session)):
    obj=session.get(Application,item_id)
    if not obj: raise HTTPException(404,"Өтініш табылмады")
    session.delete(obj); session.commit()
