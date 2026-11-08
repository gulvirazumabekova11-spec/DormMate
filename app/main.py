from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.db import init_db
from app.routers import students, rooms, applications
@asynccontextmanager
async def lifespan(app:FastAPI):
    init_db(); yield
app=FastAPI(title="DormMate API",description="Жатақханадағы бос орындар мен өтініштерді басқару жүйесі",version="1.0.0",lifespan=lifespan)
app.include_router(students.router); app.include_router(rooms.router); app.include_router(applications.router)
@app.get("/",tags=["Жүйе"])
def home(): return {"system":"DormMate","status":"жұмыс істеп тұр","docs":"/docs"}
