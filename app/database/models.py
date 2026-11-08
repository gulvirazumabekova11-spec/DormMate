from datetime import date
from enum import Enum
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel

class ApplicationStatus(str, Enum):
    pending = "Қаралуда"
    approved = "Қабылданды"
    rejected = "Қабылданбады"

class StudentBase(SQLModel):
    full_name: str = Field(min_length=3, max_length=120, index=True)
    student_number: str = Field(min_length=4, max_length=20, unique=True, index=True)
    faculty: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=6, max_length=20)

class Student(StudentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    applications: list["Application"] = Relationship(back_populates="student")

class StudentCreate(StudentBase): pass
class StudentRead(StudentBase):
    id: int
class StudentUpdate(SQLModel):
    full_name: Optional[str] = Field(default=None, min_length=3, max_length=120)
    faculty: Optional[str] = Field(default=None, min_length=2, max_length=100)
    phone: Optional[str] = Field(default=None, min_length=6, max_length=20)

class RoomBase(SQLModel):
    building: str = Field(min_length=1, max_length=50, index=True)
    room_number: str = Field(min_length=1, max_length=12, index=True)
    capacity: int = Field(ge=1, le=12)
    monthly_fee: float = Field(ge=0)

class Room(RoomBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    applications: list["Application"] = Relationship(back_populates="room")
class RoomCreate(RoomBase): pass
class RoomRead(RoomBase):
    id: int
    occupied_places: int = 0
    available_places: int = 0
class RoomUpdate(SQLModel):
    building: Optional[str] = Field(default=None, min_length=1, max_length=50)
    room_number: Optional[str] = Field(default=None, min_length=1, max_length=12)
    capacity: Optional[int] = Field(default=None, ge=1, le=12)
    monthly_fee: Optional[float] = Field(default=None, ge=0)

class ApplicationBase(SQLModel):
    student_id: int = Field(foreign_key="student.id", index=True)
    room_id: int = Field(foreign_key="room.id", index=True)
    submitted_at: date = Field(default_factory=date.today)
    status: ApplicationStatus = ApplicationStatus.pending
    comment: Optional[str] = Field(default=None, max_length=500)
class Application(ApplicationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student: Optional[Student] = Relationship(back_populates="applications")
    room: Optional[Room] = Relationship(back_populates="applications")
class ApplicationCreate(ApplicationBase): pass
class ApplicationRead(ApplicationBase):
    id: int
class ApplicationUpdate(SQLModel):
    room_id: Optional[int] = Field(default=None, gt=0)
    status: Optional[ApplicationStatus] = None
    comment: Optional[str] = Field(default=None, max_length=500)
