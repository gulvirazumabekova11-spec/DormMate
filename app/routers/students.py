from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from app.database.db import get_session
from app.database.models import Student, StudentCreate, StudentRead, StudentUpdate, Application
router=APIRouter(prefix="/students",tags=["Студенттер"])
@router.post("",response_model=StudentRead,status_code=201)
def create(data:StudentCreate,session:Session=Depends(get_session)):
    if session.exec(select(Student).where(Student.student_number==data.student_number)).first(): raise HTTPException(409,"Бұл студент нөмірі тіркелген")
    obj=Student.model_validate(data); session.add(obj); session.commit(); session.refresh(obj); return obj
@router.get("",response_model=list[StudentRead])
def list_all(search:Optional[str]=Query(None),session:Session=Depends(get_session)):
    q=select(Student)
    if search: q=q.where(Student.full_name.contains(search))
    return session.exec(q.order_by(Student.full_name)).all()
@router.get("/{item_id}",response_model=StudentRead)
def get(item_id:int,session:Session=Depends(get_session)):
    obj=session.get(Student,item_id)
    if not obj: raise HTTPException(404,"Студент табылмады")
    return obj
@router.patch("/{item_id}",response_model=StudentRead)
def update(item_id:int,data:StudentUpdate,session:Session=Depends(get_session)):
    obj=session.get(Student,item_id)
    if not obj: raise HTTPException(404,"Студент табылмады")
    obj.sqlmodel_update(data.model_dump(exclude_unset=True)); session.add(obj); session.commit(); session.refresh(obj); return obj
@router.delete("/{item_id}",status_code=204)
def delete(item_id:int,session:Session=Depends(get_session)):
    obj=session.get(Student,item_id)
    if not obj: raise HTTPException(404,"Студент табылмады")
    if session.exec(select(Application).where(Application.student_id==item_id)).first(): raise HTTPException(409,"Өтініші бар студентті алдымен өтініштерден босатыңыз")
    session.delete(obj); session.commit()
