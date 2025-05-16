# заполнение таблиц




from backend.app.models.task_status import TaskStatus
from backend.app.db.session import SessionLocal

def initialize_task_statuses():
    db = SessionLocal()
    statuses = [
        TaskStatus(id=1, name="Не сделано", color="red"),
        TaskStatus(id=2, name="В процессе", color="orange"),
        TaskStatus(id=3, name="Сделано", color="green"),
        TaskStatus(id=4, name="Просрочено", color="gray"),
    ]

    for status in statuses:
        exists = db.query(TaskStatus).filter_by(id=status.id).first()
        if not exists:
            db.add(status)

    db.commit()
    db.close()





