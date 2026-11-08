from sqlmodel import Session, select
from app.database.db import engine, init_db
from app.database.models import Student, Room, Application, ApplicationStatus

def seed():
    init_db()
    with Session(engine) as s:
        if s.exec(select(Student)).first():
            print("Бастапқы демо деректер бұрыннан бар")
            return
        students = [
            Student(full_name="Айдана Нұрланқызы", student_number="ST-2026-001", faculty="Ақпараттық жүйелер", phone="+7 (7XX) XXX-XX-01"),
            Student(full_name="Әлихан Серікұлы", student_number="ST-2026-002", faculty="Экономика және бизнес", phone="+7 (7XX) XXX-XX-02"),
            Student(full_name="Мадина Ермекқызы", student_number="ST-2026-003", faculty="Дизайн және технология", phone="+7 (7XX) XXX-XX-03"),
        ]
        rooms = [
            Room(building="А корпусы", room_number="101", capacity=3, monthly_fee=12000),
            Room(building="А корпусы", room_number="204", capacity=2, monthly_fee=15000),
            Room(building="Ә корпусы", room_number="12", capacity=4, monthly_fee=10000),
        ]
        s.add_all(students + rooms)
        s.commit()
        for item in students + rooms:
            s.refresh(item)
        s.add_all([
            Application(student_id=students[0].id, room_id=rooms[0].id, status=ApplicationStatus.pending, comment="Бірінші курс студенті"),
            Application(student_id=students[1].id, room_id=rooms[1].id, status=ApplicationStatus.approved),
        ])
        s.commit()
        print("DormMate демо деректері дайын")

if __name__ == "__main__":
    seed()
